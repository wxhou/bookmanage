from celery import Celery


celery = Celery('bookmanage')
celery.config_from_object('app.core.celeryconfig')
