import logging

time_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(name)s: %(message)s", datefmt=time_format
)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
