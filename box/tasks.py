
def create_shipping_options(shipping_ids):
    """
    Get available shipping options for a list of shipping ids
    Uses Melhor Envio API
    Also saves the cheapest shipping option as the selected one
    """

    from melhor_envio.service import MelhorEnvioService

    from account.models import Sender
    from box.models import Shipping, ShippingOption
    shipping_from = None
    sender = Sender.objects.first()
    if sender:
        shipping_from = sender.postal_code
    shippings = Shipping.objects.filter(id__in=shipping_ids).exclude(recipient__cep__isnull=True)
    for shipping in shippings:

        shipping_options = MelhorEnvioService.get_shipping_options(
            shipping=shipping,
            postal_from=shipping_from
        )

        if shipping_options:
            create_list = []
            fields = "name", "price", "delivery_time"
            for shipping_info in shipping_options:

                # Ignore "Azul Cargo" company as it does not generate labels via API
                if 'azul cargo' in shipping_info.get('name', '').lower():
                    pass

                # Get data with same key
                data = {field: shipping_info.get(field, None) for field in fields}
                shipping_option = ShippingOption(
                    **data,
                    melhor_envio_id=shipping_info.get("id", None),
                    company_name=shipping_info.get("company", {}).get("name", None),
                    delivery_time_min=shipping_info.get("delivery_range", {}).get("min", None),
                    delivery_time_max=shipping_info.get("delivery_range", {}).get("max", None),
                )
                create_list.append(shipping_option)
                    
                
            try:
                ShippingOption.objects.bulk_create(create_list)
            except Exception as e:
                print(f"ERROR - {e}")
                pass

            # Save options to shipping
            ids = [item.id for item in create_list]
            shipping.shipping_options.set(ids)

            # Save cheapest option as selected option
            cheapest_shipping = shipping.shipping_options.filter(price__isnull=False).order_by('price').first()
            shipping.shipping_option_selected = cheapest_shipping

            shipping.save()
        else:
            print(f"Não foram encontradas opções de entrega para o Envio #{shipping.id}.")


def add_deliveries_to_cart(shipping_ids):
    from account.models import Sender, Warning
    from melhor_envio.service import MelhorEnvioService

    from box.models.shipping import Shipping
    
    # todo: check if recipient is valid (has all fields)

    # Select first sender
    sender = Sender.objects.all().order_by('id').values()[0]
    shippings = Shipping.objects.filter(
        id__in=shipping_ids,
        shipping_option_selected__isnull=False,
        box__isnull=False,
        recipient__isnull=False,
        label__isnull=True
    )
    if shippings and sender:
        return MelhorEnvioService.add_items_to_cart(shippings, sender)

    elif not sender:
        Warning.objects.create(
                text="Não há um remetente para criar os envios.",
                solution=f"Criar um novo remetente. Veja a documentação do projeto (README.md) para mais informações."
            )
        return []
    elif not shippings:
        Warning.objects.create(
                text="Não há envios válidos para gerar etiquetas.",
                description="Para gerar as etiquetas, os envios precisam: ter uma opção de frete selecionada, ter uma caixa, um assinante e não possuir uma etiqueta.",
                solution=f"Caso o envio já possua uma etiqueta, use a ação 'Limpar etiquetas' do Admin 'Envios'"
            )
        return []
