from functools import wraps
from flask import request, current_app
from app.response import ErrCode, response_err
from .model import User


def dc_login_required(func):
    """登录验证"""
    @wraps(func)
    def wrappers(*args, **kwargs):
        authorization = request.headers.get('Authorization')
        if authorization is None:
            return response_err(ErrCode.COMMON_TOKEN_ERROR, 'token error')
        token_type, token = authorization.split(None, 1)
        if token is None or token_type.lower() != 'bearer':
            return response_err(ErrCode.COMMON_TOKEN_ERROR, 'token error')
        if User.validate_token(token):
            return func(*args, **kwargs)
        return response_err(ErrCode.COMMON_TOKEN_ERROR, 'token error')

    return wrappers
