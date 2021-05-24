from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_apispec.extension import FlaskApiSpec

db = SQLAlchemy()
cache = Cache()
migrate = Migrate(db=db)
docs = FlaskApiSpec(document_options=False)  # 为False时不显示options方法
limiter = Limiter(key_func=get_remote_address)


def raw_sql(_sql):
    result = db.engine.execute(text(_sql))
    return result