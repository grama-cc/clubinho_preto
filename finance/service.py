import requests
from account.models import Subscriber
from clubinho_preto.settings import ASAAS_KEY, ASAAS_URL

from finance.models import Subscription


class FinanceService:
    @staticmethod
    def asaas_resquest(api_endpoint):
        url = f'{ASAAS_URL}{api_endpoint}'
        r = requests.get(url, headers={'access_token': ASAAS_KEY})
        return r.json()

    @staticmethod
    def get_asaas_customers():
        offset = 0
        limit = 100
        
        url = f'customers?offset={offset}&limit={limit}'
        content = FinanceService.asaas_resquest(url)
        has_more = content.get('hasMore')
        customers = content.get('data')
        while has_more:
            offset += limit
            url = f'customers?offset={offset}&limit={limit}'
            content = FinanceService.asaas_resquest(url)
            customers += content.get('data')
            has_more = content.get('hasMore')
            
        return customers

    @staticmethod
    def get_asaas_subscriptions(customer_id=None):
        offset = 0
        limit = 100

        url = f'subscriptions?offset={offset}&limit={limit}'
        if customer_id:
            url += f'&customer={customer_id}'

        content = FinanceService.asaas_resquest(url)
        subscriptions = content.get('data')
        has_more = content.get('hasMore')

        while has_more:
            offset += limit
            url = f'subscriptions?offset={offset}&limit={limit}'
            content = FinanceService.asaas_resquest(url)
            subscriptions += content.get('data')
            has_more = content.get('hasMore')

        return subscriptions

    @staticmethod
    def import_asaas_subscriptions():
        subscriptions = FinanceService.get_asaas_subscriptions()
        existing_subscriptions_ids = Subscription.objects.all().values_list('asaas_id', flat=True)

        created = errors = 0

        for subscription in subscriptions:

            # skip existing subscriptions
            if subscription.get('id') in existing_subscriptions_ids:
                continue

            customer_id = subscription.get('customer')
            subscriber = Subscriber.objects.filter(asaas_customer_id=customer_id).first() or None
            data = {
                'subscriber': subscriber.id if subscriber else None,
                'value': subscription.get('value'),
                'date': subscription.get('dateCreated'),
                'asaas_id': subscription.get('id'),
                'billingType': subscription.get('billingType'),
                'cycle': subscription.get('cycle'),
                'description': subscription.get('description'),
                'status': subscription.get('status'),
                'deleted': subscription.get('deleted'),
            }
            try:
                print(Subscription.objects.create(**data))
                created += 1
            except:
                errors += 1

        return [created, errors]
        
    @staticmethod
    def update_asaas_subscriptions(ids=None):
        asaas_subscriptions = FinanceService.get_asaas_subscriptions()
        
        updated = errors = 0

        for asaas_subscription in asaas_subscriptions:            
            subscriptions = Subscription.objects.filter(asaas_id=asaas_subscription.get('id'))
            
            data = {
                'value': asaas_subscription.get('value'),
                'billingType': asaas_subscription.get('billingType'),
                'cycle': asaas_subscription.get('cycle'),
                'description': asaas_subscription.get('description'),
                'status': asaas_subscription.get('status'),
                'deleted': asaas_subscription.get('deleted'),
            }
            try:
                subscriptions.update(**data)
                updated += len(subscriptions)
            except:
                errors += len(subscriptions) if subscriptions else 1

        return [updated, errors]
