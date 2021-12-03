from django.db import models


class BoxItem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    # todo: type: livro ou brinde, brindquedo

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"


class Box(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    width = models.FloatField(null=True, verbose_name="Largura (cm)")
    height = models.FloatField(null=True, verbose_name="Altura (cm)")
    length = models.FloatField(null=True, verbose_name="Comprimento (cm)")
    weight = models.FloatField(null=True, verbose_name="Peso (kg)")

    items = models.ManyToManyField("BoxItem", blank=True, verbose_name="Itens")
    # todo carta de orientacao

    insurance_value = models.FloatField(default=0, verbose_name="Valor do Seguro")
    receipt = models.BooleanField(default=False, verbose_name="Aviso de recebimento")
    own_hand = models.BooleanField(default=False, verbose_name="Mãos próprias")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"
