from django.contrib import admin

# Register your models here.
from .models import Box, BoxItem, Shipping, ShippingOption


class BoxItemAdmin(admin.ModelAdmin):
    list_display = "name", "description"


class BoxAdmin(admin.ModelAdmin):
    list_display = "id", "name", "description", "width", "height", "length", "weight",
    search_fields = "name", "description",
    filter_horizontal = "items",


class ShippingItemAdmin(admin.ModelAdmin):
    list_display = "id", "name", "company_name", "price", "delivery_time", "delivery_time_min", "delivery_time_max", "melhor_envio_id",


class ShippingAdmin(admin.ModelAdmin):
    list_display = "id", "box", "date_created", "shipping_option_selected", "insurance_value", "recipient", "processado"
    list_filter = "recipient", "box", "shipping_option_selected",
    filter_horizontal = "shipping_options",
    readonly_fields = "date_created",
    

    def processado(self, obj):
        return obj.processed

    processado.boolean = True


admin.site.register(Box, BoxAdmin)
admin.site.register(BoxItem, BoxItemAdmin)
admin.site.register(Shipping, ShippingAdmin)
admin.site.register(ShippingOption, ShippingItemAdmin)
