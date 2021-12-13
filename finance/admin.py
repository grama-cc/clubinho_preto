from django.contrib import admin
from django.contrib.admin import register
from django.db.models import Count, Max
from .models import Subscription, PaymentHistory
from django.contrib.auth.models import Group
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule


class PaymentHistoryInlineAdmin(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = 'value', 'due_date', 'invoice_id', 'billingType', 'status',


@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = 'id', 'date', 'subscriber', 'value', 'status','charges', 'last_charge', 'cycle'
    list_filter = 'status', 'billingType', 'cycle'
    inlines = PaymentHistoryInlineAdmin,
    actions = 'import_subscriptions', 'update_subscriptions', 'update_payment_history',

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .prefetch_related('paymenthistory_set')\
            .select_related('subscriber')\
            .annotate(
                charges=Count('paymenthistory'),
                last_charge=Max('paymenthistory__due_date__date'),
                )

    def charges(modeladmin, obj):
        return obj.charges
    charges.short_description = 'Cobranças'

    def last_charge(modeladmin, obj):
        return obj.last_charge
    last_charge.short_description = 'Última cobrança'

    def import_subscriptions(modeladmin, request, queryset):
        from finance.service import FinanceService
        created, errors = FinanceService.import_asaas_subscriptions()

        modeladmin.message_user(request, f'{created} assinaturas criadas, {errors} erros')
    import_subscriptions.short_description = "Importar assinaturas Asaas"

    def update_subscriptions(modeladmin, request, queryset):
        from finance.service import FinanceService
        updated, errors = FinanceService.update_asaas_subscriptions()

        modeladmin.message_user(request, f'{updated} assinaturas atualizadas, {errors} erros')
    update_subscriptions.short_description = "Atualizar assinaturas Asaas"

    def update_payment_history(modeladmin, request, queryset):
        from celery_app.celery import task_update_payment_history
        task_update_payment_history.delay()
        modeladmin.uccess_message = 'Atualização de pagamentos em andamento'
    update_payment_history.short_description = "Atualizar status de pagamento"

admin.site.unregister(Group)

# Hide Celery admin
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(SolarSchedule)
