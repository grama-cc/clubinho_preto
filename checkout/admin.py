from django.contrib import admin
from django.core.checks import messages
from .models import Label, Purchase
from django.utils.html import mark_safe  # Newer versions

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
    list_display = 'id', 'total', 'status', 'link'
    actions = 'print_labels',

    def link(self, obj):
        if obj.print_url:
            return mark_safe(f'<a href="{obj.print_url}" target="_blank">link</a>')
        return '-'

    def print_labels(self, request, queryset):
        for purchase in queryset:
            from melhor_envio.service import MelhorEnvioService
            ids = list(purchase.label_set.values_list('id', flat=True))
            if ids:
                response = MelhorEnvioService.print_labels(ids)
                if response and response.get('url'):
                    purchase.print_url = response.get('url')
                    
        Purchase.objects.bulk_update(queryset,['print_url'])
    print_labels.short_description = 'Imprimir etiquetas'


admin.site.register(Label, LabelAdmin)
admin.site.register(Purchase, PurchaseAdmin)
