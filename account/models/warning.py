from django.db import models
from django.utils import timezone


class Warning(models.Model):
    """
    Warning model created to notify Admin of (mostly celery tasks) platform errors
    """
    created_at = models.DateTimeField(default=timezone.now, verbose_name='data')
    text = models.CharField(max_length=255, verbose_name='texto')
    description = models.TextField(null=True, blank=True, verbose_name='descrição')
    solution = models.TextField(null=True, blank=True, verbose_name='solução')
    data = models.JSONField(null=True, blank=True, verbose_name='dados')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'aviso'
        verbose_name_plural = 'avisos'