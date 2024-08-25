import logging
import sys


def get_logger(name: str, stream=sys.stdout):
    formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
    )
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name=name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
