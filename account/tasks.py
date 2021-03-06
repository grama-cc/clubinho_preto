

def importar_planilha():
    import os
    from openpyxl import load_workbook
    from account.models import Subscriber

    def get_cell(sheet, column, row):
        value = sheet["{}{}".format(str(column), str(row))].value
        if type(value) == str:
            return value.strip()
        return value

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
        return f'Foram importados {count} assinantes. Houveram {errors} erros'
    return f'O arquivo `{path}` não existe'
