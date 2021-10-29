
from django.db import models
from django.utils.translation import gettext_lazy as _


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

    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nome')
    cpf = models.CharField(max_length=11, blank=True, null=True, verbose_name='CPF')
    asaas_customer_id = models.CharField(max_length=255,blank=True, null=True)
    phone = models.CharField(max_length=255, verbose_name="telefone", blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="endereço de entrega", blank=True, null=True)
    cep = models.CharField(max_length=255, verbose_name="CEP", blank=True, null=True)
    more_info = models.TextField(verbose_name="conta pra gente, do que a criança mais gosta", blank=True, null=True)
    relatedness = models.CharField(max_length=2, choices=RELATEDNESS.choices, default=RELATEDNESS.PARENT, blank=True, null=True)
    relatedness_raw = models.CharField(max_length=255, blank=True, null=True)
    kids_name = models.CharField(max_length=255, verbose_name="Nome da criança", blank=True, null=True)
    kids_age = models.IntegerField(verbose_name="Idade da criança", blank=True, null=True)
    kids_gender = models.CharField(max_length=2, choices=GENDER.choices, default=GENDER.NO_ANSWER, blank=True, null=True)
    kids_race = models.CharField(max_length=2, choices=RACE.choices, default=RACE.BLACK, blank=True, null=True)
    kids_gender_raw = models.CharField(max_length=255, blank=True, null=True)
    kids_race_raw = models.CharField(max_length=255, blank=True, null=True)
    subscribing_date = models.DateTimeField(null=True)


    class Meta:
        verbose_name = "Assinante"
        verbose_name_plural = "Assinantes"

    def __str__(self) -> str:
        return self.email