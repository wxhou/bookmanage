from flask import Blueprint
from app.common.extensions import docs
from . import views_books


bp_book = Blueprint('bp_book', __name__)
bp_book.register_blueprint(views_books.bp_admin, url_prefix='/book')


def register_book_docs(app):
    docs.register(views_books.upload_book,
                  blueprint='bp_book.bp_admin')
    docs.register(views_books.PressView,
                  endpoint='PressView',
                  blueprint='bp_book.bp_admin')
    docs.register(views_books.PressEditView,
                  endpoint='PressEditView',
                  blueprint='bp_book.bp_admin')
    docs.register(views_books.BookView,
                  endpoint='BookView',
                  blueprint='bp_book.bp_admin')
    docs.register(views_books.BookEditView,
                  endpoint='BookEditView',
                  blueprint='bp_book.bp_admin')