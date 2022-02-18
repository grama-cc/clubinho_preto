import requests
from clubinho_preto.settings import ASAAS_KEY, ASAAS_URL
from account.models import Warning
from .models import Subscriber
import json

class AccountService:
    @staticmethod
    def update_asaas_customer_id(email, id):
        return Subscriber.objects.filter(email=email).update(asaas_customer_id=id)

    @staticmethod
    def list_asaas_customer_id():
        return Subscriber.objects.filter(asaas_customer_id__isnull=False).values_list('asaas_customer_id', flat=True)

    @staticmethod
    def create_asaas_customer(_customer_data):

        # Bypass "This querydict instance is immutable"
        # And get first item from each item on request.POST
        customer_data = {key: _customer_data.get(key, [None][0]) for key in _customer_data.keys()}

        # separate asaas data from application data
        subscriber_keys = ['relatedness', 'more_info', 'relatedness', 'relatedness_raw', 'kids_name',
                           'kids_age', 'kids_gender', 'kids_race', 'kids_gender_raw', 'kids_race_raw',
                           'subscribing_date', 'delivery', 'city', 'state_initials']
        subscriber_data = {key: customer_data[key] for key in customer_data if key in subscriber_keys}

        # Add complete subscriber info to Asaas customer
        observations = ''
        for key in subscriber_keys:
            observations += f"{key}:{customer_data.get(key)};"
        customer_data['observations'] = observations

        url = f"{ASAAS_URL}/customers"
        response = requests.post(url, json=customer_data, headers={'access_token': ASAAS_KEY})
        subscriber = None
        if response.ok:
            data = response.json()
            customer_keys = ['name', 'email', 'phone', 'address', 'addressNumber', 'province', 'complement']

            try:
                _subscriber_data = {
                    # different keys from asaas
                    'asaas_customer_id': data.get('id', None),
                    'cep': data.get('postalCode', None),
                    'cpf': data.get('cpfCnpj', None),

                    # same as asaas form
                    **{key: customer_data.get(key, None) for key in customer_keys},

                    # django only
                    **subscriber_data
                }
                subscriber = Subscriber.objects.create(**_subscriber_data)
            except Exception as e:
                Warning.objects.create(
                    text="Não foi possível criar Assinante",
                    description=str(e),
                    data=_subscriber_data,
                    solution="Tentar cadastrar manualmente pelo Admin de `Assinantes`"
                )

        return response, subscriber

    @staticmethod
    def import_asaas_customers():
        from uuid import uuid4

        from finance.service import FinanceService

        asaas_customers = FinanceService.get_asaas_customers()
        existing_customers_ids = Subscriber.objects.all().values_list('asaas_customer_id', flat=True)

        created = errors = skipped = 0

        for asaas_customer in asaas_customers:

            # skip existing customers
            if asaas_customer.get('id') in existing_customers_ids:
                skipped += 1
                continue

            email = asaas_customer.get('email', None) or f"{uuid4().int}@sem_email.com"
            keys = ['phone', 'address', 'addressNumber', 'complement', 'province']
            
            # parse from string to dict
            _observations = asaas_customer.get('observations','')
            if _observations:
                _observations = _observations.split(';')
                observations = {item.split(':')[0]: item.split(':')[1] for item in _observations if ':' in item}
                # remove keys that are not relevant
                items_to_remove = list(filter(lambda key_value:  key_value[1].strip() in ['None', ''],observations.items()))
                for key, value in items_to_remove:
                    observations.pop(key)
            else:
                observations = {}

            data = {
                'asaas_customer_id': asaas_customer.get('id'),
                'name': asaas_customer.get('name'),
                'email': email,
                'cep': asaas_customer.get('postalCode'),
                'cpf': asaas_customer.get('cpfCnpj'),
                'state_initials': asaas_customer.get('state'),

                **{key: asaas_customer.get(key, None) for key in keys},
                **observations
            }
            try:
                print(Subscriber.objects.create(**data))
                created += 1
            except Exception as e:
                errors += 1

        return [created, errors, skipped]
