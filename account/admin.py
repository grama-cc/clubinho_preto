from box.models import Shipping
from django.contrib import admin
from django.contrib.admin import register
from django.db.models import Count, F
from django.utils.html import mark_safe  # Newer versions
from finance.models import Subscription
from .models import Sender, Subscriber, Warning


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    fields = 'date', 'value', 'asaas_id', 'billingType', 'cycle', 'description', 'status', 'deleted', 'payments',
    readonly_fields = 'date', 'value', 'asaas_id', 'billingType', 'cycle', 'description', 'status', 'deleted', 'payments'
    show_change_link = True

    def payments(self, obj):
        fields = (['id', 'id'], ['value', 'valor'], ['due_date', 'vencimento'],
                  ['invoice_id', 'id da cobrança'], ['billingType', 'tipo de pagamento'], ['status', 'status'])
        payments = ''
        for p in obj.paymenthistory_set.values():
            payments += '<p>'
            for field in fields:
                payments += '<strong>{}</strong>: {}<br>'.format(field[1], p[field[0]])
            payments += '</p>'
            payments += '<br>'

        return mark_safe(payments)
    payments.short_description = 'Histórico de Pagamentos'


class ShippingInline(admin.StackedInline):
    model = Shipping
    extra = 0
    fields = 'date_created', 'box', 'shipping_option_selected',
    readonly_fields = 'date_created', 'box', 'shipping_option_selected'
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email', 'relatedness_raw', 'kids_race_raw',)
    list_display = ('id', 'name', 'email', 'city', 'province', '_can_send_package', 'subscription_status',
                    'shipping_count', 'relatedness', 'kids_race', 'asaas_customer_id')
    ordering = ('name',)
    actions = 'importar_planilha', 'import_subscribers',
    inlines = SubscriptionInline, ShippingInline,
    # todo: filter by "can_send_package"

    fieldsets = (
        ("Informações Gerais",
         {"fields": ("name", "email", "phone", "cpf")}),
        ("Endereço",
         {"fields": ("address", "addressNumber", "province", "cep", "city", "state_initials", "complement", "delivery", "note")}),
        ("Assinatura Clubinho",
         {"fields": ("relatedness", "relatedness_raw", "kids_name", "kids_age", "kids_gender", "kids_race", "kids_gender_raw", "kids_race_raw", "subscribing_date", "more_info", "asaas_customer_id")}),
    )


    def get_queryset(self, request):
        return super().get_queryset(request)\
            .select_related('subscription')\
            .annotate(
                shipping_count=Count('shippings'),
                subscription_status=F('subscription__status'),
                payments=Count('subscription__paymenthistory'),
        )

    def subscription_status(self, obj):
        return obj.subscription_status
    subscription_status.short_description = 'Status'

    def shipping_count(self, obj):
        return f"{obj.payments}/{obj.shipping_count}"
    shipping_count.short_description = 'Pagamentos/Envios'

    def _can_send_package(self, obj):
        return obj.can_send_package()
    _can_send_package.boolean = True
    _can_send_package.short_description = 'Campos ok?'

    def importar_planilha(modeladmin, request, queryset):
        from celery_app.celery import task_import_spreadsheet
        task_import_spreadsheet.delay()
        modeladmin.message_user(request, 'A planilha será importada. Isso pode demorar de 2 a 5 minutos.')

    def import_subscribers(modeladmin, request, queryset):
        from account.service import AccountService
        created, errors, skipped = AccountService.import_asaas_customers()

        modeladmin.message_user(request, f'{created} assinantes criadas, {errors} erros, {skipped} já existiam')
    import_subscribers.short_description = 'Importar assinantes Asaas'


@register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = "name", "phone", "email", "address", "jadlog_agency_id",
    readonly_fields = "jadlog_agency_options", "agency_options"
    fieldsets = (
        ("Informações Gerais",
         {"fields": ("name", "phone", "email", )}),

        ("Documentos",
         {"fields": ("document", "company_document", "state_register")}),

        ("Endereço",
         {"fields": ("address", "complement", "number", "district", "city", "country_id", "postal_code", )}),

        (None,
         {"fields": ("note",)}),

        ("JadLog",
         {"fields": ("jadlog_agency_id", "agency_options",)}),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def agency_options(self, obj):
        try:
            response = ''
            if obj.jadlog_agency_options:
                for agency in obj.jadlog_agency_options:
                    for field in agency.keys():
                        response += f'{field}: {agency[field]}<br>'
                    response += '<br>'

            return mark_safe(response)
        except Exception as e:
            return obj.jadlog_agency_options


@register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = "id", "created_at", "text", "solution",  # "description", "data",
    ordering = "-created_at",
    readonly_fields = list_display

    def has_add_permission(self, request, obj=None):
        return False
