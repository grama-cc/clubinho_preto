from django.contrib import admin
from django.core.checks import messages

# Register your models here.
from .models import Box, BoxItem, Shipping, ShippingOption
from account.models import Subscriber
from django.utils import timezone
from celery_app.celery import task_create_shipping_options


class BoxItemAdmin(admin.ModelAdmin):
    list_display = "name", "description"


class BoxAdmin(admin.ModelAdmin):
    list_display = "id", "name", "description", "width", "height", "length", "weight", "insurance_value",
    search_fields = "name", "description",
    filter_horizontal = "items",
    actions = 'create_this_month_shippings',

    def create_this_month_shippings(self, request, queryset):
        shippings = []

        # todo: update this rule
        # All subscribers that don't have shippings for this month
        subscribers = Subscriber.objects.all()\
            .exclude(shippings__date_created__month=timezone.now().month).distinct()

        # todo: make this async task
        for box in queryset:
            for subscriber in subscribers:
                shippings.append(
                    Shipping(
                        box=box,
                        recipient=subscriber
                    )
                )

        try:
            Shipping.objects.bulk_create(shippings)
            ids = [s.id for s in shippings]
            task_create_shipping_options.delay(ids)
            self.message_user(request, f"Foram criados {len(shippings)} envios")
        except Exception as e:
            self.message_user(request, f"Erro ao criar envios - {e}", level=messages.ERROR)

    create_this_month_shippings.short_description = "Criar envios deste mês"


class ShippingItemAdmin(admin.ModelAdmin):
    list_display = "id", "name", "company_name", "price", "delivery_time", "delivery_time_min", "delivery_time_max", "melhor_envio_id",


class ShippingAdmin(admin.ModelAdmin):
    list_display = "id", "box", "recipient", "date_created", "shipping_option_selected",
    list_filter = "recipient", "box", 
    # filter_horizontal = "shipping_options",
    readonly_fields = "date_created",
    actions = 'generate_shipping_options',

    def generate_shipping_options(self, request, queryset):
        from celery_app.celery import task_create_shipping_options
        ids = list(queryset.values_list('id', flat=True))
        task_create_shipping_options.delay(ids)
    
    generate_shipping_options.short_description = "Gerar opções de envio"

admin.site.register(Box, BoxAdmin)
admin.site.register(BoxItem, BoxItemAdmin)
admin.site.register(Shipping, ShippingAdmin)
admin.site.register(ShippingOption, ShippingItemAdmin)
