from flask import Blueprint
from books.views_auth import bp_auth, UserView, UserEditView
from books.views_books import bp_book, PressView, PressEditView, BookView, BookEditView
from books.views_demo import bp_demo

# bp_client
bp_client = Blueprint('client', __name__)
bp_client.register_blueprint(bp_auth, url_prefix='/auth')
bp_client.register_blueprint(bp_book, url_prefix='/book')
bp_client.register_blueprint(bp_demo, url_prefix='/demo')
# bp_auth
bp_auth.add_url_rule('/user', view_func=UserView.as_view('UserView'))
bp_auth.add_url_rule('/user/<int:pk>',
                     view_func=UserEditView.as_view('UserEditView'))
# bp_book
bp_book.add_url_rule('/press', view_func=PressView.as_view('PressView'))
bp_book.add_url_rule('/press/<int:pk>',
                     view_func=PressEditView.as_view('PressEditView'))
bp_book.add_url_rule('/', view_func=BookView.as_view('BookView'))
bp_book.add_url_rule('/<int:pk>', view_func=BookEditView.as_view('BookEditView'))
# bp_demo