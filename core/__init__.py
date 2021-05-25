# -*- coding: utf-8 -*-
import os
import sys
from flask import g, Flask
from flask_cors import CORS
from settings import BASE_DIR
from core.extensions import (db, migrate, cache, docs, limiter)
from core.commands import register_commands
from core.errors import register_errors
from core.logger import register_logger


def create_app(env=None, celery=None):
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    print("use in: ", env)
    pyfile = os.path.join(BASE_DIR, 'settings', env + '.py')
    app.config.from_pyfile(pyfile)
    register_extensions(app)
    register_logger(app)
    register_request_hook(app)
    if celery is not None:
        return app
    register_commands(app)
    register_errors(app)
    register_blueprints(app)
    register_docs(app)
    return app


def register_blueprints(app):
    from apps.router import bp_client
    app.register_blueprint(bp_client, url_prefix='/client')


def register_docs(app):
    from apps.router import register_docs_apps
    register_docs_apps(app)


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app=app)
    docs.init_app(app)
    limiter.init_app(app)
    cache.init_app(app, config=app.config['CACHE_CONFIG'])
    CORS(app)


def register_request_hook(app):
    @app.before_request
    def init_redis():
        g.redis_obj = cache.cache._write_client = cache.cache._read_clients