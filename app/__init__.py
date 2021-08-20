# -*- coding: utf-8 -*-
import os
import logging
from logging.handlers import RotatingFileHandler

import click
from flask import Flask
from settings.base import BASE_DIR
from app.extensions import (db, cors, mail, migrate, cache, docs, limiter)
from app.exceptions import register_errors


def create_app(env=None):
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    print("use in: ", env)
    pyfile = os.path.join(BASE_DIR, 'settings', env + '.py')
    app.config.from_pyfile(pyfile)
    register_extensions(app)
    register_logger(app)
    register_commands(app)
    register_errors(app)
    register_blueprints(app)
    register_docs()
    return app


def register_blueprints(app):
    from apps_book.router import bp_client
    app.register_blueprint(bp_client, url_prefix='/client')


def register_docs():
    from apps_book.router import register_docs_apps
    register_docs_apps()


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app=app)
    docs.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app, config=app.config['CACHE_CONFIG'])
    cors.init_app(app)
    app.redis_obj = cache.cache._write_client = cache.cache._read_clients


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


def register_commands(app):
    from apps_book.model import User, Role, Permission

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            db.drop_all()
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--email',
                  prompt=True,
                  help='The username used to login.')
    @click.option('--password',
                  prompt=True,
                  hide_input=True,
                  confirmation_prompt=True,
                  help='The password used to login.')
    def adminuser(email, password):
        """Create user."""
        db.create_all()

        user = User.query.first()
        role = Role.query.filter_by(name='Admin').first()
        if user is not None:
            click.echo('Updating user...')
            user.email = email
            user.role = role
            user.active = True
            user.password = password
        else:
            click.echo('Creating user...')
            user = User(email=email, role=role)
            user.password = password
            user.active = True
            db.session.add(user)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    def initrole():
        roles_permissions_map = {
            'Guest': ['SEE'],
            'User': ['LOGIN', 'SEE', 'LEASE'],
            'VIP': ['LOGIN', 'SEE', 'LEASE', 'BUY'],
            'Author': ['LOGIN', 'SEE', 'LEASE', 'BUY', 'WRITE', 'UPLOAD'],
            'Admin':
                ['LOGIN', 'SEE', 'LEASE', 'BUY', 'WRITE', 'UPLOAD', 'ADMIN']
        }
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(
                    name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()
        click.echo("Init Role Done!")
