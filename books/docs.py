
from app.extensions import docs
from . import views_auth, views_books, views_demo


def register_books_docs():
    docs.register(views_auth.upload_avatar,
                  blueprint='client.bp_auth')
    docs.register(views_auth.login,
                  blueprint='client.bp_auth')
    docs.register(views_auth.logout,
                  blueprint='client.bp_auth')
    docs.register(views_auth.active_user,
                  blueprint='client.bp_auth')
    docs.register(views_auth.UserView,
                  endpoint='UserView',
                  blueprint='client.bp_auth')
    docs.register(views_auth.UserEditView,
                  endpoint='UserEditView',
                  blueprint='client.bp_auth')
    docs.register(views_books.upload_book,
                  blueprint='client.bp_book')
    docs.register(views_books.PressView,
                  endpoint='PressView',
                  blueprint='client.bp_book')
    docs.register(views_books.PressEditView,
                  endpoint='PressEditView',
                  blueprint='client.bp_book')
    docs.register(views_books.BookView,
                  endpoint='BookView',
                  blueprint='client.bp_book')
    docs.register(views_books.BookEditView,
                  endpoint='BookEditView',
                  blueprint='client.bp_book')
    docs.register(views_demo.hello,
                  blueprint='client.bp_demo')
