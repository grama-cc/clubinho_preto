
from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from finance.models import SUBSCRIPTION_SUCCESS_STATUS

class SubscriberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def allowed_shipping(self):
        """ All subscribers who can receive a new shipment, ie:
        - have paid this month's subscription
        - do not have an existing shipment in the current month
        """
        return self.get_queryset()\
            .select_related('subscription')\
            .prefetch_related('subscription__paymenthistory_set')\
            .filter(
                subscription__status='ACTIVE',  # - have an active subscription
                subscription__paymenthistory__due_date__month=timezone.now().month,
                subscription__paymenthistory__status__in=SUBSCRIPTION_SUCCESS_STATUS,
        ).exclude(
                shippings__date_created__month=timezone.now().month
        ).distinct()
        


class Subscriber(models.Model):

    class RELATEDNESS(models.TextChoices):
        PARENT = 'PA', _('Mãe/Pai')
        GRANPARENT = 'GR', _('Avôou Avó')
        STEP = 'ST', _('Madrasta ou Padrasto')
        AUNT = 'AU', _('Tia ou Tio')
        BROTHER = 'BR', _('Irmão ou Irmã')
        TEACHER = 'TE', _('Professor(a)')
        OTHER = 'OT', _('Outro')

    class GENDER(models.TextChoices):
        MALE = 'MA', _('Masculino')
        FEMALE = 'FE', _('Feminino')
        NO_ANSWER = 'NO', _('Prefiro não responder')

    class RACE(models.TextChoices):
        WHITE = 'WH', _('Branca')
        PARDO = 'PA', _('Parda')
        BLACK = 'BL', _('Preta')
        YELLOW = 'YE', _('Amarela')
        NATIVE = 'NA', _('Indígena')
        BLACK_NATIVE = 'BN', _('Preta e Indígena')

    # ! Update admin fields if you add new ones here

    email = models.EmailField()
    name = models.CharField(max_length=255, null=True, verbose_name='Nome')
    cpf = models.CharField(max_length=11, null=True, verbose_name='CPF')

    asaas_customer_id = models.CharField(max_length=255, blank=True, null=True)

    phone = models.CharField(max_length=255, verbose_name="telefone", null=True)
    address = models.CharField(max_length=255, verbose_name="endereço de entrega", null=True)
    addressNumber = models.CharField(max_length=255, verbose_name="número", null=True)
    complement = models.CharField(max_length=255, verbose_name="complemento", blank=True, null=True)
    province = models.CharField(max_length=255, verbose_name="bairro", null=True)
    cep = models.CharField(max_length=255, verbose_name="CEP", null=True)
    delivery = models.CharField(max_length=255, verbose_name="frete para", blank=True, null=True)
    city = models.CharField(max_length=255, verbose_name="cidade", null=True)
    state_initials = models.CharField(max_length=2, null=True, verbose_name='UF')
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name='Observações de endereço')

    more_info = models.TextField(verbose_name="conta pra gente, do que a criança mais gosta", blank=True, null=True)
    relatedness = models.CharField(max_length=2, choices=RELATEDNESS.choices,
                                   default=RELATEDNESS.PARENT, blank=True, null=True, verbose_name='parentesco')
    relatedness_raw = models.CharField(max_length=255, blank=True, null=True)
    kids_name = models.CharField(max_length=255, verbose_name="Nome da criança", blank=True, null=True)
    kids_age = models.IntegerField(verbose_name="Idade da criança", blank=True, null=True)
    kids_gender = models.CharField(max_length=2, choices=GENDER.choices,
                                   default=GENDER.NO_ANSWER, blank=True, null=True, verbose_name="sexo da criança")
    kids_race = models.CharField(max_length=2, choices=RACE.choices, default=RACE.BLACK, blank=True, null=True, verbose_name="Cor da criança")
    kids_gender_raw = models.CharField(max_length=255, blank=True, null=True)
    kids_race_raw = models.CharField(max_length=255, blank=True, null=True)
    subscribing_date = models.DateTimeField(null=True, verbose_name='Data de inscrição')

    objects = SubscriberManager()
    no_joins = models.Manager()

    class Meta:
        verbose_name = "Assinante"
        verbose_name_plural = "Assinantes"

    def __str__(self) -> str:
        if self.name:
            return self.name
        return self.email

    def save(self, *args, **kwargs) -> None:
        if not self.subscribing_date:
            self.subscribing_date = timezone.now()
        return super().save(*args, **kwargs)

    def can_send_package(self, get_field=False):
        fields = 'name', 'email', 'phone', 'address', 'cpf', 'addressNumber', 'province', 'cep', 'city', 'state_initials',
        for field in fields:
            if not getattr(self, field):
                return field if get_field else False
        return True
