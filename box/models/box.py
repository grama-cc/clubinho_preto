from django.db import models


class BoxItem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"


class Box(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    width = models.FloatField(blank=True, null=True, verbose_name="Largura (cm)")
    height = models.FloatField(blank=True, null=True, verbose_name="Altura (cm)")
    length = models.FloatField(blank=True, null=True, verbose_name="Comprimento (cm)")
    weight = models.FloatField(blank=True, null=True, verbose_name="Peso (kg)")

    items = models.ManyToManyField("BoxItem", blank=True, verbose_name="Itens")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"
