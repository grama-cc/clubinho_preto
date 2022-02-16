from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.models import Group
from django.db.models import Count
from django.db.models.expressions import OuterRef, Subquery
from django_celery_beat.models import (ClockedSchedule, CrontabSchedule,
                                       IntervalSchedule, PeriodicTask,
                                       SolarSchedule)

from finance.models import SUBSCRIPTION_DICT

from .models import PaymentHistory, Subscription



class PaymentHistoryInlineAdmin(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = 'value', 'due_date', 'invoice_id', 'billingType', 'status',


@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = 'id', 'date', 'subscriber', 'value', 'status', 'charges', 'last_charge', 'cycle'
    list_filter = 'status', 'billingType', 'cycle', 'subscriber'
    inlines = PaymentHistoryInlineAdmin,
    actions = 'import_subscriptions', 'update_subscriptions', 'update_payment_history',

    def get_queryset(self, request):
        last_charge = PaymentHistory.objects.filter(
            subscription=OuterRef('pk')
        ).order_by('-due_date')
        return super().get_queryset(request)\
            .prefetch_related('paymenthistory_set')\
            .select_related('subscriber')\
            .annotate(
                charges=Count('paymenthistory'),
                last_charge_date=Subquery(last_charge.values_list('due_date', flat=True)[:1]),
                last_charge_status=Subquery(last_charge.values_list('status', flat=True)[:1]),
        )

    def charges(modeladmin, obj):
        return obj.charges
    charges.short_description = 'Cobranças'

    def last_charge(modeladmin, obj):
        date = obj.last_charge_date.strftime('%d/%m/%Y') \
            if hasattr(obj, 'last_charge_date') and obj.last_charge_date else 'S/ data'
        status = obj.last_charge_status \
            if hasattr(obj, 'last_charge_status') and obj.last_charge_status else 'S/ status'
        return f'{date} - {SUBSCRIPTION_DICT.get(status, status)}'
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
