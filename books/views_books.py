import os
from flask import g, request, Blueprint, current_app
from marshmallow import fields, validate
from flask_apispec import doc, use_kwargs, marshal_with, MethodResource

from common.response import ErrCode, response_err, response_succ
from app.utils import allowed_file, random_filename
from app.decorators import dc_login_required
from app.extensions import cache
from .model import db, Press, Book, BookMedia, Author
from .serializer import PressSchema, BookSchema, BookMediaSchema, AuthorSchema

bp_book = Blueprint('bp_book', __name__)


@bp_book.post('/book/upload')
@doc(tags=["图书管理"], summary="上传图书资料", type='file')
@use_kwargs(BookMediaSchema, location='files')
@marshal_with(schema=None, code=200, description="SUCCESS")
def upload_book(**kwargs):
    image = request.files.get('image')
    video = request.files.get('video')
    audio = request.files.get('audio')
    ctype = request.form.get('ctype')
    if not any([image, video, audio]):
        return response_err(ErrCode.FILES_UPLOAD_ERROR, 'not file to upload')
    result = {}
    if image:
        image_filename = image.filename.strip('" ')
        if not allowed_file('image', image_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        hash_name = random_filename(image, image_filename)
        media_obj = BookMedia.query.filter_by(uid=hash_name).one_or_none()
        if media_obj is None:
            filepath = os.path.join(current_app.config['UPLOAD_IMAGE_FOLDER'],
                                    hash_name)
            image.save(filepath)
            book_media = BookMedia(
                url='/images/' + hash_name, mtype=1, ctype=ctype)
            db.session.add(book_media)
        media_obj.status = 0
        db.session.commit()
        result['image'] = book_media.id
    if audio:
        audio_filename = audio.filename.strip('" ')
        if not allowed_file('audio', audio_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        hash_name = random_filename(audio, audio_filename)
        media_obj = BookMedia.query.filter_by(uid=hash_name).one_or_none()
        if media_obj is None:
            filepath = os.path.join(current_app.config['UPLOAD_AUDIO_FOLDER'],
                                    hash_name)
            audio.save(filepath)
            book_media = BookMedia(
                url='/audios/' + hash_name, mtype=2, ctype=ctype)
            db.session.add(book_media)
        media_obj.status = 0
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
        book_media = BookMedia(url='/videos/' + filename, mtype=3, ctype=ctype)
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
    def post(self, pk, **kwargs):
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
        result = []
        for book in books:
            item = {
                'id': book.id,
                'book_name': book.name,
                'book_isbn': book.name,
                'translator': book.translator,
                'desc': book.desc
            }
            medias = BookMedia.query.filter_by(book_id=book.id, status=0)
            for media_ in medias:
                if media_.mtype == 1:
                    item['image_url'] = media_.url
                if media_.mtype == 2:
                    item['audio_url'] = media_.url
                if media_.mtype == 3:
                    item['video_url'] = media_.url
            result.append(item)
        return response_succ(data=result)

    @doc(summary="添加图书")
    @use_kwargs(BookSchema(exclude=('id', )))
    @marshal_with(BookSchema)
    def post(self, **kwargs):
        press_obj = Press.query.filter_by(**kwargs.get('press', {}),
                                          status=0).one_or_none()
        book = Book(name=kwargs.get('name'),
                    ISBN=kwargs.get('ISBN'),
                    translator=kwargs.get('translator'),
                    desc=kwargs.get('desc'))
        if press_obj is not None:
            book.press = press_obj
        db.session.add(book)
        db.session.commit()
        BookMedia.query.filter(
            BookMedia.id.in_(kwargs.get('images', [])), BookMedia.status == 0,
            BookMedia.mtype == 1).update(dict(book_id=book.id),
                                         synchronize_session=False)
        db.session.commit()
        BookMedia.query.filter_by(id=kwargs.get('video'), mtype=3,
                                  status=0).update(dict(book_id=book.id))
        db.session.commit()
        BookMedia.query.filter_by(id=kwargs.get('audio'), mtype=2,
                                  status=0).update(dict(book_id=book.id))
        db.session.commit()
        return response_succ(data=BookSchema().dump(book))


@doc(tags=['图书管理'])
class BookEditView(MethodResource):
    @doc(summary="图书详情")
    @marshal_with(BookSchema)
    def get(self, pk):
        book = Book.query.filter_by(id=int(pk), status=0).one_or_none()
        if book is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        result = BookSchema().dump(book)
        book_media = BookMedia.query.filter_by(book_id=book.id, status=0)
        for med in book_media:
            if med.mtype == 1:
                result['image_url'] = med.url
            if med.mtype == 2:
                result['audio_url'] = med.url
            if med.mtype == 3:
                result['video_url'] = med.url
        return response_succ(data=result)

    @doc(summary="修改图书")
    @use_kwargs(BookSchema(exclude=('id', ), partial=True))
    @marshal_with(BookSchema)
    def post(self, pk, **kwargs):
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
        BookMedia.query.filter_by(status=0,
                                  book_id=pk).update(dict(status=-1),
                                                     synchronize_session=False)
        BookMedia.query.filter(BookMedia.id.in_(kwargs.get('images', [])),
                               BookMedia.mtype == 1).update(
                                   dict(book_id=pk, status=0),
                                   synchronize_session=False)
        db.session.commit()
        BookMedia.query.filter_by(id=kwargs.get('video'),
                                  mtype=3).update(dict(book_id=pk, status=0))
        db.session.commit()
        BookMedia.query.filter_by(id=kwargs.get('audio'),
                                  mtype=2).update(dict(book_id=pk, status=0))
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


@doc(tags=['作者管理'])
class AuthorView(MethodResource):

    @doc(summary='作者列表')
    @marshal_with(AuthorSchema(many=True))
    def get(self):
        authors = Author.query.filter_by(status=0)
        return response_succ(data=AuthorSchema(many=True).dump(authors))

    @doc(summary='添加作者')
    @use_kwargs(AuthorSchema(exclude=('id',)))
    @marshal_with(AuthorSchema)
    def post(self, **kwargs):
        author = Author(**kwargs)
        db.session.add(author)
        db.session.commit()
        return response_succ(AuthorSchema().dump(author))


@doc(tags=['作者管理'])
class AuthorEditView(MethodResource):

    @doc(summary='获取作者信息')
    @marshal_with(AuthorSchema)
    def get(self, pk):
        author = Author.query.filter_by(id=int(pk), status=0).one_or_none()
        if author is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        return response_succ(AuthorSchema().dump(author))

    @doc(summary='修改作者信息')
    @use_kwargs(AuthorSchema(exclude=('id',), partial=True))
    @marshal_with(AuthorSchema)
    def post(self, pk, **kwargs):
        author = Author.query.filter_by(
            id=kwargs.get('id'), status=0).one_or_none()
        if author is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        for k, v in kwargs.items():
            setattr(author, k, v)
        db.session.commit()
        return response_succ(AuthorSchema().dump(author))

    @doc(summary='删除作者')
    @marshal_with(None)
    def delete(self, pk):
        author = Author.query.filter_by(id=int(pk), status=0).one_or_none()
        if author is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        return response_succ(AuthorSchema().dump(author))
