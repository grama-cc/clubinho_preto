from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save

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

def get_label_print_link(sender, instance, created, **kwargs):
    if created:
        from celery_app.celery import task_print_labels
        task_print_labels.delay(instance.id)

post_save.connect(get_label_print_link, sender=Purchase)
        
        