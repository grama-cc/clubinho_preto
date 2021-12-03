from box.models.shipping import Shipping
from django.contrib import admin
from django.contrib.admin import register
from django.db.models import Count, F

from finance.models import Subscription
from .models import Sender, Subscriber


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    fields = 'date', 'value', 'asaas_id', 'billingType', 'cycle', 'description', 'status', 'deleted',
    readonly_fields = 'date', 'value', 'asaas_id', 'billingType', 'cycle', 'description', 'status', 'deleted',


class ShippingInline(admin.StackedInline):
    model = Shipping
    extra = 0
    fields = 'date_created', 'box', 'shipping_option_selected',
    readonly_fields = 'date_created', 'box', 'shipping_option_selected'


@register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email', 'relatedness_raw', 'kids_race_raw',)
    list_display = ('id', 'name', 'email', 'city', 'province', '_can_send_package', 'subscription_status',
                    'shipping_count', 'relatedness', 'kids_race', 'asaas_customer_id')
    ordering = ('name',)
    actions = 'importar_planilha', 'import_subscribers',
    inlines = SubscriptionInline, ShippingInline,
    # todo: filter by "can_send_package"
    # self.fields['']

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .select_related('subscription')\
            .annotate(
                shipping_count=Count('shippings'),
                subscription_status=F('subscription__status'),
        )

    def subscription_status(self, obj):
        return obj.subscription_status
    subscription_status.short_description = 'Status'

    def shipping_count(self, obj):
        return obj.shipping_count
    shipping_count.short_description = 'Envios'

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
    list_display = "name", "phone", "email", "address",

    fieldsets = (
        ("Informações Gerais",
         {"fields": ("name", "phone", "email", )}),

        ("Documentos",
         {"fields": ("document", "company_document", "state_register")}),

        ("Endereço",
         {"fields": ("address", "complement", "number", "district", "city", "country_id", "postal_code", )}),

        (None,
         {"fields": ("note",)}),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
