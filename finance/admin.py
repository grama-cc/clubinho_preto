from django.contrib import admin
from django.contrib.admin import register
from django.db.models import Count
from .models import Subscription, PaymentHistory
from django.contrib.auth.models import Group
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule


class PaymentHistoryInlineAdmin(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = 'value', 'due_date', 'invoice_id', 'billingType', 'status',


@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'subscriber', 'payments', 'value', 'status', 'cycle')
    list_filter = 'status', 'billingType', 'cycle'
    inlines = (PaymentHistoryInlineAdmin,)
    actions = 'import_subscriptions', 'update_subscriptions'

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .prefetch_related('paymenthistory_set')\
            .select_related('subscriber')\
            .annotate(payments=Count('paymenthistory'))

    def payments(modeladmin, obj):
        return obj.payments
    payments.short_description = 'Pagamentos'

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


admin.site.unregister(Group)

# Hide Celery admin
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(SolarSchedule)
