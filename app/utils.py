import os
import random
import hashlib
from itertools import product
from flask import current_app
from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from settings.base import UPLOAD_MEDIA_FOLDER


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
    new_filename = md5.hexdigest() + ext.lower()
    return new_filename


def random_code(length=4):
    """随机验证码"""
    return "".join(random.sample(string.ascii_letters + string.digits, length))


def random_color(s=1, e=255):
    """随机颜色"""
    return (random.randint(s, e), random.randint(s, e), random.randint(s, e))


def get_captcha(length=4, width=120, height=40):
    """生成验证码"""
    font_file = os.path.join(UPLOAD_MEDIA_FOLDER, 'font', 'arial.ttf')
    image = Image.new('RGB', (width, height), (255, 255, 255))  # 创建Image对象
    font = ImageFont.truetype(font_file, 32)    # 创建Font对象
    draw = ImageDraw.Draw(image)    # 创建Draw对象
    for x, y in product(range(width), range(height)):
        draw.point((x, y), fill=random_color(128, 255))  # 随机颜色填充每个像素
    code = random_code(length)    # 验证码
    for t in range(length):
        draw.text((30 * t + 5, 1), code[t], font=font,
                  fill=random_color(0, 127))    # 写到图片上
    image = image.filter(ImageFilter.BoxBlur(1))    # 模糊图像
    # image.save(f"{code}.png", )  # 保存图片
    # image.show()
    return code, image


if __name__ == '__main__':
    print(random_filename(
        "/Users/hoou/VScode/bookmanage/media/images/2f815da28f7b4db28389e48d64091510.jpg"))
    print(random_filename(
        "/Users/hoou/VScode/bookmanage/media/images/2f815da28f7b4db28389e48d64091596.jpg"))
