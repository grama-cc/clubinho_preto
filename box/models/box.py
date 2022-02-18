from django.db import models
from django.utils.translation import gettext_lazy as _

class BoxItem(models.Model):

    class TYPE(models.TextChoices):
        BOOK = 'LI', _('Livro')
        TOY = 'TO', _('Brinquedo')
        PRIZE = 'PR', _('Brinde')
        OTHER = 'OT', _('Outro')
    
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    type = models.CharField(choices=TYPE.choices, max_length=3, verbose_name="Tipo", default=TYPE.OTHER)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"


class Box(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    width = models.FloatField(default=23.0, verbose_name="Largura (cm)")
    height = models.FloatField(default=5.0, verbose_name="Altura (cm)")
    length = models.FloatField(default=35.0, verbose_name="Comprimento (cm)")
    weight = models.FloatField(default=1.0, verbose_name="Peso (kg)")

    items = models.ManyToManyField("BoxItem", blank=True, verbose_name="Itens")
    letter = models.FileField(upload_to='cartas/', blank=True, null=True, verbose_name="Carta de orientação")

    insurance_value = models.FloatField(default=0, verbose_name="Valor do Seguro")
    receipt = models.BooleanField(default=False, verbose_name="Aviso de recebimento")
    own_hand = models.BooleanField(default=False, verbose_name="Mãos próprias")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"
