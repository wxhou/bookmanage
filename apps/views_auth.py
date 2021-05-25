import os
import sqlalchemy
from werkzeug.datastructures import FileStorage
from flask_apispec import doc, marshal_with, use_kwargs, MethodResource
from flask import g, request, Blueprint, current_app
from marshmallow import Schema, fields, validate
from core.utils import ErrCode, response_err, response_succ, allowed_file, random_filename, hash_filename
from core.extensions import cache, docs
from .model import db, User, Avatar
from .decorators import dc_login_required

bp_auth = Blueprint('bp_auth', __name__)


@bp_auth.post('/avatar/upload')
@doc(tags=["用户管理"], summary="上传用户资料")
@use_kwargs({
    'image': FileStorage,
    'video': FileStorage
},
            location='files',
            description='all good here')
@marshal_with(schema=None, code=200, description='all good here')
def upload_avatar():
    image = request.files.get('image')
    video = request.files.get('video')
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
        avatar = Avatar(url='/images/' + filename, mtype=1, ctype=ctype)
        db.session.add(avatar)
        db.session.commit()
        result['image'] = avatar.id
    if video:
        video_filename = video.filename.strip('" ')
        if not allowed_file('video', video_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        filename = random_filename(video_filename)
        filepath = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'],
                                filename)
        video.save(filepath)
        avatar = Avatar(url='/images/' + filename, mtype=3, ctype=ctype)
        db.session.add(avatar)
        db.session.commit()
        result['video'] = avatar.id
    return response_succ(data=result)


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


@bp_auth.post('/login')
@doc(tags=["登录注册"], summary='登录')
@use_kwargs(UserSchema(only=('email', 'password')))
def login(**kwargs):
    """登录"""
    user = User.query.filter_by(email=kwargs.get('email')).one_or_none()
    if user is not None and user.validate_password(kwargs.get("password")):
        token, _ = user.generate_token()
        user.token = token
        db.session.commit()
        return response_succ(token=token)
    return response_err(ErrCode.COMMON_LOGIN_ERROR, 'login error')


@bp_auth.get('/logout')
@doc(tags=["登录注册"], summary="登出", deprecated=True)
@dc_login_required
def logout():
    """登出"""
    user = User.query.filter_by(id=g.current_user.id, status=0).one_or_none()
    if user is None:
        return response_err(ErrCode.QUERY_NO_DATA, 'logout error')
    user.token = ''
    db.session.commit()
    return response_succ()


@doc(tags=['用户管理'])
class UserView(MethodResource):
    """用户管理
    """
    @doc(summary="用户列表")
    @marshal_with(UserSchema(many=True))
    def get(self, **kwargs):
        user = User.query.filter_by(status=0)
        return response_succ(data=UserSchema(many=True).dump(user))

    @doc(summary="新建用户")
    @use_kwargs(UserSchema)
    @marshal_with(UserSchema)
    def post(self, **kwargs):
        try:
            user = User(username=kwargs.get('username'),
                        email=kwargs.get('email'),
                        phone=kwargs.get('phone'),
                        avatar_id=kwargs.get('avatar'))
            user.password = kwargs.get('password')
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return response_err(ErrCode.COMMON_REGISTER_ERROR,
                                'user has exists')
        return response_succ(data=UserSchema().dump(user))


@doc(tags=['用户管理'])
class UserEditView(MethodResource):
    """用户管理
    """
    @doc(summary="用户详情")
    @use_kwargs({'email': fields.Email()}, location='query')
    @marshal_with(UserSchema)
    def get(self, pk, **kwargs):
        user = User.query.filter_by(id=int(pk), status=0,
                                    **kwargs).one_or_none()
        if user is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'data not exists')
        return response_succ(data=UserSchema().dump(user))

    @doc(summary="修改用户信息")
    @dc_login_required
    @use_kwargs(UserSchema(exclude=('email', ), partial=True))
    @marshal_with(UserSchema)
    def put(self, pk, **kwargs):
        user = User.query.filter_by(id=int(pk), status=0).one_or_none()
        if user is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'user not exists')
        for k, v in kwargs.items():
            setattr(user, k, v)
        db.session.commit()
        return response_succ(UserSchema().dump(user))

    @doc(summary="删除用户")
    @dc_login_required
    def delete(self, pk):
        user = User.query.filter_by(id=int(pk), status=0).one_or_none()
        if user is None:
            return response_err(ErrCode.QUERY_NO_DATA, 'user not exists')
        return response_succ()