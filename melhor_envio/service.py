import json

import requests
from clubinho_preto.settings import (MELHORENVIO_CLIENT_ID, MELHORENVIO_SECRET,
                                     MELHORENVIO_URL, MELHORENVIO_REDIRECT_URL)
from django.core.cache import cache

MELHORENVIO_CACHE_TIME = 2592000


def save_token_to_cache(data):
    cache.set("access_token", data.get("access_token"), MELHORENVIO_CACHE_TIME) # valid for 30 days
    cache.set("refresh_token", data.get("refresh_token"), int(MELHORENVIO_CACHE_TIME*1.5)) # valid for 45 days


class MelhorEnvioService():

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
        bearer_token = MelhorEnvioService.get_token()
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
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
        response = requests.post(
            url=f"{MELHORENVIO_URL}api/v2/me/shipment/calculate",
            headers=headers,
            data=json.dumps(data)
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
        for shipping in shippings:
        
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
                "volumes": [ # Correios only accepts one volume per request
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

                    # todo: NF
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
            

            bearer_token = MelhorEnvioService.get_token()
            headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
            
            response = requests.post(
                url=f"{MELHORENVIO_URL}api/v2/me/cart/",
                headers=headers,
                data=json.dumps(data)
            )

            if response.ok:
                try:
                    label = response.json()
                    shipping.label = label
                    shipping.save()
                    
                except:
                    # Returns html if there is error
                    print(f"1-Não conseguiu adicionar itens no carrinho {response.status_code}")    
            else:
                print(f"2-Não conseguiu adicionar itens no carrinho {response.status_code}")