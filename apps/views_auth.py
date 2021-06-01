import os
import sqlalchemy
from flask_apispec import doc, marshal_with, use_kwargs, MethodResource
from flask import g, request, Blueprint, current_app
from marshmallow import Schema, fields, validate

from core.extensions import cache, docs
from core.mails import send_register_email
from core.response import ErrCode, response_err, response_succ
from core.utils import allowed_file, random_filename

from .model import db, User, Avatar, Role
from .serializer import UserSchema
from .decorators import dc_login_required

bp_auth = Blueprint('bp_auth', __name__)


@bp_auth.post('/avatar/upload')
@doc(tags=["用户管理"], summary="上传用户资料", type='file')
@use_kwargs(
    {
        'image': fields.Raw(),
        'video': fields.Raw(),
        'ctype': fields.Str(default=1)
    },
    location='files')
@marshal_with(schema=None, code=200, description='all good here')
def upload_avatar(**kwargs):
    image = request.files.get('image')
    video = request.files.get('video')
    ctype = request.form.get('ctype')
    if not any([image, video]):
        return response_err(ErrCode.FILES_UPLOAD_ERROR, 'not file to upload')
    result = {}
    if image:
        image_filename = image.filename.strip('" ')
        if not allowed_file('image', image_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        hash_name = random_filename(image, image_filename)
        avatar_obj = Avatar.query.filter_by(uid=hash_name).one_or_none()
        if avatar_obj is None:
            filepath = os.path.join(current_app.config['UPLOAD_IMAGE_FOLDER'],
                                    hash_name)
            image.save(filepath)
            avatar_obj = Avatar(url='/images/' + hash_name,
                                mtype=1, uid=hash_name, ctype=ctype)
            db.session.add(avatar_obj)
        avatar_obj.status = 0
        db.session.commit()
        result['image'] = avatar_obj.id
    if video:
        video_filename = video.filename.strip('" ')
        if not allowed_file('video', video_filename):
            return response_err(ErrCode.FILES_UPLOAD_ERROR,
                                'file is not allow')
        hash_name = random_filename(video, video_filename)
        avatar_obj = Avatar.query.filter_by(uid=hash_name).one_or_none()
        if avatar_obj is None:
            filepath = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'],
                                    hash_name)
            video.save(filepath)
            avatar_obj = Avatar(url='/videos/' + hash_name,
                                mtype=3, uid=hash_name, ctype=ctype)
            db.session.add(avatar_obj)
        avatar_obj.status = 0
        db.session.commit()
        result['video'] = avatar_obj.id
    return response_succ(data=result)


@bp_auth.post('/login')
@doc(tags=["登录注册"], summary='登录')
@use_kwargs(UserSchema(only=('email', 'password')))
def login(**kwargs):
    """登录"""
    user = User.query.filter_by(email=kwargs.get('email')).one_or_none()
    if user is not None and user.validate_password(
            kwargs.get("password")) and user.active:
        token, expire = user.generate_token()
        user.token = token
        db.session.commit()
        return response_succ(token=token, expire=expire)
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
            user.role = Role.query.filter_by(name='Guest').first()
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return response_err(ErrCode.COMMON_REGISTER_ERROR,
                                'user has exists')
        token, _ = user.generate_token()
        user.token = token
        db.session.commit()
        send_register_email(token, user.email)
        return response_succ(data=UserSchema().dump(user))


@doc(tags=["用户管理"], summary="用户激活")
@bp_auth.get('/user/active/<token>')
def active_user(token):
    """激活用户"""
    if User.validate_token(token):
        current_app.logger.info(g.current_user)
        user = g.current_user
        user.active = True
        user.token = ''
        db.session.commit()
        return response_succ()
    return response_err(ErrCode.COMMON_LOGIN_ERROR, 'register error')


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
