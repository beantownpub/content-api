import logging


FORMATTER = logging.Formatter(
    "{\"timestamp\": \"%(asctime)s\", \"level\": \"%(levelname)s\", \"module\": \"%(module)s\", \"function\": \"%(funcName)s\", \"message\": \"%(message)s\"}", "%Y-%m-%d %H:%M:%S"
)


def init_logger(log_level=None):
    if __name__ != "__main__":
        app_log = logging.getLogger()
        gunicorn_logger = logging.getLogger("gunicorn.error")
        gunicorn_logger.handlers = []
        app_log.handlers = gunicorn_logger.handlers
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(FORMATTER)
        app_log.addHandler(stream_handler)
        if log_level:
            app_log.setLevel(log_level)
        else:
            app_log.setLevel("INFO")
        return app_log
