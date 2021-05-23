# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask
from flask_cors import CORS
from core.extensions import (db, migrate, cache, docs)
from core.commands import register_commands
from core.errors import register_errors

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app(env=None, celery=None):
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    print("use in: ", env)
    pyfile = os.path.join(basedir, 'settings', env + '.py')
    app.config.from_pyfile(pyfile)
    register_extensions(app)
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
    cache.init_app(app, config=app.config['CACHE_CONFIG'])
    CORS(app)
