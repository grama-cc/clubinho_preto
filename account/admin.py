import os
from django.contrib import admin, messages
from openpyxl import load_workbook
from .models import Subscriber, Sender
from django.contrib.admin import register


def get_cell(sheet, column, row):
    value = sheet["{}{}".format(str(column), str(row))].value
    if type(value) == str:
        return value.strip()
    return value


@register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email', 'relatedness_raw', 'kids_race_raw',)
    list_display = ('id', 'name', 'email', 'cep', 'relatedness', 'kids_race', 'asaas_customer_id')
    ordering = ('name',)
    actions = 'importar_planilha', 'import_subscribers',

    def importar_planilha(modeladmin, request, queryset):
        path = 'account/data/info.xlsx'
        if os.path.exists(path):
            workbook = spreadsheet = load_workbook('account/data/info.xlsx', data_only=True)
            sheet = workbook.active
            count = 0
            errors = 0
            row = 2

            for i in range(1120):
                data = {
                    "subscribing_date": get_cell(sheet, 'A', row),
                    "name": get_cell(sheet, 'C', row),
                    "email": get_cell(sheet, 'B', row),
                    "relatedness_raw": get_cell(sheet, 'D', row),
                    "phone": get_cell(sheet, 'F', row),
                    "kids_age": int(get_cell(sheet, 'G', row).replace('especial', '0').replace(' anos', '').replace(' ano', '').replace('4 e 6', '6')),
                    "kids_race_raw": get_cell(sheet, 'H', row),
                    "address": get_cell(sheet, 'I', row),
                    "cep": get_cell(sheet, 'J', row),
                    "more_info": get_cell(sheet, 'K', row),
                }

                if data["email"]:
                    try:
                        Subscriber.objects.create(**data)
                        count += 1
                    except Exception as e:
                        print(e)
                        errors += 1
                    finally:
                        row += 1
                else:
                    break
            messages.success(request, f'Foram importados {count} assinantes. Houveram {errors} erros')
            return
        messages.warning(request, f'O arquivo `{path}` não existe')

    def import_subscribers(modeladmin, request, queryset):
        from account.service import AccountService
        created, errors, skipped = AccountService.import_asaas_customers()

        modeladmin.message_user(request, f'{created} assinantes criadas, {errors} erros, {skipped} já existiam')

    import_subscribers.short_description = 'Importar assinantes Asaas'


@register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = "name", "phone", "email", "address",

    fieldsets = (
        ("Informações Gerais",
         {"fields": ("name", "phone", "email", )}),

        ("Documentos",
         {"fields": ("document", "company_document", "state_register")}),

        ("Endereço",
         {"fields": ("address", "complement", "number", "district", "city", "country_id", "postal_code", )}),

        (None,
         {"fields": ("note",)}),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
