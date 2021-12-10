from os import readlink
from django.contrib import admin
from django.core.checks import messages
from .models import Label, Purchase
from django.utils.html import mark_safe  # Newer versions
from celery_app.celery import task_print_labels
# Register your models here.


class LabelInline(admin.StackedInline):
    model = Label
    extra = 0 
    fields = [f.name for f in Label._meta.fields]
    readonly_fields = fields

class PurchaseAdmin(admin.ModelAdmin):
    list_display = 'id', 'created_at', 'total', 'status', 'link', 'labels'
    search_fields = 'label__id',
    actions = 'print_labels',
    ordering = '-created_at',
    inlines = LabelInline,

    def labels(self, obj):
        return mark_safe('<br>'.join([str(label.id) for label in obj.label_set.all()]))
    labels.short_description = 'IDs Etiquetas'

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


# admin.site.register(Label, LabelAdmin)
admin.site.register(Purchase, PurchaseAdmin)
