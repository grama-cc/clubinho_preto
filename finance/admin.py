from django.contrib import admin
from django.contrib.admin import register
from .models import Subscription, PaymentHistory


class PaymentHistoryInlineAdmin(admin.TabularInline):
    model = PaymentHistory

@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','date', 'subscriber', 'value', 'status')
    filter = ('status')
    inlines = (PaymentHistoryInlineAdmin,)
    actions = 'import_subscriptions',

    def import_subscriptions(modeladmin, request, queryset):
        from finance.service import FinanceService
        created, errors = FinanceService.import_asaas_subscriptions()

        modeladmin.message_user(request, f'{created} assinaturas criadas, {errors} erros')

    import_subscriptions.short_description = "Importar assinaturas Asaas"