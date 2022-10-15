import os
from flask_apispec import doc, marshal_with, use_kwargs, MethodResource
from flask import g, request, Blueprint, current_app, url_for
from marshmallow import fields
from app.common.extensions import db, cache, docs
from app.common.response import ErrCode, response_err, response_succ
from app.common.utils import allowed_file, random_filename

from .model import Avatar, User, Role
from .decorators import dc_login_required
from .serializer import AvatarsSchema, UserSchema
from .tasks import send_register_email


bp_admin = Blueprint('bp_admin', __name__)


@bp_admin.post('/avatar/upload')
@doc(tags=["用户管理"], summary="上传用户资料", type='file')
@use_kwargs(AvatarsSchema, location='files')
@marshal_with(schema=None, code=200, description='all good here')
def upload_avatar(**kwargs):
    image = request.files.get('image')
    video = request.files.get('video')
    ctype = request.form.get('ctype')
    if not any([image, video]):
        return response_err(ErrCode.FILE_NOT_FOUND)
    result = {}
    if image:
        image_filename = image.filename.strip('" ')
        if not allowed_file('image', image_filename):
            return response_err(ErrCode.FILE_EXT_ERROR)
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
            return response_err(ErrCode.FILE_EXT_ERROR)
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


@bp_admin.post('/login')
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
    return response_err(ErrCode.AUTH_LOGIN_ERROR)


@bp_admin.route('/logout', methods=['GET', 'POST'])
@doc(tags=["登录注册"], summary="登出") # deprecated=True 标记swagger删除
@dc_login_required
def logout():
    """登出"""
    user = User.query.filter_by(id=g.current_user.id, status=0).one_or_none()
    if user is None:
        return response_err(ErrCode.USER_NOT_EXISTS)
    user.token = ''
    db.session.commit()
    return response_succ()


@doc(tags=['用户管理'])
class UserView(MethodResource):
    """用户管理
    """

    @doc(summary="用户列表")
    @marshal_with(UserSchema(many=True))
    @dc_login_required
    def get(self, **kwargs):
        user = User.query.filter_by(status=0)
        return response_succ(data=UserSchema(many=True).dump(user))

    @doc(summary="新建用户")
    @use_kwargs(UserSchema)
    @marshal_with(UserSchema)
    def post(self, **kwargs):
        email = kwargs.get('email')
        user = User.query.filter_by(email=email).one_or_none()
        if email and user is not None:
            return response_err(ErrCode.USER_HAS_EXISTS)
        user = User(username=kwargs.get('username'),
                    email=email,
                    phone=kwargs.get('phone'),
                    avatar_id=kwargs.get('avatar'))
        user.password = kwargs.get('password')
        user.role = Role.query.filter_by(name='Guest').first()
        db.session.add(user)
        db.session.commit()
        token, _ = user.generate_token()
        user.token = token
        db.session.commit()
        # send_mail
        register_url = url_for('.active_user', token=token, _external=True)
        send_register_email.delay(register_url, user.email)
        return response_succ(data=UserSchema().dump(user))


@doc(tags=["用户管理"], summary="用户激活")
@bp_admin.get('/user/active/<token>')
def active_user(token):
    """激活用户"""
    if User.validate_token(token):
        user = g.current_user
        user.active = True
        user.token = ''
        db.session.commit()
        return response_succ()
    return response_err(ErrCode.AUTH_REGISTER_ERROR)


@doc(tags=['用户管理'])
class UserEditView(MethodResource):
    """用户管理
    """

    decorators = [dc_login_required]

    @doc(summary="用户详情")
    @use_kwargs({'email': fields.Email()}, location='query')
    @marshal_with(UserSchema)
    def get(self, pk, **kwargs):
        user = User.query.filter_by(id=int(pk), status=0,
                                    **kwargs).one_or_none()
        if user is None:
            return response_err(ErrCode.USER_NOT_EXISTS)
        return response_succ(data=UserSchema().dump(user))

    @doc(summary="修改用户信息")
    @dc_login_required
    @use_kwargs(UserSchema(exclude=('email',), partial=True))
    @marshal_with(UserSchema)
    def post(self, pk, **kwargs):
        user = User.query.filter_by(id=int(pk), status=0).one_or_none()
        if user is None:
            return response_err(ErrCode.USER_NOT_EXISTS)
        for k, v in kwargs.items():
            setattr(user, k, v)
        db.session.commit()
        return response_succ(UserSchema().dump(user))


bp_admin.add_url_rule('/user', view_func=UserView.as_view('UserView'))
bp_admin.add_url_rule('/user/<int:pk>',
                     view_func=UserEditView.as_view('UserEditView'))