from functools import wraps
from flask import request, current_app
from common.response import ErrCode, response_err
from books.model import User
from flask_babel import _


def dc_login_required(func):
    """登录验证"""
    @wraps(func)
    def wrappers(*args, **kwargs):
        authorization = request.headers.get('Authorization')
        if authorization is None:
            return response_err(ErrCode.COMMON_TOKEN_ERROR, _('Not logged in'))
        token_type, token = authorization.split(None, 1)
        if token is None or token_type.lower() != 'bearer':
            return response_err(ErrCode.COMMON_TOKEN_ERROR, _('Token type error'))
        if User.validate_token(token):
            return func(*args, **kwargs)
        return response_err(ErrCode.COMMON_TOKEN_ERROR, _('Token validate error'))

    return wrappers
