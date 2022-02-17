from clubinho_preto.settings import (MELHORENVIO_CLIENT_ID,
                                     MELHORENVIO_REDIRECT_URL, MELHORENVIO_URL)
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View

from melhor_envio.service import MelhorEnvioService


class AuthorizeApplicationView(View):
    def get(self, request):
        return redirect(
            f"{MELHORENVIO_URL}/oauth/authorize?client_id={MELHORENVIO_CLIENT_ID}&redirect_uri={MELHORENVIO_REDIRECT_URL}&response_type=code&state=teste&scope=cart-read cart-write companies-read companies-write coupons-read coupons-write notifications-read orders-read products-read products-write purchases-read shipping-calculate shipping-cancel shipping-checkout shipping-companies shipping-generate shipping-preview shipping-print shipping-share shipping-tracking ecommerce-shipping transactions-read users-read users-write"
        )


class GetTokenView(View):
    def get(self, request):
        code = request.GET.get("code", None)
        response = MelhorEnvioService.set_access_token(code=code)
        return HttpResponse(
            content=response.content, status=response.status_code, content_type=response.headers["Content-Type"]
        )


class RefreshTokenView(View):
    def get(self, request):
        refresh_token = request.GET.get("refresh_token", None)
        response = MelhorEnvioService.set_refresh_token(refresh_token)
        return HttpResponse(
            content=response.content, status=response.status_code, content_type=response.headers["Content-Type"]
        )
