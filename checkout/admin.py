from django.contrib import admin
from django.core.checks import messages
from .models import Label, Purchase
from django.utils.html import mark_safe  # Newer versions
from celery_app.celery import task_print_labels, task_cart_checkout
# Register your models here.


class LabelAdmin(admin.ModelAdmin):
    list_display = 'id', 'price', 'status', 'shipping', 'is_paid'
    actions = 'checkout',

    def is_paid(self, obj):
        return bool(obj.purchase)
    is_paid.boolean = True
    is_paid.short_description = 'Pago?'

    def checkout(self, request, queryset):
        ids = list(queryset.values_list('id', flat=True))
        task_cart_checkout.delay(ids)
        self.message_user(request, f"{len(ids)} etiquetas estão sendo processadas")
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
            task_print_labels.delay(purchase.id)
        self.message_user(request, f"{len(queryset)} compras estão sendo processadas")

        Purchase.objects.bulk_update(queryset, ['print_url'])
    print_labels.short_description = 'Imprimir etiquetas'


admin.site.register(Label, LabelAdmin)
admin.site.register(Purchase, PurchaseAdmin)
