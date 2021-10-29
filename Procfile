
web: gunicorn clubinho_preto.wsgi --timeout 120 --keep-alive 5
celery: celery -A celery_app worker -B -l INFO