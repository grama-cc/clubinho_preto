from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Populate the database with initial data'

    def handle(self, *args, **options):
        from account.models import Sender

        if not Sender.objects.count():
            Sender.objects.create(
                **{
                    "name": "Nome do remetente",
                    "phone": "53984470102",
                    "email": "contato@melhorenvio.com.br",
                    "document": "16571478358",
                    "company_document": "89794131000100",
                    "state_register": "123456",
                    "address": "Endereço do remetente",
                    "complement": "Complemento",
                    "number": "1",
                    "district": "Bairro",
                    "city": "São Paulo",
                    "country_id": "BR",
                    "postal_code": "01002001",
                    "note": "observação"
                })
            print("Criou remetente com dados exemplo")
        else:
            print("Já existe um remetente cadastrado")

