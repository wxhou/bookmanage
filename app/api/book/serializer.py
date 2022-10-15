from marshmallow import Schema, fields, validate
from app.common.fields import FileField


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
    ctype = fields.Int(default=1)


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
