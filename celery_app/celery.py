import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubinho_preto.settings')
app = Celery('celery_app')
# Using a string here means the worker will not have to pickle the object when using Windows, namespace='CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_transport_options = {'visibility_timeout': 3600}


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        clear_old_warnings.s(),
    )

    sender.add_periodic_task(
        crontab(minute=0, hour='*/12'),
        task_import_asaas_customers.s(),
    )

    sender.add_periodic_task(
        crontab(minute=10, hour='*/1'),
        task_update_subscriptions.s(),
    )

    sender.add_periodic_task(
        crontab(minute=20, hour='*/1'),
        task_import_subscriptions.s(),
    )

    sender.add_periodic_task(
        crontab(minute=40, hour='*/1'),
        task_update_payment_history.s(),
    )

    sender.add_periodic_task(
        crontab(minute=5, hour=0),
        task_get_jadlog_agencies.s(),
    )


@app.task
def task_import_spreadsheet():
    from account.tasks import importar_planilha
    return importar_planilha()


@app.task
def task_import_subscriptions(_=None):
    from finance.service import FinanceService
    created, errors = FinanceService.import_asaas_subscriptions()
    return f'{created} assinaturas criadas, {errors} erros'


@app.task
def task_update_subscriptions(_=None):
    from finance.service import FinanceService
    updated, errors = FinanceService.update_asaas_subscriptions()
    return f'{updated} assinaturas atualizadas, {errors} erros'


@app.task
def task_import_asaas_customers(_=None):
    from account.service import AccountService
    created, errors, skipped = AccountService.import_asaas_customers()
    return f'{created} clientes criados, {errors} erros'


@app.task
def task_create_shipping_options(shipping_ids):
    from box.tasks import create_shipping_options
    return create_shipping_options(shipping_ids)


@app.task
def task_add_deliveries_to_cart(shipping_ids):
    from box.tasks import add_deliveries_to_cart
    return add_deliveries_to_cart(shipping_ids)


@app.task
def task_cart_checkout(label_ids):
    from melhor_envio.service import MelhorEnvioService
    return MelhorEnvioService.cart_checkout(label_ids)


@app.task
def task_print_labels(purchase_id):
    from melhor_envio.service import MelhorEnvioService
    return MelhorEnvioService.print_labels(purchase_id)


@app.task
def task_get_jadlog_agencies():
    from melhor_envio.service import MelhorEnvioService
    return MelhorEnvioService.get_jadlog_agencies()


@app.task
def task_update_payment_history(_=None):
    from finance.service import FinanceService
    return FinanceService.update_payment_history()


@app.task
def clear_old_warnings():
    from datetime import timedelta

    from account.models import Warning
    from django.utils import timezone
    _7_days_ago = timezone.now() - timedelta(days=7)
    Warning.objects.filter(created_at__lt=_7_days_ago).delete()
