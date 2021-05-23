from flask import Blueprint
from core.extensions import docs
from apps.views_auth import bp_auth, login
from apps.views_books import bp_book

bp_client = Blueprint('client', __name__)
bp_client.register_blueprint(bp_auth, url_prefix='/auth')
bp_client.register_blueprint(bp_book, url_prefix='/book')


def register_docs_apps(app):
    docs.register(login, endpoint='login', blueprint='client.bp_auth')