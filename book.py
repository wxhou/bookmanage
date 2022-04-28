from __future__ import absolute_import, unicode_literals
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from celery import Celery
from dotenv import load_dotenv
from settings import celeryconfig
from common.initial import register_initial
from common.exceptions import register_exceptions
from common.extensions import register_extensions, register_celery


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ENV_FILE = os.path.join(BASE_DIR, '.env')
if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE)


def create_app(**kwargs):
    env = kwargs.get('env') or os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    print("use in: ", env)
    print("root_path:", app.root_path)
    env_file = os.path.join(BASE_DIR, 'settings', env + '.py')
    app.config.from_pyfile(env_file)
    register_extensions(app)
    register_exceptions(app)
    register_celery(kwargs.get('celery'), app)
    register_logger(app)
    register_initial(app)
    register_blueprints(app)
    return app


def register_blueprints(app):
    from apps.auth.router import bp_auth, register_auth_docs
    from apps.book.router import bp_book, register_book_docs
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_book)
    register_auth_docs()
    register_book_docs()


def register_logger(app):
    # 配置flask自带日志
    logger_level = {
        'DEBUG': logging.DEBUG,
        'ERROR': logging.ERROR,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'CRITICAL': logging.CRITICAL
    }
    file_handler = RotatingFileHandler(filename=app.config['LOGGER_FILE'],
                                       maxBytes=10 * 1024 * 1024,
                                       backupCount=10)
    formatter = logging.Formatter(app.config['LOGGER_FORMATTER'])
    file_handler.setFormatter(formatter)
    app.logger.setLevel(logger_level[app.config['LOGGER_LEVEL']])
    app.logger.addHandler(file_handler)

    # 其他日志
    socket_handler = RotatingFileHandler(
        filename=app.config['LOGGER_FILE_WEBSOCKET'],
        maxBytes=10 * 1024 * 1024,
        backupCount=10)
    formatter = logging.Formatter(app.config['LOGGER_FORMATTER'])
    socket_handler.setFormatter(formatter)
    socket_handler.setLevel(logger_level[app.config['LOGGER_LEVEL']])
    websocket_logger = logging.getLogger('websocket')
    websocket_logger.addHandler(socket_handler)




def make_celery(app_name):

    celery = Celery(
        app_name,
        broker=celeryconfig.broker_url,
        backend=celeryconfig.result_backend
    )
    celery.config_from_object(celeryconfig)
    celery.autodiscover_tasks(['apps.auth', 'apps.book'])
    return celery

book_celery = make_celery(__name__)
app = create_app(celery=book_celery)

if __name__=='__main__':
    app.run(debug=True, port=app.config['DEBUG_PORT'])