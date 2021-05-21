import os
import sqlalchemy
from flasgger import swag_from
from flask import g, request, Blueprint, current_app
from marshmallow import Schema, fields, validate, ValidationError
from core.utils import ErrCode, response_err, response_succ, allowed_file, random_filename, hash_filename
from core.extensions import cache
from .model import db, User, Avatar
from .decorators import dc_login_required

bp_auth = Blueprint('bp_auth', __name__)


@bp_auth.post('/avatar/upload')
def upload_avatar():
    """上传资源"""
    image = request.files.get('image')
    video = request.files.get('video')
    ctype = request.files.get('ctype')
    if not any([image, video]):
        return response_err(ErrCode.FILES_UPLOAD_ERROR, 'not file to upload')
    result = {}
    if image:
        image_filename = image.filename.strip('" ')
        if allowed_file('image', image_filename):
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
        if allowed_file('video', video_filename):
            filename = random_filename(video_filename)
            filepath = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'],
                                    filename)
            video.save(filepath)
            avatar = Avatar(url='/images/' + filename, mtype=3, ctype=ctype)
            db.session.add(avatar)
            db.session.commit()
            result['video'] = avatar.id
    return response_succ(data=result)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True,
                             load_only=True,
                             validate=[
                                 validate.Length(8, 16),
                                 validate.Regexp("^[a-zA-Z]\w{5,17}$")
                             ])


@bp_auth.post('/login')
@swag_from('./docs/auth/login.yml')
def login():
    """登录"""
    try:
        args = LoginSchema().load(request.get_json())
    except ValidationError as err:
        return response_err(ErrCode.COMMON_PARAMS_ERROR, err.messages)
    user = User.query.filter_by(email=args.get('email')).one_or_none()
    if user is not None and user.validate_password(args.get("password")):
        token, _ = user.generate_token()
        user.token = token
        db.session.commit()
        return response_succ(token=token)
    return response_err(ErrCode.COMMON_LOGIN_ERROR, 'login error')


@bp_auth.get('/logout')
@dc_login_required
@swag_from('./docs/auth/logout.yml')
def logout():
    """登出"""
    user = User.query.filter_by(id=g.current_user.id, status=0).one_or_none()
    if user is None:
        return response_err(ErrCode.QUERY_NO_DATA, 'logout error')
    user.token = ''
    db.session.commit()
    return response_succ()


class RegisterSchema(Schema):
    """用户信息"""
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


@bp_auth.post('/user/register')
@swag_from('./docs/auth/register.yml')
def register():
    """注册用户"""
    try:
        args = RegisterSchema().load(request.get_json())
    except ValidationError as err:
        return response_err(ErrCode.COMMON_PARAMS_ERROR, err.messages)
    try:
        user = User(username=args.get('username'),
                    email=args.get('email'),
                    phone=args.get('phone'),
                    avatar_id=args.get('avatar'))
        user.password = args.get('password')
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return response_err(ErrCode.COMMON_REGISTER_ERROR, 'user has exists')
    user_obj = RegisterSchema().dump(user)
    avatar_obj = Avatar.query.filter_by(id=args.get('avatar'), status=0).one_or_none()
    if avatar_obj is not None:
        user_obj['avatar_url'] = avatar_obj.url
    return response_succ(user_obj)


@bp_auth.post('/user/modify')
@dc_login_required
def user_modify():
    """修改用户"""
    try:
        args = RegisterSchema(exclude=('email', ),
                              partial=True).load(request.get_json())
    except ValidationError as err:
        return response_err(ErrCode.COMMON_PARAMS_ERROR, err.messages)
    user = User.query.filter_by(id=g.current_user.id, status=0).one_or_none()
    for k, v in args.items():
        setattr(user, k, v)
    db.session.commit()
    user_obj = RegisterSchema()
    current_app.logger.info(user_obj)
    avatar_obj = Avatar.query.filter_by(id=user.avatar_id, status=0).one_or_none()
    user_obj.context['avatar_url'] = avatar_obj.url
    current_app.logger.info(user_obj.context)
    result = user_obj.dump(user)
    current_app.logger.info(result.data)
    return response_succ(result)
