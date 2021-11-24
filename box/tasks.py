
def create_shipping_options(shipping_ids):
    """
    Get available shipping options for a list of shipping ids
    Uses Melhor Envio API
    Also saves the cheapest shipping option as the selected one
    """

    from box.models import Shipping, ShippingOption
    from melhor_envio.service import MelhorEnvioService
    from clubinho_preto.settings import MELHORENVIO_SHIPPING_FROM

    shippings = Shipping.objects.filter(id__in=shipping_ids).exclude(recipient__cep__isnull=True)
    for shipping in shippings:

        shipping_options = MelhorEnvioService.get_shipping_options(
            postal_from=MELHORENVIO_SHIPPING_FROM,
            postal_to=shipping.recipient.cep,

            height=shipping.box.height,
            width=shipping.box.width,
            length=shipping.box.length,
            weight=shipping.box.weight,

            insurance_value=shipping.box.insurance_value,
            receipt=shipping.box.receipt,
            own_hand=shipping.box.own_hand
        )

        if shipping_options:
            create_list = []
            fields = "name", "price", "delivery_time", "id"
            for shipping_info in shipping_options:
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
                    shipping_option.save()
                    # ShippingOption.objects.bulk_create(create_list)
                except Exception as e:
                    raise e  # todo

            # Save options to shipping
            ids = [item.id for item in create_list]
            shipping.shipping_options.set(ids)

            # Save cheapest option as selected option
            cheapest_shipping = shipping.shipping_options.filter(price__isnull=False).order_by('price').first()
            shipping.shipping_option_selected = cheapest_shipping

            shipping.save()
        else:
            # todo
            pass
