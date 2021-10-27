from datetime import datetime


def account_task():
    print(f'Celery task says it\'s {datetime.now()}')
