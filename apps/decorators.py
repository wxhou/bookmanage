from functools import wraps
from flask import request, current_app
from core.utils import ErrCode, response_err, response_succ
from .model import User


def dc_login_required(func):
    """登录验证"""
    @wraps(func)
    def wrappers(*args, **kwargs):
        authorization = request.headers.get('Authorization')
        if authorization is None:
            return response_err(ErrCode.COMMON_TOKEN_ERROR, 'token error')
        token_type, token = authorization.split(None, 1)
        if token_type.lower() != 'bearer' and token is None:
            return response_err(ErrCode.COMMON_TOKEN_ERROR, 'token error')
        if User.validate_token(token):
            return func(*args, **kwargs)
        return response_err(ErrCode.COMMON_TOKEN_ERROR, 'token error')

    return wrappers