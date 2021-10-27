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
        crontab(),
        task_account_task.s(),
    )


@app.task
def task_account_task():
    return account_task()
