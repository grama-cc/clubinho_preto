from django.db import models
from django.utils import timezone
from django.db.models import Q


class ShippingOption(models.Model):

    name = models.CharField(max_length=255, verbose_name="Nome")
    company_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Nome")
    price = models.FloatField(null=True, blank=True, verbose_name="Preço")

    delivery_time = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tempo de entrega (em dias)")
    delivery_time_min = models.PositiveIntegerField(null=True, blank=True,
                                                    verbose_name="Tempo de entrega mínimo (em dias)")
    delivery_time_max = models.PositiveIntegerField(null=True, blank=True,
                                                    verbose_name="Tempo de entrega máximo (em dias)")

    melhor_envio_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="Melhor Envio ID")

    def __str__(self):
        msg = ""
        if self.company_name:
            msg += self.company_name + " - "
        if self.name:
            msg += self.name
        if self.price:
            msg += " - R$ " + str(self.price)
        if msg:
            return msg
        return super().__str__()
        
    class Meta:
        verbose_name = "Opção de Envio"
        verbose_name_plural = "Opções de Envio"


class Shipping(models.Model):

    date_created = models.DateTimeField(default=timezone.now, verbose_name="Data de criação")

    box = models.ForeignKey("Box", on_delete=models.PROTECT, verbose_name="Caixa", related_name="shippings")
    recipient = models.ForeignKey("account.Subscriber", on_delete=models.PROTECT, verbose_name="Destinatário",
                                  related_name="shippings")


    shipping_options = models.ManyToManyField("ShippingOption", blank=True, verbose_name="Opções de Envio",
                                              related_name="+")

    shipping_option_selected = models.ForeignKey(
        "ShippingOption", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Opção de Envio Selecionada",
        related_name="+",)  # todo: limit_choices_to

    label = models.JSONField(null=True, blank=True, verbose_name="Dados da Etiqueta")

    def __str__(self):
        if self.id:
            return f"{self.id}"
        return "Novo Envio"

    class Meta:
        verbose_name = "Envio"
        verbose_name_plural = "Envios"

    @property
    def processed(self):
        return self.shipping_options.count() > 0


    def delete_label(self):
        if self.label and self.label.get('id'):
            from melhor_envio.service import MelhorEnvioService

            response = MelhorEnvioService.remove_label_from_cart(self.label.get('id'))            
            if response.ok or response.status_code == 404:
                self.label = None
                self.save()
                return True