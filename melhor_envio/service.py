from clubinho_preto.settings import (MELHORENVIO_CLIENT_ID,
                                     MELHORENVIO_REDIRECT_URL,
                                     MELHORENVIO_SECRET, MELHORENVIO_URL)
import requests
from django.core.cache import cache
import json

class MelhorEnvioService():

    @staticmethod
    def get_token():
        token = cache.get("access_token")
        if token:
            return token
        else:
            # todo: check refresh token
            # todo: check refresh token expiration on cache and increase
            # todo: if not refresh_token: reauthenticate
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
