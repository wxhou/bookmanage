from copy import deepcopy
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from flask_babel import gettext as _

class ErrCode(object):
    """_summary_

    Args:
        object (_type_): _description_
        1XXX - 2XXX: 公共
        3XXX: 登录
    """
    COMMON_HTTP_STATUS_CODES = {
        400: [400, _(HTTP_STATUS_CODES[400])],
        404: [404, _(HTTP_STATUS_CODES[404])],
        405: [405, _(HTTP_STATUS_CODES[405])],
        429: [429, _(HTTP_STATUS_CODES[429])],
        500: [500, _(HTTP_STATUS_CODES[500])],
    }

    COMMON_PARAMS_ERROR = [1001, _('request params error')]
    COMMON_DB_ERROR = [1002, _('db error')] # 数据异常
    COMMON_NOT_FOUND = [1003, _('not found')]
    COMMON_INTERNAL_ERR =   [1004, _('internal error')]
    COMMON_PERMISSION_ERR = [1005, _('no permission')]

    QUERY_NO_DATA = [2001, _('data not exists')]
    QUERY_DATA_EXIST = [2002, _('data has exists')]
    FILE_NOT_FOUND = [2004, _('not file to upload')]
    FILE_EXT_ERROR = [2005, _('not file to upload')]

    # AUTH
    USER_NOT_EXISTS = [3001, _('user not exists')]
    USER_HAS_EXISTS = [3002, _('user has exists')]
    AUTH_NOT_LOGIN = [3003, _('Not logged in')]
    AUTH_LOGIN_ERROR = [3004, _('username/password error')]
    AUTH_REGISTER_ERROR = [3005, _('register error')]
    AUTH_TOKEN_ERROR = [3006, _('register error')]
    AUTH_TOKEN_TYPE_ERROR = [3007, _('Token type error')]
    AUTH_TOKEN_VALIDATE_ERROR = [3008, _('Token validate error')]


def response_err(code):
    """错误返回"""
    return jsonify({'errcode': code[0], 'errmsg': code[1]})


def response_succ(result=None, cookies=None, **kwargs):
    """正确返回"""
    if result is None:
        results = {'errcode': 0, 'errmsg': 'success'}
    else:
        results = deepcopy(result)
    res = jsonify({**results, **kwargs})
    if cookies is not None:
        for k, v in cookies.items():
            res.set_cookie(k, v)
    return res
