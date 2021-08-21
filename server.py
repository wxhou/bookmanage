from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from dotenv import load_dotenv
from app import create_app
from settings.base import BASE_DIR
from settings import celeryconfig


def make_celery(app_name):

    celery = Celery(
        app_name,
        broker=celeryconfig.broker_url,
        backend=celeryconfig.result_backend
    )
    celery.config_from_object(celeryconfig)
    return celery


env_file = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_file):
    load_dotenv(env_file)


my_celery = make_celery(__name__)
app = create_app(celery=my_celery)
