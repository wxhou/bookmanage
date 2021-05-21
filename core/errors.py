import traceback
from flask import current_app
from .utils import response_err, ErrCode, HTTP_STATUS_CODES


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return response_err(400, msg=HTTP_STATUS_CODES[400])

    @app.errorhandler(404)
    def page_not_found(e):
        return response_err(ErrCode.COMMON_NOT_FOUND,
                            msg=HTTP_STATUS_CODES[404])

    @app.errorhandler(429)
    def to_many_request(e):
        return response_err(429, msg=HTTP_STATUS_CODES[429])

    @app.errorhandler(500)
    def internal_server_error(e):
        current_app.logger.critical(traceback.format_exc())
        return response_err(500, msg=HTTP_STATUS_CODES[500])

    @app.errorhandler(Exception)
    def unknown_error(e):
        current_app.logger.critical(traceback.format_exc())
        return response_err(ErrCode.COMMON_DB_ERROR, msg='Unknown Error')