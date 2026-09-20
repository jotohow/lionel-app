import logging

from db import next_gameweek


def setup_logger(name):
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


def get_gameweek() -> int:
    gameweek, _ = next_gameweek()
    return gameweek
