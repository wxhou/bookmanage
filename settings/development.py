from settings import *
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

DEBUG = True
SECRET_KEY = "7fd2ad44-b91a-11eb-a15a-98e0d9885a43"
SQLALCHEMY_DATABASE_URI = "mysql://root:root1234@localhost/db_booklibray"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
# mail
MAIL_SERVER = 'smtp.126.com'
MAIL_PORT = 25
MAIL_USERNAME = 'twxhou@126.com'
MAIL_PASSWORD = 'GQWJDUKVWNOJLPOH'
MAIL_DEFAULT_SENDER = ('BookLibray Admin', MAIL_USERNAME)

# upload
MAX_CONTENT_LENGTH = 50 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}

# 分页数
PAGE_PER_NUM = 15

# cache_redis
CACHE_CONFIG = {
    'CACHE_TYPE': "redis",  # Flask-Caching related configs
    'CACHE_REDIS_HOST': '127.0.0.1',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 2,
    "CACHE_DEFAULT_TIMEOUT": 600
}

# crontabs
SCHEDULER_API_ENABLED = True

# SWAGGER_2 文档配置
# https://swagger.io/specification/v2/
# https://editor.swagger.io/


def resolver(schema):
    return None


APISPEC_SPEC = APISpec(title='books',
                       version='V1',
                       openapi_version='2.0',
                       plugins=[MarshmallowPlugin(schema_name_resolver=resolver)])
