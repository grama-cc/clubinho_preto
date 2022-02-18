from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = 'Test commands'

    def handle(self, *args, **options):
        from account.models import Warning

        pass
        