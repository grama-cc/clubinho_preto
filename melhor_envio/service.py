import json

import requests
from checkout.models import Label, Purchase
from clubinho_preto.settings import (MELHORENVIO_CLIENT_ID,
                                     MELHORENVIO_REDIRECT_URL,
                                     MELHORENVIO_SECRET, MELHORENVIO_URL)
from django.core.cache import cache

MELHORENVIO_CACHE_TIME = 2592000


def save_token_to_cache(data):
    cache.set("access_token", data.get("access_token"), MELHORENVIO_CACHE_TIME)  # valid for 30 days
    cache.set("refresh_token", data.get("refresh_token"), int(MELHORENVIO_CACHE_TIME*1.5))  # valid for 45 days


class MelhorEnvioService():

    @staticmethod
    def melhor_envio_request(url, method='get', data={}):
        bearer_token = MelhorEnvioService.get_token()
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}

        return getattr(requests, method)(
            url=f"{MELHORENVIO_URL}{url}",
            headers=headers,
            data=json.dumps(data)
        )

    @staticmethod
    def set_access_token(code):
        response = requests.post(
            f"{MELHORENVIO_URL}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": {MELHORENVIO_CLIENT_ID},
                "client_secret": {MELHORENVIO_SECRET},
                "redirect_uri": {MELHORENVIO_REDIRECT_URL},
                "code": {code},
            },
        )
        if response.ok:
            # save tokens to cache
            data = response.json()
            save_token_to_cache(data)
        return response

    @staticmethod
    def set_refresh_token(token=None):
        if not token:
            token = cache.get("refresh_token")

        response = requests.post(
            f"{MELHORENVIO_URL}/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": {MELHORENVIO_CLIENT_ID},
                "client_secret": {MELHORENVIO_SECRET},
                "refresh_token": {token},
            },
        )

        if response.ok:
            # save tokens to cache
            data = response.json()
            save_token_to_cache(data)
        return response

    @staticmethod
    def get_token():
        token = cache.get("access_token")
        if token:
            return token
        else:
            refresh_token = cache.get("refresh_token")
            if refresh_token:
                response = MelhorEnvioService.set_refresh_token(refresh_token)
                if response.ok:
                    token = response.json().get("access_token")
                    return token
            else:
                # todo: if not refresh_token: reauthenticate via 'AuthorizeApplicationView' api
                pass

            print("\t\tSEM TOKEN")
            return None

    @staticmethod
    def get_shipping_options(postal_from, postal_to, height, width, length, weight, insurance_value, receipt, own_hand):
        """
        Make a request to Melhor Envio API and get avaliable shipping options with passed params
        """
        data = {
            "from": {
                "postal_code": postal_from
            },
            "to": {
                "postal_code": postal_to
            },
            "package": {
                "height": height,
                "width": width,
                "length": length,
                "weight": weight
            },
            "options": {
                "insurance_value": insurance_value,
                "receipt": receipt,
                "own_hand": own_hand
            }
        }
        response = MelhorEnvioService.melhor_envio_request(
            url="api/v2/me/shipment/calculate",
            method="post",
            data=data
        )

        if response.ok:
            try:
                return response.json()
            except:
                # Returns html if there is error
                print(f"Não conseguiu gerar opções de frete {response.status_code}")
                return False

        else:
            print(f"Não conseguiu gerar opções de frete {response.status_code}")
            return False

    @staticmethod
    def add_items_to_cart(shippings, sender):
        """
        Add delivery options to MelhorEnvio cart.
        After this, comes the checkout step
        """
        success = 0
        failure = 0
        for shipping in shippings.filter(label__isnull=True):

            recipient = shipping.recipient
            same_name_subscriber_fields = 'name', 'email', 'phone', 'address', 'complement',

            # TODO: NFE
            nfe = "31190307586261000184550010000092481404848162"

            data = {
                "service": shipping.shipping_option_selected.melhor_envio_id,

                # todo: agency
                # Nota: o campo agency é obrigatório para a transportadora JadLog apenas
                # para integrações que utilizem o token gerado no painel do Melhor Envio,
                # não se fazendo necessário para outras transportadoras ou integrações
                # que utilizem os tokens gerados através de OAuth2.
                # "agency": 49,


                "from": sender,
                "to": {

                    **{field: getattr(recipient, field) for field in same_name_subscriber_fields},
                    "document": recipient.cpf,
                    "number": recipient.addressNumber,
                    "district": recipient.province,
                    "postal_code": recipient.cep,
                    # "company_document": "89794131000101", # PJ only
                    # "state_register": "123456", # PJ only
                    "city": recipient.city,
                    "state_abbr": recipient.state_initials,
                    "country_id": "BR",
                    "note": recipient.note or '',
                },
                "volumes": [  # Correios only accepts one volume per request
                    {
                        "height": shipping.box.height,
                        "width": shipping.box.width,
                        "length": shipping.box.length,
                        "weight": shipping.box.weight,
                    }
                ],
                "options": {
                    "insurance_value": shipping.box.insurance_value,
                    "receipt": shipping.box.receipt,
                    "own_hand": shipping.box.own_hand,
                    "reverse": False,
                    "non_commercial": False,


                    # Nota: para transportadoras privadas (todas menos Correios),
                    # o campo options.invoice.key é obrigatório e deve conter a chave da NF.
                    # Isto pode ser contornado configurando o envio para que o mesmo seja
                    # um envio não comercial (com declaração de conteúdo), para isto deve
                    # ser setada a flag options.non_commercial como true.

                    "invoice": {
                        "key": nfe
                    },
                    # "platform": "Nome da Plataforma",
                    # "tags": [
                    #     {
                    #         "tag": "Identificação do pedido na plataforma, exemplo: 1000007",
                    #         "url": "Link direto para o pedido na plataforma, se possível, caso contrário pode ser passado o valor null"
                    #     }
                    # ]
                }
            }

            response = MelhorEnvioService.melhor_envio_request(
                url="api/v2/me/cart/",
                method="post",
                data=data
            )

            if response.ok:
                try:
                    fields = 'id','created_at','price','format','status','protocol','volumes',
                    info = response.json()
                    Label.objects.create(
                        shipping=shipping,
                        full_info=info,
                        **{field: info.get(field) for field in fields}
                    )
                    success += 1

                except:
                    failure += 1
                    print(f"1-Não conseguiu adicionar itens no carrinho {response.status_code}")
            else:
                print(f"2-Não conseguiu adicionar itens no carrinho {response.status_code}")

        return f"{success} itens adicionados ao carrinho com sucesso e {failure} itens não adicionados"

    @staticmethod
    def remove_label_from_cart(label_id):
        return MelhorEnvioService.melhor_envio_request(
            url=f"api/v2/me/cart/{label_id}",
            method='delete'
        )

    @staticmethod
    def cart_checkout(label_ids):
        payload = {
            "orders": [str(label_id) for label_id in label_ids]
        }
        response = MelhorEnvioService.melhor_envio_request(
            url=f"api/v2/me/shipment/checkout",
            method='post',
            data=payload
        )
        if response.ok:
            try:
                checkout_data = response.json()
                
                orders = checkout_data.get('purchase', {}).get('orders', [])
                label_ids = [order.get('id') for order in orders]
                
                fields = 'id', 'created_at', 'total', 'status'
                data = {}
                for field in fields:
                    value = checkout_data.get('purchase',{}).get(field)
                    if value:
                        data[field] = value
                purchase = Purchase.objects.create(
                    **data,
                    full_info=checkout_data
                )

                return Label.objects.filter(id__in=label_ids).update(purchase=purchase, status='released')
                
            except Exception as e:
                raise e
                return False
        return False
