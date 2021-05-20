import os
import uuid
from copy import deepcopy
from flask import jsonify, current_app
from pypinyin import lazy_pinyin
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.utils import secure_filename


class ErrCode(object):
    COMMON_LOGIN_ERROR = 1001
    COMMON_PARAMS_ERROR = 1002
    COMMON_DB_ERROR = 1003
    COMMON_TYPE_ERROR = 1004
    COMMON_NOT_FOUND = 1005

    QUERY_NO_DATA = 2001
    QUERY_DATA_EXIST = 2002


def response_err(code, msg=None):
    """错误返回"""
    if msg is None:
        msg = ''
    return jsonify({'errcode': code, 'errmsg': msg})


def response_succ(result=None, cookies=None, **kwargs):
    """正确返回"""
    if result is None:
        results = {'errcode': 0, 'errmsg': 'success'}
    else:
        results = deepcopy(result)
    for k, v in kwargs.items():
        if k == 'code':
            results['errcode'] = v
            continue
        results[k] = v
    res = jsonify(results)
    if cookies:
        for k, v in cookies.items():
            res.set_cookie(k, v)
    return res

def random_filename(old_filename):
    """随机文件名
    使用lazy_pinyin应对中文文件名
    """
    old_filename = "".join(lazy_pinyin(old_filename))
    old_filename = secure_filename(old_filename)
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename