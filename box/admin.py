from account.models import Sender, Subscriber
from celery_app.celery import task_cart_checkout, task_create_shipping_options
from django.contrib import admin
from django.core.checks import messages
from django.db.models import F
from django.utils import timezone

# Register your models here.
from .models import Box, BoxItem, Shipping, ShippingOption
from checkout.models import Label


class BoxItemAdmin(admin.ModelAdmin):
    list_display = "name", "description"


class BoxAdmin(admin.ModelAdmin):
    list_display = "id", "name", "description", "width", "height", "length", "weight", "insurance_value",
    search_fields = "name", "description",
    filter_horizontal = "items",
    actions = 'create_this_month_shippings',

    def create_this_month_shippings(self, request, queryset):
        shippings = []

        # All subscribers that don't have shippings for this month 
        # and have paid this months subscription charge
        subscribers = Subscriber.objects.allowed_shipping()

        # todo: make this async task
        for box in queryset:
            for subscriber in subscribers:
                if subscriber.can_send_package():  # Remove subscribers that don't have full address info
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


class ShippingOptionAdmin(admin.ModelAdmin):
    list_display = "id", "name", "company_name", "price", "delivery_time", "delivery_time_min", "delivery_time_max", "melhor_envio_id",


class ShippingAdmin(admin.ModelAdmin):
    list_display = "id", "box", "recipient", "city", "province", "date_created", "shipping_option_selected", "user_ok", "has_label",
    list_filter = "box", "recipient",  # todo: filter by has label
    # filter_horizontal = "shipping_options",
    readonly_fields = "date_created", "label",
    actions = 'generate_shipping_options', 'generate_labels', 'clear_labels', 'checkout'

    # Limit foreign key choices based on another field from the instance
    def get_form(self, request, obj=None, **kwargs):
        form = super(ShippingAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['shipping_options'].queryset = obj.shipping_options.all()
            form.base_fields['shipping_option_selected'].queryset = obj.shipping_options.all()
        return form


    def get_queryset(self, request):
        return super().get_queryset(request)\
            .select_related('box', 'recipient')\
            .annotate(
                city=F('recipient__city'),
                province=F('recipient__province'),
        )

    def city(self, obj):
        return obj.city
    city.short_description = "Cidade"

    def province(self, obj):
        return obj.province
    province.short_description = "Bairro"

    def user_ok(self, obj):
        if obj.recipient:
            return obj.recipient.can_send_package()
        return False
    user_ok.boolean = True
    user_ok.short_description = "Usuário ok?"

    def has_label(self, obj):
        return hasattr(obj, 'label')
    has_label.boolean = True
    has_label.short_description = "Etiqueta"

    def generate_shipping_options(self, request, queryset):
        from celery_app.celery import task_create_shipping_options

        if not Sender.objects.count():
            self.message_user(
                request, "É preciso criar um Remetente primeiro. veja como no README do projeto", level=messages.WARNING)
            return

        ids = list(queryset.values_list('id', flat=True))
        task_create_shipping_options.delay(ids)
    generate_shipping_options.short_description = "Gerar opções de envio"

    def generate_labels(self, request, queryset):
        from celery_app.celery import task_add_deliveries_to_cart
        task_add_deliveries_to_cart.delay([s.id for s in queryset])
        total = sum([getattr(s.shipping_option_selected, 'price', 0) for s in queryset])
        self.message_user(request, f"{len(queryset)} etiquetas estão sendo geradas. Isso pode demorar um pouco. O valor total delas é: R${round(total,2)}")
    generate_labels.short_description = "Gerar etiquetas"

    def clear_labels(self, request, queryset):
        from checkout.models import Label
        count, _ = Label.objects.filter(shipping__in=queryset).delete()
        self.message_user(request, f"{count} etiquetas foram apagadas.")
    clear_labels.short_description = "Limpar etiquetas"

    def checkout(self, request, queryset):
        labels = Label.objects.filter(shipping__in=queryset).values('id', 'price')
        ids = [l['id'] for l in labels]
        task_cart_checkout.delay(ids)
        total = sum([l['price'] for l in labels])
        self.message_user(request, f"{len(ids)} etiquetas estão sendo processadas. O valor total delas é: R${round(total,2)}")
    checkout.short_description = 'Comprar etiquetas'


admin.site.register(Box, BoxAdmin)
admin.site.register(BoxItem, BoxItemAdmin)
admin.site.register(Shipping, ShippingAdmin)
# admin.site.register(ShippingOption, ShippingOptionAdmin)
