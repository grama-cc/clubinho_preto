from django.db import models
from django.utils import timezone

class Label(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    price = models.FloatField(default=0, verbose_name="Preço")
    format = models.CharField(max_length=255, null=True, blank=True, verbose_name="Formato")
    status = models.CharField(max_length=255, null=True, blank=True)
    protocol = models.CharField(max_length=255, null=True, blank=True, verbose_name="Protocolo")
    volumes = models.JSONField(null=True, blank=True)
    full_info = models.JSONField(null=True, blank=True, verbose_name="Informações completas")

    shipping = models.OneToOneField('box.Shipping', on_delete=models.CASCADE, null=True, blank=True)
    purchase = models.ForeignKey('checkout.Purchase', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Etiqueta'

    def __str__(self):
        if self.id:
            return self.id
        return super().__str__()
    

# todo: remove from cart on pre-delete