import traceback
from flask import current_app
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException, InternalServerError
from .response import ErrCode, response_err, response_succ


def register_errors(app):
    @app.errorhandler(404)
    def page_not_found(err):
        return response_err(ErrCode.COMMON_NOT_FOUND, HTTP_STATUS_CODES[404],
                            err.code)

    @app.errorhandler(422)
    @app.errorhandler(400)
    def request_error(err):
        """ValidationErrorRequest"""
        headers = err.data.get("headers", None)
        message = err.data.get('messages', ["Invalid request."])
        if headers:
            return response_err(ErrCode.COMMON_PARAMS_ERROR,
                                message.get('json'), err.code, headers)
        return response_err(ErrCode.COMMON_PARAMS_ERROR, message.get('json'),
                            err.code)

    @app.errorhandler(429)
    def to_many_request(err):
        return response_err(429, HTTP_STATUS_CODES[429], err.code)

    @app.errorhandler(500)
    @app.errorhandler(InternalServerError)
    def internal_server_error(err):
        current_app.logger.critical(traceback.format_exc())
        return response_err(500, HTTP_STATUS_CODES[500], err.code)
    
    @app.errorhandler(Exception)
    def unknown_error(err):
        current_app.logger.critical(traceback.format_exc())
        return response_err(ErrCode.COMMON_DB_ERROR, 'Unknown Error', 500)
