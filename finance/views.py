import json

from account.service import AccountService
from django.http import response
from django.shortcuts import render
from django.views import View
from finance.models import DELIVERY_CHOICES
from finance.service import FinanceService
# Create your views here.


class SubscribeView(View):

    def get(self, request):
        # return render(request, 'success.html', {'email':"fulano@gmail.com"})
        return render(request, 'subscription.html', {'delivery_options': DELIVERY_CHOICES.items()})

    def post(self, request):
        data = {}
        for key in ["email", "name", "cpfCnpj", "relatedness", "relatedness_raw", "phone", "kids_name",
                    "kids_age", "kids_gender_raw", "address", "postalCode", "more_info"]:
            data[key] = request.POST.get(key)

        # Handle required delivery field
        delivery_choice = request.POST.get('delivery', None)
        if not delivery_choice or DELIVERY_CHOICES.get(delivery_choice) is None:
            return render(request, 'subscription.html', {'error_message': 'É preciso escolher uma opção de frete válida'})
        delivery_choice = DELIVERY_CHOICES.get(delivery_choice)

        # print(f'delivery ok {delivery_choice}')
        asaas_response, subscriber = AccountService.create_asaas_customer(data)
        # At this point you may or may not have a Subscriber instance, if not, an email has been sent to the application admins
        # print(f'asaas_response ok {asaas_response.content}')
        # print(f'subscriber {subscriber}')

        if asaas_response.ok:
            # Create payment request (in Asaas) and send paymentLink to user
            customer_id = asaas_response.json().get('id')
            payment_response = FinanceService.create_asaas_subscription(customer_id, delivery_choice)
            # print(f'payment_response {payment_response}')

            if payment_response and payment_response.get('id'):

                context = {'email': subscriber.email if subscriber else None}
                return render(request, 'success.html', context)

            else:
                # Return to form with error message
                return render(request, 'subscription.html', {'error_message': "Ocorreu um erro ao criar a assinatura. Por favor entre em contato ou tente novamente mais tarde"})
        else:
            # todo: send mail? or create Form error model
            message = json.loads(
                asaas_response.content) if asaas_response.content else 'Ocorreu um erro interno. Por favor entre em contato'
            if message and message.get('errors'):
                errors = [error.get('description') for error in message.get('errors')]
                message = '\n'.join(errors)
            return render(request, 'subscription.html', {'error_message': str(message)})
