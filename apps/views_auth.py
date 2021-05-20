from flasgger import swag_from
from flask import request, Blueprint, current_app
from marshmallow import Schema, fields, validate, ValidationError
from core.utils import ErrCode, response_err, response_succ
from core.extensions import cache
from .model import db, User

bp_auth = Blueprint('bp_auth', __name__)


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
    try:
        args = LoginSchema().load(request.get_json())
    except ValidationError as err:
        return response_err(ErrCode.COMMON_PARAMS_ERROR, err.messages)
    user = User.query.filter_by(email=args.get('email')).one_or_none()
    if user is not None and user.validate_password(args.get("password")):
        token, expiration = user.generate_token()
        cache.set(user.email, token, timeout=3600)
        db.session.commit()
        return response_succ(token=token)
    return response_err(ErrCode.COMMON_LOGIN_ERROR, 'login error')


@bp_auth.post('/logout')
@swag_from('./docs/auth/logout.yml')
def logout():
    return response_succ()
