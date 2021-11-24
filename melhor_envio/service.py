import json

import requests
from clubinho_preto.settings import (MELHORENVIO_CLIENT_ID, MELHORENVIO_SECRET,
                                     MELHORENVIO_URL, MELHORENVIO_REDIRECT_URL)
from django.core.cache import cache

MELHORENVIO_CACHE_TIME = 2592000


def save_token_to_cache(data):
    cache.set("access_token", data.get("access_token"), MELHORENVIO_CACHE_TIME)
    cache.set("refresh_token", data.get("refresh_token"), MELHORENVIO_CACHE_TIME*2)


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
