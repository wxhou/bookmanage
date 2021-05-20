#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import click
from .extensions import db
from apps.model import User


def register_commands(app):
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
        if user is not None:
            click.echo('Updating user...')
            user.email = email
            user.password = password
        else:
            click.echo('Creating user...')
            user = User(email=email)
            user.password = password
            db.session.add(user)

        db.session.commit()
        click.echo('Done.')