import json
from datetime import datetime, timedelta

import requests
from account.models import Subscriber
from clubinho_preto.settings import ASAAS_KEY, ASAAS_URL

from finance.models import Subscription
from clubinho_preto.settings import BASE_SUBSCRIPTION_VALUE


class FinanceService:
    @staticmethod
    def asaas_resquest(api_endpoint, method='GET', data=None):
        url = f'{ASAAS_URL}{api_endpoint}'

        if method in ['GET', 'POST']:
            if method == 'GET':
                r = requests.get(url, headers={'access_token': ASAAS_KEY})
            elif method == 'POST':
                r = requests.post(url, data=json.dumps(data), headers={'access_token': ASAAS_KEY})
            return r.json()

        return False

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
                'subscriber': subscriber if subscriber else None,
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
            except Exception as e:
                print(f"Subscription import error {e}")
                errors += 1

        return [created, errors]

    @staticmethod
    def update_asaas_subscriptions(ids=None):
        asaas_subscriptions = FinanceService.get_asaas_subscriptions()
        subscribers = Subscriber.objects.all().values_list('id', 'asaas_customer_id')
        subscribers_dict = {s[1]:s[0] for s in subscribers}

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

            customer_id = asaas_subscription.get('customer')
            subscriber = subscribers_dict.get(customer_id)
            if subscriber:
                data['subscriber'] = subscriber

            try:
                subscriptions.update(**data)
                updated += len(subscriptions)
            except Exception as e:
                errors += len(subscriptions) if subscriptions else 1

        return [updated, errors]

    @staticmethod
    def create_asaas_payment(customer_id, delivery_choice):
        total_value = float(BASE_SUBSCRIPTION_VALUE) + float(delivery_choice.get('value'))
        url = 'payments'
        data = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "value": total_value,
            "dueDate": (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'),
            "description": f"Assinatura Clubinho Preto + frete para { delivery_choice.get('title')}",
            "cycle": "MONTHLY",  # todo: check cycle
        }

        response = FinanceService.asaas_resquest(url, method='POST', data=data)
        return response

    def create_asaas_subscription(customer_id, delivery_choice):
        total_value = float(BASE_SUBSCRIPTION_VALUE) + float(delivery_choice.get('value'))
        url = 'subscriptions'
        data = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "value": total_value,
            "dueDate": (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'),
            "description": f"Assinatura Clubinho Preto + frete para { delivery_choice.get('title')}",
            "cycle": "MONTHLY"
        }

        response = FinanceService.asaas_resquest(url, method='POST', data=data)
        return response