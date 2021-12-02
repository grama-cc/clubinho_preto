from django.contrib import admin
from django.core.checks import messages
from .models import Label, Purchase
# Register your models here.

class LabelAdmin(admin.ModelAdmin):
    list_display = 'id', 'price', 'status', 'shipping', 'is_paid'
    actions = 'checkout',

    def is_paid(self, obj):
        return bool(obj.purchase)
    is_paid.boolean = True
    is_paid.short_description = 'Pago?'

    def checkout(self, request, queryset):
        from melhor_envio.service import MelhorEnvioService
        ids = list(queryset.values_list('id', flat=True))
        # todo: make this call async
        count = MelhorEnvioService.cart_checkout(ids)
        if count:
            self.message_user(request, f"{count} etiquetas compradas com sucesso")
        else:
            self.message_user(request, f"Ocorreu um erro", level=messages.ERROR)
    checkout.short_description = 'Comprar etiquetas'        

class PurchaseAdmin(admin.ModelAdmin):
    list_display = 'id', 'total', 'status'

admin.site.register(Label, LabelAdmin)
admin.site.register(Purchase, PurchaseAdmin)