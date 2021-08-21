from flask import Blueprint
from app.extensions import docs
from books.views_auth import bp_auth, login, logout, active_user, UserView, UserEditView, upload_avatar
from books.views_books import bp_book, PressView, PressEditView, BookView, BookEditView, upload_book

#bp_client
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
bp_book.add_url_rule('/', view_func=BookView.as_view('Book'))
bp_book.add_url_rule('/<int:pk>', view_func=BookEditView.as_view('BookEdit'))


def register_docs_apps():
    docs.register(upload_avatar,
                  endpoint='upload_avatar',
                  blueprint='client.bp_auth')
    docs.register(login, endpoint='login', blueprint='client.bp_auth')
    docs.register(logout, endpoint='logout', blueprint='client.bp_auth')
    docs.register(active_user,
                  endpoint='active_user',
                  blueprint='client.bp_auth')
    docs.register(UserView, endpoint='User', blueprint='client.bp_auth')
    docs.register(UserEditView,
                  endpoint='UserEdit',
                  blueprint='client.bp_auth')
    docs.register(upload_book,
                  endpoint='upload_book',
                  blueprint='client.bp_book')
    docs.register(PressView, endpoint='Press', blueprint='client.bp_book')
    docs.register(PressEditView,
                  endpoint='PressEdit',
                  blueprint='client.bp_book')
    docs.register(BookView, endpoint='Book', blueprint='client.bp_book')
    docs.register(BookEditView,
                  endpoint='BookEdit',
                  blueprint='client.bp_book')
