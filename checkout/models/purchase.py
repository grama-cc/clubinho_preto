from django.db import models
from django.utils import timezone


class Purchase(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(verbose_name='Data de criação')
    total = models.FloatField(default=0, verbose_name="Preço")
    status = models.CharField(max_length=255, null=True, blank=True)    
    full_info = models.JSONField(null=True, blank=True, verbose_name="Informações completas")
    print_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Compra de etiqueta'

    def __str__(self):
        if self.id:
            return self.id
        return super().__str__()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        return super().save(*args, **kwargs)