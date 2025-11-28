web: gunicorn reformeApi.wsgi --log-file -
celery: celery -A reformeApi worker -l info
rqworker: python manage.py rqworker default
