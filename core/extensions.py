
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

db = SQLAlchemy()
cache = Cache()
migrate = Migrate(db=db)


def raw_sql(_sql):
    result = db.engine.execute(text(_sql))
    return result