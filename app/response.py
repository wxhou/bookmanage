from copy import deepcopy
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


class ErrCode(object):
    COMMON_LOGIN_ERROR = 1001
    COMMON_TOKEN_ERROR = 1002
    COMMON_PARAMS_ERROR = 1003
    COMMON_DB_ERROR = 1004
    COMMON_NOT_FOUND = 1005
    COMMON_REGISTER_ERROR = 1006

    QUERY_NO_DATA = 2001
    QUERY_DATA_EXIST = 2002

    FILES_UPLOAD_ERROR = 3001


def response_err(code, msg='', *args):
    """错误返回"""
    if args:
        return jsonify({'errcode': code, 'errmsg': msg}), *args
    return jsonify({'errcode': code, 'errmsg': msg})


def response_succ(result=None, cookies=None, **kwargs):
    """正确返回"""
    if result is None:
        results = {'errcode': 0, 'errmsg': 'success'}
    else:
        results = deepcopy(result)
    for k, v in kwargs.items():
        if k in ['code', 'errcode']:
            results['errcode'] = v
            continue
        results[k] = v
    res = jsonify(results)
    if cookies:
        for k, v in cookies.items():
            res.set_cookie(k, v)
    return res
