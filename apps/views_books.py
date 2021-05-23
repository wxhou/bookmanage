import os
import sqlalchemy
from flask import g, request, Blueprint, current_app
from marshmallow import Schema, fields, validate, ValidationError
from core.utils import ErrCode, response_err, response_succ, allowed_file, random_filename, hash_filename
from core.extensions import cache
from .model import db, Press, Book, BookMedia
from .decorators import dc_login_required

bp_book = Blueprint('bp_book', __name__)


class PressSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,
                         validate=validate.Length(0,64),
                         data_key='press_name')
    addr = fields.String(required=True,
                         validate=validate.Length(0, 128),
                         data_key='press_addr')
    books = fields.List(fields.Nested(lambda: BookSchema))


class BookSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, data_key='book_name')
    isbn = fields.String(required=True, data_key='book_isbn')
    translator = fields.String(required=False)
    desc = fields.String(required=False)
    author = fields.List(fields.Nested(PressSchema))


@bp_book.post('/press/insert')
def press_insert():
    try:
        args = PressSchema(exclude=('id', )).load(request.get_json())
    except ValidationError as err:
        return response_err(ErrCode.COMMON_PARAMS_ERROR, err.messages)
    press = Press(name=args.get('name'), addr=args.get('addr'))
    db.session.add(press)
    db.session.commit()
    return response_succ(data=PressSchema().dump(press))


@bp_book.get('/press/list')
def press_list():
    arg = request.args
    error = PressSchema()