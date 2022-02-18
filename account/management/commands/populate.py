from django.core.management.base import BaseCommand
from celery_app.celery import task_import_asaas_customers, task_import_subscriptions, task_update_subscriptions
from celery import chain

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

    print("Importando assinantes e assinaturas")
    chain(
        task_import_asaas_customers.s(),
        task_import_subscriptions.s(),
        task_update_subscriptions.s(),
    )().get()