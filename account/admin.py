from django.contrib import admin
from django.contrib.admin import register

from .models import Sender, Subscriber


@register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email', 'relatedness_raw', 'kids_race_raw',)
    list_display = ('id', 'name', 'email', 'cep', '_can_send_package', 'relatedness', 'kids_race', 'asaas_customer_id')
    ordering = ('name',)
    actions = 'importar_planilha', 'import_subscribers',
    # todo: filter by "can_send_package"
    # todo: Shipping Inline

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
