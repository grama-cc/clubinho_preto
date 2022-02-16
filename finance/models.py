from django.db import models

DELIVERY_CHOICES = {
    'rio': {
        'value': 15.00,
        'title': 'Cidade do Rio'
    },
    'metropolitana': {
        'value': 20.00,
        'title': 'Região Metropolitana (Baixada, Niterói e São Gonçalo)'
    },
    'sp_es_mg': {
        'value': 30.00,
        'title': 'SP, ES e MG'
    },
    'sul_bahia': {
        'value': 30.00,
        'title': 'Região Sul e Bahia'
    },
}


class Subscription(models.Model):
    subscriber = models.OneToOneField('account.Subscriber', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Assinante')
    value = models.FloatField(blank=True, null=True, verbose_name='Valor')
    date = models.DateTimeField(null=True, verbose_name='Data')
    asaas_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID Asaas')
    billingType = models.CharField(max_length=255, blank=True, null=True, verbose_name='Tipo de cobrança')
    cycle = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ciclo')
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name='Descrição')
    status = models.CharField(max_length=255, blank=True, null=True)
    deleted = models.BooleanField(default=False, verbose_name='Excluído')

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"


class PaymentHistory(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Assinatura')
    value = models.FloatField(blank=True, null=True, verbose_name='Valor')
    due_date = models.DateTimeField(null=True, verbose_name='Data de vencimento')
    invoice_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID da fatura')
    billingType = models.CharField(max_length=255, blank=True, null=True, verbose_name='Tipo de cobrança')
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Histórico de Pagamento"
        verbose_name_plural = "Histórico de Pagamentos"


def fetch_payments_history(sender, instance, created, *args, **kwargs):
    if created:
        from celery_app.celery import task_update_payment_history
        task_update_payment_history.delay([instance.id])

models.signals.post_save.connect(fetch_payments_history, sender=Subscription)