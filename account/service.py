from os import name
import requests
from clubinho_preto.settings import ASAAS_KEY, ASAAS_URL

from .models import Subscriber


class AccountService:
    @staticmethod
    def update_asaas_customer_id(email, id):
        return Subscriber.objects.filter(email=email).update(asaas_customer_id=id)

    @staticmethod
    def list_asaas_customer_id():
        return Subscriber.objects.filter(asaas_customer_id__isnull=False).values_list('asaas_customer_id', flat=True)

    @staticmethod
    def create_asaas_customer(customer_data):

        # separate asaas data from our data
        subscriber_keys = ['relatedness', 'more_info', 'relatedness', 'relatedness_raw', 'kids_name',
                           'kids_age', 'kids_gender', 'kids_race', 'kids_gender_raw', 'kids_race_raw', 'subscribing_date', ]

        subscriber_data = {key: customer_data[key] for key in customer_data if key in subscriber_keys}

        for key, value in subscriber_data.items():
            customer_data.pop(key)

        url = f"{ASAAS_URL}/customers"
        response = requests.post(url, json=customer_data, headers={'access_token': ASAAS_KEY})
        if response.ok:
            data = response.json()

            try:
                Subscriber.objects.create(
                    asaas_customer_id=data.get('id', None),
                    cep=data.get('postalCode', None),

                    name=data.get('name', None),
                    email=data.get('email', None),
                    phone=data.get('phone', None),
                    address=data.get('address', None),

                    **subscriber_data
                )
            except Exception as e:
                print(f'______COULD NOT CREATE SUBSCRIBER: {e}')
                # todo: handle error: delete customer from asaas?
                # todo: create asaas customer on Subscriber model's save()?

        return response
