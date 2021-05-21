DEBUG = True
SECRET_KEY = "7fd2ad44-b91a-11eb-a15a-98e0d9885a43"
SQLALCHEMY_DATABASE_URI = "mysql://root:root1234@localhost/db_booklibray"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

# upload
MAX_CONTENT_LENGTH = 50*1024*1024
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
UPLOAD_IMAGE_FOLDER = './media/images'
UPLOAD_AUDIO_FOLDER = './media/audios'
UPLOAD_VIDEO_FOLDER = './media/videos'

# 分页数
PAGE_PER_NUM = 15

#cache_redis
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
SWAGGER = {
    "swagger": "2.0",
    # 'title': '测试平台接口文档',  # 浏览器标签页名称
    "info": {
        "title": "图书管理系统",  # 网页内标题
        "version": "1.0.0",
        "description": "图书管理系统(测试环境)",
    },
    # "schemes": ['http', 'https'],
    # "host": "127.0.0.1:5000",  # overrides localhost:500
    # "basePath": "",  # base bash for blueprint registration
    # "securityDefinitions": {
    #     "APIKeyHeader": {
    #         "type": "apiKey",
    #         "name": "Authorization",
    #         "in": "header",
    #     }
    # }
}

SWAGGER_CONFIG = {
    "swagger_ui":
    True,
    "headers": [],
    "specs": [{
        "endpoint": 'apispec_1',
        "route": '/apidocs/apispec_1.json',
        "rule_filter": lambda rule: True,  # all in
        "model_filter": lambda tag: True,  # all in
    }],
    "static_url_path":
    "/apidocs/flasgger_static",
    "specs_route":
    "/apidocs/",
}