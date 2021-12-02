"""clubinho_preto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from clubinho_preto import settings
from django.conf.urls.static import static
from finance.views import SubscribeView
from melhor_envio.views import AuthorizeApplicationView, GetTokenView, RefreshTokenView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('subscribe', SubscribeView.as_view(), name='subscribe'),
    path('authorize_application', AuthorizeApplicationView.as_view(), name='authorize_application'),
    path('refresh_token', RefreshTokenView.as_view(), name='refresh_token'),
    path('get_token', GetTokenView.as_view(), name='get_token'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
