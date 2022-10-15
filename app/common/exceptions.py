import traceback
from flask import current_app, request
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import InternalServerError
from .response import ErrCode, response_err


def register_exceptions(app):
    @app.errorhandler(404)
    def page_not_found(err):
        current_app.logger.error(request.url)
        return response_err(ErrCode.COMMON_HTTP_STATUS_CODES[404], err.code)

    @app.errorhandler(422)
    @app.errorhandler(400)
    @app.errorhandler(ValidationError)
    def request_error(err):
        """ValidationErrorRequest"""
        current_app.logger.error("[ERROR]request url is : {}".format(request.url))
        current_app.logger.error("[ERROR]request params is : {}".format(err.data))
        current_app.logger.error("[ERROR]request message is : {}".format(err.messages))
        response = response_err(ErrCode.COMMON_PARAMS_ERROR)
        for k,v in err.data.get("headers", {}).items():
            response.headers[k] = v
        response.status_code = err.code
        return response


    @app.errorhandler(429)
    def to_many_request(err):
        response = response_err(ErrCode.COMMON_HTTP_STATUS_CODES[429])
        response.status_code = err.code
        return response

    @app.errorhandler(500)
    @app.errorhandler(InternalServerError)
    def internal_server_error(err):
        current_app.logger.critical(traceback.format_exc())
        response = response_err(ErrCode.COMMON_HTTP_STATUS_CODES[500])
        response.status_code = err.code
        return response

    @app.errorhandler(Exception)
    def unknown_error(err):
        current_app.logger.critical(traceback.format_exc())
        response = response_err(ErrCode.COMMON_INTERNAL_ERR)
        response.status_code = 500
        return response
