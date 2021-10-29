import json
from django.core.management.base import BaseCommand

from account.models import subscriber


class Command(BaseCommand):
    help = 'Test command'

    def handle(self, *args, **options):
        from account.service import AccountService
        data = {
            "name": "Marcelo Almeida",
            "email": "marcelo.almeida@gmail.com",
            "phone": "4738010919",
            "mobilePhone": "4799376637",
            "cpfCnpj": "24971563792",
            "postalCode": "01310-000",
            "address": "Av. Paulista",
            "addressNumber": "150",
            "complement": "Sala 201",
            "province": "Centro",
            "externalReference": "12987382",
            "notificationDisabled": False,
            "additionalEmails": "marcelo.almeida2@gmail.com,marcelo.almeida3@gmail.com",
            "municipalInscription": "46683695908",
            "stateInscription": "646681195275",
            "observations": "ótimo pagador, nenhum problema até o momento",

            "relatedness": "PA",
            "relatedness_raw": "pai",
            "kids_name": "Criança filha",
            "kids_age": "8",
            "kids_gender": "MA",
            "kids_race": "YE",
            "kids_gender_raw": "menino",
            "kids_race_raw": "asiática",
            "subscribing_date": "2020-02-02",
        }
        response, subscriber = AccountService.create_asaas_customer(data)

        if response.ok:
            print("Criado com sucesso")
        else:
            if response.content:
                content = json.loads(response.content)
                print(content)
            else:
                print('Não há mensagem de erro')
