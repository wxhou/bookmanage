import logging
from logging.handlers import RotatingFileHandler


def register_logger(app):
    # 配置flask自带日志
    logger_level = {
        'DEBUG': logging.DEBUG,
        'ERROR': logging.ERROR,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'CRITICAL': logging.CRITICAL
    }
    file_handler = RotatingFileHandler(filename=app.config['LOGGER_FILE'],
                                       maxBytes=10 * 1024 * 1024,
                                       backupCount=10)
    formatter = logging.Formatter(app.config['LOGGER_FORMATTER'])
    file_handler.setFormatter(formatter)
    app.logger.setLevel(logger_level[app.config['LOGGER_LEVEL']])
    app.logger.addHandler(file_handler)

    # 其他日志
    socket_handler = RotatingFileHandler(
        filename=app.config['LOGGER_FILE_WEBSOCKET'],
        maxBytes=10 * 1024 * 1024,
        backupCount=10)
    formatter = logging.Formatter(app.config['LOGGER_FORMATTER'])
    socket_handler.setFormatter(formatter)
    socket_handler.setLevel(logger_level[app.config['LOGGER_LEVEL']])
    websocket_logger = logging.getLogger('websocket')
    websocket_logger.addHandler(socket_handler)

    # celery日志
    handler = RotatingFileHandler(filename=app.config['LOGGER_FILE_CELERY'],
                                  maxBytes=10 * 1024 * 1024,
                                  backupCount=10)
    formatter = logging.Formatter(app.config['LOGGER_FORMATTER'])
    handler.setFormatter(formatter)
    handler.setLevel(logger_level[app.config['LOGGER_LEVEL']])
    celery_logger = logging.getLogger('celery')
    celery_logger.addHandler(celery_logger)
