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
    subscriber = models.OneToOneField('account.Subscriber', on_delete=models.SET_NULL, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(null=True)
    asaas_id = models.CharField(max_length=255, blank=True, null=True)
    billingType = models.CharField(max_length=255, blank=True, null=True)
    cycle = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"


class PaymentHistory(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    due_date = models.DateTimeField(null=True)
    invoice_id = models.CharField(max_length=255, blank=True, null=True)
    billingType = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Histórico de Pagamento"
        verbose_name_plural = "Histórico de Pagamentos"
