from box.models import Shipping
from django.contrib import admin
from django.contrib.admin import register
from django.db.models import Count
from django.forms import ModelForm
from django.db.models.expressions import OuterRef, Subquery
from django.utils.html import mark_safe  # Newer versions
from finance.models import (PaymentHistory, Subscription, SUBSCRIPTION_DICT)

from .models import Sender, Subscriber, Warning

# Text to put at the end of each page's <title>.
admin.site.site_title = "Clubinho Preto"

# Text to put in each page's <h1> (and above login form).
admin.site.site_header = "Clubinho Preto Admin"

admin.site.site_url = '/authorize_application'

# region Forms
class SenderModelForm(ModelForm):

    class Meta:
        model = Sender
        fields = '__all__'

        help_texts = {
            'update_jadlog_options': 'Deixe marcada esta opção para atualizar as opções de agências jadlog. <br>\
                Uma vez que forem atualizadas, ela será automaticamente desmarcada.',
        }

# endregion

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
    list_display = ('id', 'name', 'email', 'city', 'province', 'relatedness', 'kids_age', 'kids_race',
                    'last_payment_status', 'missing_field', 'shipping_count')
    ordering = ('name',)
    actions = 'update_asaas_info',  # 'importar_planilha', 'import_subscribers',
    inlines = SubscriptionInline, ShippingInline,
    list_filter = 'kids_race', 'kids_age',

    fieldsets = (
        ("Informações Gerais",
         {"fields": ("name", "email", "phone", "cpf")}),
        ("Endereço",
         {"fields": ("address", "addressNumber", "province", "cep", "city", "state_initials", "complement", "delivery", "note")}),
        ("Informações do Clubinho",
         {"fields": ("relatedness", "relatedness_raw", "kids_name", "kids_age", "kids_gender", "kids_race", "kids_gender_raw", "kids_race_raw", "subscribing_date", "more_info", "asaas_customer_id")}),
    )

    def get_queryset(self, request):
        last_payment = Subquery(PaymentHistory.objects.filter(
            subscription__subscriber_id=OuterRef("id"),
        ).order_by("-due_date").values('status')[:1])

        return super().get_queryset(request)\
            .select_related('subscription')\
            .annotate(
                shipping_count=Count('shippings'),
                last_payment_status=last_payment,
                payments=Count('subscription__paymenthistory'),
        )

    def last_payment_status(self, obj):
        status = obj.last_payment_status
        return SUBSCRIPTION_DICT.get(status, status)

    last_payment_status.short_description = 'Status'

    def shipping_count(self, obj):
        return f"{obj.payments}/{obj.shipping_count}"
    shipping_count.short_description = 'Pagamentos/Envios'

    # def _can_send_package(self, obj):
    #     return obj.can_send_package(get_field=True) == True
    # _can_send_package.boolean = True
    # _can_send_package.short_description = 'Campos ok?'

    def missing_field(self, obj):
        can_send = obj.can_send_package(get_field=True)
        if can_send is True:
            return None
        return can_send
    missing_field.short_description = 'Campo faltando'

    def importar_planilha(modeladmin, request, queryset):
        from celery_app.celery import task_import_spreadsheet
        task_import_spreadsheet.delay()
        modeladmin.message_user(request, 'A planilha será importada. Isso pode demorar de 2 a 5 minutos.')

    def import_subscribers(modeladmin, request, queryset):
        from account.service import AccountService
        created, errors, skipped = AccountService.import_asaas_customers()

        modeladmin.message_user(request, f'{created} assinantes criadas, {errors} erros, {skipped} já existiam')
    import_subscribers.short_description = 'Importar assinantes Asaas'

    def update_asaas_info(modeladmin, request, queryset):
        from celery import chain
        from celery_app.celery import (task_import_asaas_customers,
                                       task_import_subscriptions,
                                       task_update_payment_history,
                                       task_update_subscriptions)
        res = chain(
            task_import_asaas_customers.s(),
            task_import_subscriptions.s(),
            task_update_subscriptions.s(),
            task_update_payment_history.s()
        )()
        res.get()
    update_asaas_info.short_description = 'Atualizar dados Asaas'


@register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = "name", "phone", "email", "address", "jadlog_agency_id",
    readonly_fields = "jadlog_agency_options", "agency_options"
    form = SenderModelForm
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
         {"fields": ("jadlog_agency_id", "agency_options", "update_jadlog_options")}),
    )

    def has_add_permission(self, request, obj=None):
        # can only create if there are none existing
        return Sender.objects.count() == 0

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
