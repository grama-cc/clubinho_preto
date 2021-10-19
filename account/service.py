from .models import Subscriber
class AccountService:
    @staticmethod
    def update_asaas_customer_id(email, id):
        return Subscriber.objects.filter(email=email).update(asaas_customer_id=id)

    @staticmethod
    def list_asaas_customer_id():
        return Subscriber.objects.filter(asaas_customer_id__isnull=False).values_list('asaas_customer_id', flat=True)
        