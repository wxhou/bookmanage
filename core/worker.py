from celery import Celery
from celery.exceptions import CeleryError
from core import create_app


def celery_app(app):
    celery = Celery(app.import_name,
                    broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    if not app.config.get('APP_DIR'):
        raise CeleryError("no app registered, please set app.config['APP_DIR]")
    celery.autodiscover_tasks(app.config['APP_DIR'])
    return celery


celery = celery_app(create_app(celery=True))
