import os
from celery.schedules import crontab
from celery import Celery
from account.tasks import account_task

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubinho_preto.settings')
app = Celery('celery_app')
# Using a string here means the worker will not have to pickle the object when using Windows, namespace='CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_transport_options = {'visibility_timeout': 3600}


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.add_periodic_task(
        crontab(minute=0, hour='*/12'),
        task_import_subscriptions.s(),
    )

    sender.add_periodic_task(
        crontab(minute=30, hour='*/12'),
        task_update_subscriptions.s(),
    )


@app.task
def task_import_subscriptions():
    from finance.service import FinanceService
    created, errors = FinanceService.import_asaas_subscriptions()
    return f'{created} assinaturas criadas, {errors} erros'

@app.task
def task_update_subscriptions():
    from finance.service import FinanceService
    updated, errors = FinanceService.update_asaas_subscriptions()
    return f'{updated} assinaturas atualizadas, {errors} erros'
