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
    id = fields.Integer()
    name = fields.String(required=True,
                         validate=validate.Length(0, 64),
                         data_key='press_name')
    addr = fields.String(required=False,
                         validate=validate.Length(0, 128),
                         data_key='press_addr')


class BookSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True, data_key='book_name')
    ISBN = fields.String(required=True, data_key='book_isbn')
    translator = fields.String(required=False)
    desc = fields.String(required=False)
    press = fields.Nested(PressSchema(only=('id', )))


@bp_book.post('/book/upload')
@doc(tags=["图书管理"], summary="上传图书资料")
@use_kwargs(
    {
        'image': fields.Raw(),
        'video': fields.Raw(),
        'audio': fields.Raw(),
        'ctype': fields.Int()
    },
    location='files')
@marshal_with(schema=None, code=200, description="SUCCESS")
def upload_book():
    image = request.files.get('image')
    video = request.files.get('video')
    audio = request.files.get('audio')
    ctype = request.files.get('ctype')
    if not any([image, video]):
        return response_err(ErrCode.FILES_UPLOAD_ERROR, 'not file to upload')
    result = {}
    if image:
        image_filename = image.filename.strip('" ')
        if not allowed_file('image', image_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        filename = random_filename(image_filename)
        filepath = os.path.join(current_app.config['UPLOAD_IMAGE_FOLDER'],
                                filename)
        image.save(filepath)
        book_media = BookMedia(url='/images/' + filename, mtype=1, ctype=ctype)
        db.session.add(book_media)
        db.session.commit()
        result['image'] = book_media.id
    if audio:
        audio_filename = image.filename.strip('" ')
        if not allowed_file('audio', audio_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        filename = random_filename(image_filename)
        filepath = os.path.join(current_app.config['UPLOAD_AUDIO_FOLDER'],
                                filename)
        image.save(filepath)
        book_media = BookMedia(url='/images/' + filename, mtype=2, ctype=ctype)
        db.session.add(book_media)
        db.session.commit()
        result['audio'] = book_media.id
    if video:
        video_filename = video.filename.strip('" ')
        if not allowed_file('video', video_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        filename = random_filename(video_filename)
        filepath = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'],
                                filename)
        video.save(filepath)
        book_media = BookMedia(url='/images/' + filename, mtype=3, ctype=ctype)
        db.session.add(book_media)
        db.session.commit()
        result['video'] = book_media.id
    return response_succ(data=result)


@doc(tags=["出版社管理"])
class PressView(MethodResource):
    @doc(summary="出版社列表")
    @marshal_with(PressSchema(many=True))
    def get(self):
        presss = Press.query.filter_by(status=0)
        return response_succ(data=PressSchema(many=True).dump(presss))

    @doc(summary="添加出版社")
    @use_kwargs(PressSchema(exclude=('id', )))
    @marshal_with(PressSchema)
    def post(self, **kwargs):
        press = Press(**kwargs)
        db.session.add(press)
        db.session.commit()
        return response_succ(data=PressSchema().dump(press))


@doc(tags=["出版社管理"])
class PressEditView(MethodResource):
    @doc(summary="出版社详情")
    @use_kwargs(PressSchema(exclude=('id', ), partial=True))
    @marshal_with(PressSchema)
    def get(self, pk, **kwargs):
        presss = Press.query.filter_by(id=int(pk), **kwargs,
                                       status=0).one_or_none()
        if presss is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        return response_succ(data=PressSchema().dump(presss))

    @doc(summary="修改出版社")
    @use_kwargs(PressSchema(exclude=('id', ), partial=True))
    @marshal_with(PressSchema)
    def put(self, pk, **kwargs):
        press = Press.query.filter_by(id=int(pk), status=0).one_or_none()
        if press is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        for k, v in kwargs.items():
            setattr(press, k, v)
        db.session.commit()
        return response_succ(PressSchema().dump(press))

    @doc(summary="删除出版社")
    @marshal_with(None)
    def delete(self, pk, **kwargs):
        press = Press.query.filter_by(id=int(pk), status=0).one_or_none()
        if press is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        press.status = -1
        db.session.commit()
        return response_succ()


@doc(tags=['图书管理'])
class BookView(MethodResource):
    @doc(summary="图书列表")
    @marshal_with(BookSchema(many=True))
    def get(self):
        books = Book.query.filter_by(status=0)
        return response_succ(data=BookSchema(many=True).dump(books))

    @doc(summary="添加图书")
    @use_kwargs(BookSchema(exclude=('id', )))
    @marshal_with(BookSchema)
    def post(self, **kwargs):
        press_obj = Press.query.filter_by(**kwargs.pop('press', None),
                                          status=0).one_or_none()
        if press_obj is None:
            return response_err(ErrCode.QUERY_NO_DATA, "出版社是空的")
        kwargs['press'] = press_obj
        book = Book(**kwargs)
        db.session.add(book)
        db.session.commit()
        return response_succ(data=BookSchema().dump(book))


@doc(tags=['图书管理'])
class BookEditView(MethodResource):
    @doc(summary="图书详情")
    def get(self, pk):
        book = Book.query.filter_by(id=int(pk), status=0).one_or_none()
        if book is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        return response_succ(data=BookSchema().dump(book))

    @doc(summary="修改图书")
    @use_kwargs(BookSchema(exclude=('id', )))
    @marshal_with(BookSchema)
    def put(self, pk, **kwargs):
        press_obj = Press.query.filter_by(**kwargs.pop('press', None),
                                          status=0).one_or_none()
        if press_obj is not None:
            kwargs['press'] = press_obj
        book = Book.query.filter_by(id=int(pk), status=0).one_or_none()
        if book is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        for k, v in kwargs.items():
            setattr(book, k, v)
        db.session.commit()
        return response_succ(data=BookSchema().dump(book))

    @doc(summary="删除图书")
    @marshal_with(None)
    def delete(self, pk):
        book = Book.query.filter_by(id=int(pk), status=0).one_or_none()
        if book is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        book.status = -1
        db.session.commit()
        return response_succ()