from django.contrib import admin
from django.contrib.admin import register
from .models import Subscription, PaymentHistory


class PaymentHistoryInlineAdmin(admin.TabularInline):
    model = PaymentHistory

@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','date', 'subscriber', 'value', 'status', 'cycle')
    list_filter = 'status', 'billingType', 'cycle'
    inlines = (PaymentHistoryInlineAdmin,)
    actions = 'import_subscriptions', 'update_subscriptions'

    def import_subscriptions(modeladmin, request, queryset):
        from finance.service import FinanceService
        created, errors = FinanceService.import_asaas_subscriptions()

        modeladmin.message_user(request, f'{created} assinaturas criadas, {errors} erros')

    def update_subscriptions(modeladmin, request, queryset):
        from finance.service import FinanceService
        updated, errors = FinanceService.update_asaas_subscriptions()

        modeladmin.message_user(request, f'{updated} assinaturas atualizadas, {errors} erros')

    import_subscriptions.short_description = "Importar assinaturas Asaas"
    update_subscriptions.short_description = "Atualizar assinaturas Asaas"


