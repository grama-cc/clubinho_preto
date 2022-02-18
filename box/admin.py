from account.models import Sender, Subscriber
from celery import chain
from celery_app.celery import task_cart_checkout, task_create_shipping_options
from checkout.models import Label
from checkout.models.purchase import Purchase
from django.contrib import admin
from django.core.checks import messages
from django.db.models import F
from django.db.models.expressions import OuterRef, Subquery
from django.utils.html import mark_safe  # Newer versions

from .models import Box, BoxItem, Shipping


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
            if len(ids):
                task_create_shipping_options.delay(ids)
                self.message_user(request, f"Foram criados {len(ids)} envios")
            else:
                self.message_user(request, f"Não há assinantes aptos a receber envios", messages.WARNING)
        except Exception as e:
            self.message_user(request, f"Erro ao criar envios - {e}", level=messages.ERROR)

    create_this_month_shippings.short_description = "Criar envios deste mês"


class ShippingOptionAdmin(admin.ModelAdmin):
    list_display = "id", "name", "company_name", "price", "delivery_time", "delivery_time_min", "delivery_time_max", "melhor_envio_id",


class ShippingAdmin(admin.ModelAdmin):
    list_display = "id", "box", "recipient", "destination", "date_created", "shipping_option_selected", "user_ok", "has_label", "label_link",
    list_filter = "box", "recipient",
    readonly_fields = "date_created", "label",
    actions = 'generate_shipping_options', 'process_all_shippings', 'clear_labels',

    # Limit foreign key choices based on another field from the instance
    def get_form(self, request, obj=None, **kwargs):
        form = super(ShippingAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['shipping_options'].queryset = obj.shipping_options.all()
            form.base_fields['shipping_option_selected'].queryset = obj.shipping_options.all()
        return form


    def get_queryset(self, request):
        # Annotate label pdf link for ease of use
        label_purchase_link = Subquery(Purchase.objects.filter(
            label__shipping=OuterRef("id"),
        ).order_by("-created_at").values('print_url')[:1])

        return super().get_queryset(request)\
            .select_related('box', 'recipient', 'shipping_option_selected', 'label')\
            .prefetch_related('shipping_options')\
            .annotate(
                label_link=label_purchase_link,
                city=F('recipient__city'),
                province=F('recipient__province'),
        )

    #  region Fields
    def destination(self, obj):
        return ' - '.join([obj.city, obj.province])
    destination.short_description = "Cidade / Bairro"

    def user_ok(self, obj):
        if obj.recipient:
            return obj.recipient.can_send_package()
        return False
    user_ok.boolean = True
    user_ok.short_description = "Usuário ok?"

    def has_label(self, obj):
        return hasattr(obj, 'label')
    has_label.boolean = True
    has_label.short_description = "Tem Etiqueta"

    def label_link(self, obj):
        if obj.label_link:
            return mark_safe(f'<a href="{obj.label_link}" target="_blank">link da etiqueta</a>')
    label_link.short_description = "Link Etiqueta"

    # endregion Fields

    # region Actons
    def generate_shipping_options(self, request, queryset):
        from celery_app.celery import task_create_shipping_options

        if not Sender.objects.count():
            self.message_user(
                request, "É preciso criar um Remetente primeiro. veja como no README do projeto", level=messages.WARNING)
            return

        ids = list(queryset.values_list('id', flat=True))
        task_create_shipping_options.delay(ids)
        self.message_user(request, f"{len(ids)} envios estão sendo gerados. Isso pode demorar um pouco. Por favor atualize a página para ver os resultados.")
    generate_shipping_options.short_description = "Gerar opções de envio"
    
    def clear_labels(self, request, queryset):
        from checkout.models import Label
        count, _ = Label.objects.filter(shipping__in=queryset).delete()
        self.message_user(request, f"{count} etiquetas foram apagadas.")
    clear_labels.short_description = "Limpar etiquetas"
    
    def process_all_shippings(self, request, queryset):
        from celery_app.celery import task_add_deliveries_to_cart

        # Do not regenerate labels if there is a label
        queryset = queryset.filter(label__isnull=True)
        if queryset:
            labels_total_price = sum([getattr(s.shipping_option_selected, 'price', 0) for s in queryset])
            # label_ids = list(Label.objects.filter(shipping__in=queryset.filter(label__isnull=True)).values_list('id', flat=True))
            
            chain(
                task_add_deliveries_to_cart.s([s.id for s in queryset]),
                task_cart_checkout.s()
            )().get()
            
            self.message_user(request, f"Gerando {len(queryset)} etiquetas. O valor total delas é: R${round(labels_total_price,2)}")
        else:
            self.message_user(request, f"Não há envios sem etiquetas para serem geradas.", level=messages.WARNING)
    process_all_shippings.short_description = "Processar todos os envios"


admin.site.register(Box, BoxAdmin)
admin.site.register(BoxItem, BoxItemAdmin)
admin.site.register(Shipping, ShippingAdmin)
# admin.site.register(ShippingOption, ShippingOptionAdmin)
