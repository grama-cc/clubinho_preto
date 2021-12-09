from django.db import models


class Sender(models.Model):

    name = models.CharField(max_length=255, verbose_name="Nome")
    phone = models.CharField(max_length=255, verbose_name="Telefone")
    email = models.CharField(max_length=255)
    
    document = models.CharField(max_length=255, verbose_name="CPF")
    company_document = models.CharField(max_length=255, verbose_name="CNPJ")
    state_register = models.CharField(max_length=255, verbose_name="Inscrição Estadual")
    
    address = models.CharField(max_length=255, verbose_name="Endereço")
    complement = models.CharField(max_length=255, verbose_name="Complemento")
    number = models.CharField(max_length=255, verbose_name="Número")
    district = models.CharField(max_length=255, verbose_name="Bairro")
    city = models.CharField(max_length=255, verbose_name="Cidade")
    country_id = models.CharField(max_length=255, verbose_name="Sigla País")
    postal_code = models.CharField(max_length=255, verbose_name="CEP")
    note = models.CharField(max_length=255, verbose_name="Observação")

    jadlog_agency_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="Agência Jadlog")
    jadlog_agency_options = models.JSONField(default=dict, verbose_name="Opções Agências Jadlog")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Remetente"
        verbose_name_plural = "Remetente"
