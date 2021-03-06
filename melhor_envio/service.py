import json

import requests
from requests.api import get
from account.models import Sender, Warning
from checkout.models import Label, Purchase
from clubinho_preto.settings import (BACKEND_BASE_URL, JADLOG_ID,
                                     MELHORENVIO_CLIENT_ID,
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

            Warning.objects.create(
                text="Autentica????o do melhor envio vencida, por favor reautenticar.",
                description=f"Acessar a url {BACKEND_BASE_URL}/authorize_application, ver modelo de resposta abaixo",
                solution=f"?? preciso acessar a url de autentica????o. A resposta dela deve ser um c??digo de acesso.",
                data={
                    "token_type": "Bearer",
                    "expires_in": 2592000,
                    "access_token": "blabla...",
                    "refresh_token": "blabla..."
                }
            )
            print("Criou aviso")

            return None

    @staticmethod
    def get_shipping_options(shipping, postal_from):
        """
        Make a request to Melhor Envio API and get avaliable shipping options with passed params
        """

        def create_warning(error, data):
            Warning.objects.create(
                text="N??o foi poss??vel criar op????es de envio",
                description=str(error),
                solution=f"Revisar dados do envio #{shipping.id}",
                data=data
            )
        data = {
            "from": {
                "postal_code": postal_from
            },
            "to": {
                "postal_code": shipping.recipient.cep
            },
            "package": {
                "height": shipping.box.height,
                "width": shipping.box.width,
                "length": shipping.box.length,
                "weight": shipping.box.weight
            },
            "options": {
                "insurance_value": shipping.box.insurance_value,
                "receipt": shipping.box.receipt,
                "own_hand": shipping.box.own_hand
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
            except Exception as e:
                # Returns html if there is error
                create_warning("Retornou uma p??gina HTML ao inv??s de uma resposta de API.", data)
                return False

        else:
            create_warning(f"status da resposta:{response.status_code}, resposta:{response.content}", data)
            return False

    @staticmethod
    def add_items_to_cart(shippings, sender):
        """
        Add delivery options to MelhorEnvio cart.
        After this, comes the checkout step
        """

        def create_warning(shipping_id, error, data):
            Warning.objects.create(
                text="N??o foi poss??vel adicionar itens no carrinho",
                description=str(error),
                solution=f"Revisar dados do Envio #{shipping_id} e cep do remetente",
                data=data
            )

        labels = []
        for shipping in shippings:

            recipient = shipping.recipient
            same_name_subscriber_fields = 'name', 'email', 'phone', 'address', 'complement',

            data = {
                "service": shipping.shipping_option_selected.melhor_envio_id,
                
                # Nota: o campo agency ?? obrigat??rio para a transportadora JadLog apenas
                # para integra????es que utilizem o token gerado no painel do Melhor Envio,
                # n??o se fazendo necess??rio para outras transportadoras ou integra????es
                # que utilizem os tokens gerados atrav??s de OAuth2.
                # "agency": JADLOG_ID,


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
                    "non_commercial": True,


                    # Nota: para transportadoras privadas (todas menos Correios),
                    # o campo options.invoice.key ?? obrigat??rio e deve conter a chave da NF.
                    # Isto pode ser contornado configurando o envio para que o mesmo seja
                    # um envio n??o comercial (com declara????o de conte??do), para isto deve
                    # ser setada a flag options.non_commercial como true.

                    # "invoice": {
                    #     "key": nfe
                    # },
                    
                    # "platform": "Nome da Plataforma",
                    # "tags": [
                    #     {
                    #         "tag": "Identifica????o do pedido na plataforma, exemplo: 1000007",
                    #         "url": "Link direto para o pedido na plataforma, se poss??vel, caso contr??rio pode ser passado o valor null"
                    #     }
                    # ]
                }
            }

            if shipping.shipping_option_selected.company_name and 'jadlog' in shipping.shipping_option_selected.company_name.lower():
                data['agency'] = JADLOG_ID

            response = MelhorEnvioService.melhor_envio_request(
                url="api/v2/me/cart/",
                method="post",
                data=data
            )
            if response.ok:
                try:
                    fields = 'id', 'created_at', 'price', 'format', 'status', 'protocol', 'volumes',
                    info = response.json() # the error occurs here, when a HTML page cannot be converted to json
                    label = Label.objects.create(
                        shipping=shipping,
                        full_info=info,
                        **{field: info.get(field) for field in fields}
                    )   
                    labels.append(label)
                except:
                    create_warning(shipping.id, "Respondeu p??gina HTML ao inv??s de resposta de API", data)
            else:
                create_warning(
                    shipping.id, f"status da resposta:{response.status_code}, resposta:{response.content}", data)
        return [l.id for l in labels]

    @staticmethod
    def remove_label_from_cart(label_id):
        return MelhorEnvioService.melhor_envio_request(
            url=f"api/v2/me/cart/{label_id}",
            method='delete'
        )

    @staticmethod
    def cart_checkout(label_ids):

        def create_warning(error, data):
            Warning.objects.create(
                text="N??o foi poss??vel fazer checkout de etiquetas",
                description=str(error),
                solution=f"Verificar se todas as etiquetas est??o no carrinho (IDs das etiquetas no campo de dados)",
                data=data
            )

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
                    value = checkout_data.get('purchase', {}).get(field)
                    if value:
                        data[field] = value
                purchase = Purchase.objects.create(
                    **data,
                    full_info=checkout_data
                )

                return Label.objects.filter(id__in=label_ids).update(purchase=purchase, status='released')

            except Exception as e:
                create_warning(e, payload)
        else:
            create_warning(f"status da resposta:{response.status_code}, resposta:{response.content}", payload)
        return False

    @staticmethod
    def print_labels(purchase_id):

        purchase = Purchase.objects.get(id=purchase_id)
        label_ids = list(purchase.label_set.values_list('id', flat=True))

        data = {
            'orders': [str(label_id) for label_id in label_ids]
        }
        response = MelhorEnvioService.melhor_envio_request(
            url=f"api/v2/me/shipment/generate",
            method='post',
            data=data
        )
        if response.ok:
            try:
                response.json()  # may return a html page
            except:
                Warning.objects.create(
                    text="N??o conseguiu gerar as etiquetas para impress??o",
                    description=f"status da resposta:{response.status_code}, resposta:{response.content}",
                    solution=f"Verificar Compra: #{purchase_id}",
                    data=data
                )
                return False

        data['mode'] = 'public'  # anyone can see the labels

        response = MelhorEnvioService.melhor_envio_request(
            url=f"api/v2/me/shipment/print",
            method='post',
            data=data
        )
        if response.ok:
            try:
                data = response.json()
                purchase.print_url = data.get('url')
                purchase.save()
                return True
            except:
                Warning.objects.create(
                    text="N??o conseguiu imprimir as etiquetas",
                    description=f"status da resposta:{response.status_code}, resposta:{response.content}",
                    solution=f"Verificar Compra: #{purchase_id}",
                    data=data
                )
                return False

    @staticmethod
    def get_jadlog_agencies():
        sender = Sender.objects.first()
        if not sender:
            Warning.objects.create(
                text="Nenhum remetente cadastrado",
                solution=f"Favor referir a documenta????o para mais informa????es",
            )
            return False

        response = requests.get(f"{MELHORENVIO_URL}/api/v2/me/shipment/agencies/?company={JADLOG_ID}")
        if response.ok:
            try:
                data = response.json()
                fields = 'id', 'name', 'status',
                agencies = []
                for agency in data:
                    agency_data = {
                        'address': agency.get('address',{}).get('address'),
                        'district': agency.get('address',{}).get('district'),
                        'city': agency.get('address',{}).get('city',{}).get('city'),
                        
                        **{f: agency.get(f) for f in fields},
                    }
                    if 'rio de janeiro' in agency_data.get('city','').lower():
                        agencies.append(agency_data)
                        
                sender.jadlog_agency_options = agencies
                sender.update_jadlog_options = False
                sender.save()
                return True
            except Exception as e:
                pass
        Warning.objects.create(
            text="N??o foi poss??vel obter as ag??ncias do JadLog",
            description=f"status da resposta:{response.status_code}, resposta:{response.content}",
            solution=f"Verificar se o JadLog est?? ativo e se o c??digo da ag??ncia ?? {JADLOG_ID}",
        )
