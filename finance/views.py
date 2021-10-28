from account.models import Subscriber
from django.shortcuts import render
from django.views import View

# Create your views here.


class SubscribeView(View):

    def get(self, request):
        return render(request, 'subscription.html', {'error_message':'Não rolou'})

    def post(self, request):
        data = {}
        for key in ["email", "name", "relatedness", "relatedness_raw", "phone", "kids_name",
                    "kids_age", "kids_gender_raw", "address", "cep", "more_info"]:
            data[key] = request.POST.get(key)

        try:
            Subscriber.objects.create(**data)
            # todo: next step: asaas subscription
            return render(request, 'success.html', {'data': data}) # todo: fill form with wrong data for ease of use
        except Exception as e:
            print(e)
            # todo: improve error message
            return render(request, 'subscription.html', {'error_message':str(e)})
