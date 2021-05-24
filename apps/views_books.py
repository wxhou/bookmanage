import os
import sqlalchemy
from flask import g, request, Blueprint, current_app
from marshmallow import Schema, fields, validate
from flask_apispec import doc, use_kwargs, marshal_with, MethodResource
from core.utils import ErrCode, response_err, response_succ, allowed_file, random_filename, hash_filename
from core.extensions import cache
from .model import db, Press, Book, BookMedia
from .decorators import dc_login_required

bp_book = Blueprint('bp_book', __name__)


class PressSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,
                         validate=validate.Length(0, 64),
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


@doc(tags=["出版社管理"])
class PressView(MethodResource):
    @doc(summary="出版社列表")
    @marshal_with(PressSchema(many=True))
    def get(self):
        presss = Press.query.filter_by(status=0)
        return response_succ(data=PressSchema(many=True).dump(presss))

    @doc(summary="添加出版社")
    @use_kwargs(PressSchema(exclude=['id', 'books']))
    @marshal_with(PressSchema)
    def post(self, **kwargs):
        press = Press(**kwargs)
        db.session.add(press)
        db.session.commit()
        return response_succ(data=PressSchema().dump(press))


@doc(tags=["出版社管理"])
class PressEditView(MethodResource):
    @doc(summary="出版社详情")
    @marshal_with(PressSchema())
    def get(self, pk):
        presss = Press.query.filter_by(id=int(pk), status=0).one_or_none()
        if presss is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        return response_succ(data=PressSchema().dump(presss))

    @doc(summary="修改出版社")
    @marshal_with(PressSchema)
    def put(self, pk, **kwargs):
        pass

    @doc(summary="删除出版社")
    @marshal_with(PressSchema)
    def delete(self, pk, **kwargs):
        pass