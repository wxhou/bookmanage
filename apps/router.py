from flask import Blueprint
from core.extensions import docs
from apps.views_auth import bp_auth, login, logout, UserView, UserEditView, upload_avatar
from apps.views_books import bp_book, PressView, PressEditView

bp_client = Blueprint('client', __name__)

bp_client.register_blueprint(bp_auth, url_prefix='/auth')
bp_client.register_blueprint(bp_book, url_prefix='/book')
# bp_auth
bp_auth.add_url_rule('/user', view_func=UserView.as_view('User'))
bp_auth.add_url_rule('/user/<int:pk>',
                     view_func=UserEditView.as_view('UserEdit'))
# bp_book
bp_book.add_url_rule('/press', view_func=PressView.as_view('Press'))
bp_book.add_url_rule('/press/<int:pk>',
                     view_func=PressEditView.as_view('PressEdit'))


def register_docs_apps(app):
    docs.register(upload_avatar,
                  endpoint='upload_avatar',
                  blueprint='client.bp_auth')
    docs.register(login, endpoint='login', blueprint='client.bp_auth')
    docs.register(logout, endpoint='logout', blueprint='client.bp_auth')
    docs.register(UserView, endpoint='User', blueprint='client.bp_auth')
    docs.register(UserEditView,
                  endpoint='UserEdit',
                  blueprint='client.bp_auth')
    docs.register(PressView, endpoint='Press', blueprint='client.bp_book')
    docs.register(PressEditView,
                  endpoint='PressEdit',
                  blueprint='client.bp_book')