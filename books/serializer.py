from common.schema import Schema, fields, validate, FileField, PageSchema
from .model import User, Avatar, Book, Press, Author


class AvatarsSchema(Schema):
    """用户头像"""
    image = FileField()
    video = FileField()
    ctype = fields.Str(default=1)


class UserSchema(Schema):
    """用户信息"""
    id = fields.Integer(dump_only=True)
    username = fields.String(required=False, validate=validate.Length(0, 128))
    email = fields.String(required=True, validate=validate.Email())
    phone = fields.String(required=True, validate=validate.Length(11))
    avatar = fields.Integer(required=False)
    password = fields.String(required=True,
                             load_only=True,
                             validate=[
                                 validate.Length(8, 16),
                                 validate.Regexp("^[a-zA-Z]\w{5,17}$")
                             ])

    avatar_url = fields.Method("get_avatar_url", dump_only=True)

    def get_avatar_url(self, obj):
        avatar_obj = Avatar.query.filter_by(id=obj.avatar_id,
                                            status=0).one_or_none()
        return avatar_obj.url if avatar_obj is not None else ''


class PressSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True,
                         validate=validate.Length(0, 64),
                         data_key='press_name')
    addr = fields.String(required=False,
                         validate=validate.Length(0, 128),
                         data_key='press_addr')


class BookMediaSchema(Schema):
    image = FileField()
    audio = FileField()
    video = FileField()
    ctype: fields.Int(default=1)


class BookSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True, data_key='book_name')
    ISBN = fields.String(required=True, data_key='book_isbn')
    translator = fields.String(required=False)
    desc = fields.String(required=False)
    press = fields.Nested(PressSchema(only=('id',)))
    images = fields.List(fields.Integer(), load_only=True)
    audio = fields.Integer(load_only=True)
    video = fields.Integer(load_only=True)
    image_url = fields.String(dump_only=True)
    audio_url = fields.String(dump_only=True)
    video_url = fields.String(dump_only=True)
    author = fields.Nested(lambda: AuthorSchema(exclude=("books",)))


class AuthorSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(0, 64))
    sex = fields.String(
        required=True, validate=validate.OneOf(['male', 'female']))
    books = fields.List(fields.Nested(BookSchema(exclude=('author',))))
