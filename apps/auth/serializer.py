from marshmallow import Schema, fields, validate
from common.fields import FileField
from .model import Avatar


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