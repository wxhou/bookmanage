
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_apispec.extension import FlaskApiSpec


db = SQLAlchemy()
cache = Cache()
migrate = Migrate(db=db)
docs = FlaskApiSpec()

def raw_sql(_sql):
    result = db.engine.execute(text(_sql))
    return result