from flask import request
from sqlalchemy import text
from flask_cors import CORS
from flask_mail import Mail
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from flask_apispec.extension import FlaskApiSpec
from apispec.ext.marshmallow import MarshmallowPlugin


db = SQLAlchemy()
cache = Cache()
mail = Mail()
cors = CORS()
migrate = Migrate(db=db)
docs = FlaskApiSpec(document_options=False)  # 为False时不显示options方法
limiter = Limiter(key_func=get_ipaddr)
babel = Babel(configure_jinja=False)


apispec_plugin = MarshmallowPlugin(schema_name_resolver=lambda schema: None)


def raw_sql(_sql):
    return db.engine.execute(text(_sql))


def register_celery(celery, app):
    celery.flaskapp = app.app_context()
    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with celery.flaskapp:
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


@babel.localeselector
def get_locale():
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['zh', 'en'])
