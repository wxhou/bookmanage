import os
import uuid
import hashlib
from copy import deepcopy
from flask import jsonify, current_app
from pypinyin import lazy_pinyin
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.utils import secure_filename


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


def random_filename(old_filename):
    """随机文件名
    使用lazy_pinyin应对中文文件名
    """
    old_filename = "".join(lazy_pinyin(old_filename))
    old_filename = secure_filename(old_filename)
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def allowed_file(filetype, filename):
    filetypes = {
        'image': 'ALLOWED_IMAGE_EXTENSIONS',
        'audio': 'ALLOWED_AUDIO_EXTENSIONS',
        'video': 'ALLOWED_VIDEO_EXTENSIONS'
    }
    if filetype not in filetypes:
        return False
    ext_list = current_app.config[filetypes[filetype]]
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ext_list:
            return True
    return False

def hash_filename(_file):
    with open(_file) as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        hash_value = sha256obj.hexdigest()
    return hash_value