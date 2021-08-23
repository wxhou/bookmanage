from flask import Blueprint, current_app, request
from flask_babel import _
from flask_apispec import doc, marshal_with
from common.response import response_succ
from app.extensions import babel

bp_demo = Blueprint('bp_demo', __name__)


@babel.localeselector
def get_locale():
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['zh', 'en'])


@bp_demo.get('/')
@doc(tags=["示例"], summary="hello")
def hello():
    current_app.logger.info(request.headers)
    return response_succ(data=_("hello world"))