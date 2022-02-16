import json

from account.service import AccountService
from django.http import response
from django.shortcuts import render
from django.views import View
from finance.models import DELIVERY_CHOICES
from finance.service import FinanceService
from celery_app.celery import task_import_subscriptions
# Create your views here.


class SubscribeView(View):

    def get(self, request):
        # return render(request, 'success.html', {'email':"fulano@gmail.com"})
        return render(request, 'subscription.html', {'delivery_options': DELIVERY_CHOICES.items()})

    def post(self, request):

        # Handle required delivery field
        delivery_choice = request.POST.get('delivery', None)
        if not delivery_choice or DELIVERY_CHOICES.get(delivery_choice) is None:
            return render(request, 'subscription.html', {
                'error_message': 'É preciso escolher uma opção de frete válida',
                'delivery_options': DELIVERY_CHOICES.items()
                })
        delivery_choice = DELIVERY_CHOICES.get(delivery_choice)

        asaas_response, subscriber = AccountService.create_asaas_customer(request.POST)
        # At this point you may or may not have a Subscriber instance, if not, an email has been sent to the application admins

        if asaas_response.ok:
            # Create Asaas subscription
            customer_id = asaas_response.json().get('id')
            payment_response = FinanceService.create_asaas_subscription(customer_id, delivery_choice)

            if payment_response and payment_response.get('id'):
                # Import recenetly created subscription
                task_import_subscriptions.delay()
                
                # return success page
                context = {'email': subscriber.email if subscriber else None}
                return render(request, 'success.html', context)

            else:
                # Return to form with error message
                return render(request, 'subscription.html', {
                    'error_message': 'Ocorreu um erro ao criar a assinatura. Por favor entre em contato ou tente novamente mais tarde',
                    'delivery_options': DELIVERY_CHOICES.items()
                    })
        else:
            # todo: send mail? or create Form error model
            message = json.loads(
                asaas_response.content) if asaas_response.content else 'Ocorreu um erro interno. Por favor entre em contato'
            if message and type(message) == dict and message.get('errors'):
                errors = [error.get('description') for error in message.get('errors')]
                message = '\n'.join(errors)
            return render(request, 'subscription.html', {
                'error_message': str(message),
                'delivery_options': DELIVERY_CHOICES.items()
            })
