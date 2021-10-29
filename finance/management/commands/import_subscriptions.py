from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import subscriptions from Asaas API'

    def handle(self, *args, **options):
        from finance.service import FinanceService
        created, errors = FinanceService.import_asaas_subscriptions()
        return f'{created} assinaturas criadas, {errors} erros'
