import os
import uuid
import hashlib
from flask import current_app
from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename


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


def random_filename(stream, filename):
    """随机文件名
    使用lazy_pinyin应对中文文件名
    """
    old_filename = "".join(lazy_pinyin(filename))
    old_filename = secure_filename(old_filename)
    md5 = hashlib.md5()
    for line in stream:
        md5.update(line)
    ext = os.path.splitext(old_filename)[1]
    new_filename = md5.hexdigest() + ext
    return new_filename


if __name__ == '__main__':
    print(hash_filename(
        "/Users/hoou/VScode/bookmanage/media/images/2f815da28f7b4db28389e48d64091510.jpg"))
    print(hash_filename(
        "/Users/hoou/VScode/bookmanage/media/images/2f815da28f7b4db28389e48d64091596.jpg"))
