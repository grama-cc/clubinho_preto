import requests
from clubinho_preto.settings import (MELHORENVIO_CLIENT_ID,
                                     MELHORENVIO_REDIRECT_URL,
                                     MELHORENVIO_SECRET, MELHORENVIO_URL)
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View

MELHORENVIO_CACHE_TIME = 2592000


def save_token_to_cache(data):
    cache.set("access_token", data.get("access_token"), MELHORENVIO_CACHE_TIME)
    cache.set("refresh_token", data.get("refresh_token"), MELHORENVIO_CACHE_TIME)


class AuthorizeApplicationView(View):
    def get(self, request):
        return redirect(
            f"{MELHORENVIO_URL}/oauth/authorize?client_id={MELHORENVIO_CLIENT_ID}&redirect_uri={MELHORENVIO_REDIRECT_URL}&response_type=code&state=teste&scope=cart-read cart-write companies-read companies-write coupons-read coupons-write notifications-read orders-read products-read products-write purchases-read shipping-calculate shipping-cancel shipping-checkout shipping-companies shipping-generate shipping-preview shipping-print shipping-share shipping-tracking ecommerce-shipping transactions-read users-read users-write"
        )


class GetTokenView(View):
    def get(self, request):
        code = request.GET.get("code", None)

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

        return HttpResponse(
            content=response.content, status=response.status_code, content_type=response.headers["Content-Type"]
        )


class RefreshTokenView(View):
    def get(self, request):
        refresh_token = request.GET.get("refresh_token", None)

        response = requests.post(
            f"{MELHORENVIO_URL}/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": {MELHORENVIO_CLIENT_ID},
                "client_secret": {MELHORENVIO_SECRET},
                "refresh_token": {refresh_token},
            },
        )

        if response.ok:
            # save tokens to cache
            data = response.json()
            save_token_to_cache(data)

        return HttpResponse(
            content=response.content, status=response.status_code, content_type=response.headers["Content-Type"]
        )
