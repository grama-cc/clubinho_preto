
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
            postal_from=shipping_from,
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

                # TODO: Ignore "Azul Cargo" company as it does not generate labels via API

                data = {field: shipping_info.get(field, None) for field in fields}

                try:
                    shipping_option = ShippingOption.objects.create(
                        **data,
                        melhor_envio_id=shipping_info.get("id", None),
                        company_name=shipping_info.get("company", {}).get("name", None),
                        delivery_time_min=shipping_info.get("delivery_range", {}).get("min", None),
                        delivery_time_max=shipping_info.get("delivery_range", {}).get("max", None),
                    )
                    create_list.append(shipping_option)
                    
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


def add_deliveries_to_cart(shipping_ids):
    import json
    from datetime import datetime

    from account.models import Sender
    from melhor_envio.service import MelhorEnvioService

    from box.models.shipping import Shipping
    
    # todo: check if recipient is valid (has all fields)

    # Select first sender
    sender = Sender.objects.all().order_by('id').values()[0]
    shippings = Shipping.objects.filter(
        id__in=shipping_ids,
        shipping_option_selected__isnull=False,
        box__isnull=False,
        recipient__isnull=False
    )
    if shippings and sender:
        return MelhorEnvioService.add_items_to_cart(shippings, sender)
        
            
    elif not sender:
        return "Missing Sender"
    elif not shippings:
        return "Missing Shippings"


def checkout_cart():
    """
    Checkout MelhorEnvio cart.
    After this comes the label generation step
    """

    pass


def generate_labels(labels_ids):
    pass
