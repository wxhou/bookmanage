from sqlalchemy import text
from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_apispec.extension import FlaskApiSpec
from apispec.ext.marshmallow import MarshmallowPlugin


db = SQLAlchemy()
cache = Cache()
mail = Mail()
cors = CORS()
migrate = Migrate(db=db)
docs = FlaskApiSpec(document_options=False)  # 为False时不显示options方法
limiter = Limiter(key_func=get_remote_address)

def resolver(schema):
    return None

apispec_plugin = MarshmallowPlugin(schema_name_resolver=resolver)


def raw_sql(_sql):
    return db.engine.execute(text(_sql))


def register_celery(celery, app):
    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
