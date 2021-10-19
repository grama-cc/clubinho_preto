from django.contrib import admin
from django.contrib.admin import register
from .models import Subscription, PaymentHistory


class PaymentHistoryInlineAdmin(admin.TabularInline):
    model = PaymentHistory

@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id','date', 'subscriber', 'value', 'status')
    filter = ('status')
    inlines = (PaymentHistoryInlineAdmin,)