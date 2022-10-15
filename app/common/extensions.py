from flask import request
import platform, atexit
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import text
from sqlalchemy import inspect
from flask_cors import CORS
from flask_mail import Mail
from flask_babel import Babel
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_msearch import Search
from flask_limiter.util import get_ipaddr
from flask_apispec.extension import FlaskApiSpec
from apispec.ext.marshmallow import MarshmallowPlugin
from jieba.analyse.analyzer import ChineseAnalyzer
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler


def include_object(object, name, type_, reflected, compare_to):
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-any-drop-table-directives-with-autogenerate
    if type_ == "table" and reflected and compare_to is None:
        return False
    else:
        return True


executor = ThreadPoolExecutor()
db = SQLAlchemy()
cache = Cache()
mail = Mail()
cors = CORS()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins='*')
search = Search(db=db, analyzer=ChineseAnalyzer())
migrate = Migrate(db=db, compare_type=True, include_object=include_object)
docs = FlaskApiSpec(document_options=False)  # 为False时不显示options方法
limiter = Limiter(key_func=get_ipaddr,
                  default_limits=['6000/day', '60/minute'])
babel = Babel(configure_jinja=False)
scheduler = APScheduler()


def register_scheduler(app):
    """
    注册定时任务
    """
    app.config['SCHEDULER_JOBSTORES'] = {
            'default': SQLAlchemyJobStore(url=app.config["SQLALCHEMY_DATABASE_URI"])
        }
    if platform.system() != 'Windows':
        fcntl = __import__("fcntl")
        f = open('scheduler.lock', 'wb')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            scheduler.init_app(app)
            scheduler.start()
            app.logger.debug('Scheduler Started,---------------')
        except:
            pass

        def unlock():
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

        atexit.register(unlock)
    else:
        msvcrt = __import__('msvcrt')
        f = open('scheduler.lock', 'wb')
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            scheduler.init_app(app)
            scheduler.start()
            app.logger.debug('Scheduler Started,----------------')
        except:
            pass

        def _unlock_file():
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except:
                pass

        atexit.register(_unlock_file)



def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app=app)
    babel.init_app(app)
    docs.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app)
    search.init_app(app)
    scheduler.init_app(app)
    cache.init_app(app, config=app.config['CACHE_CONFIG'])
    cors.init_app(app)
    register_scheduler(app)
    app.redis_obj = cache.cache._write_client = cache.cache._read_clients


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
