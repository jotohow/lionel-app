import logging

from connector import get_player_preds


def setup_logger(name):
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


def get_gameweek() -> int:
    df = get_player_preds()
    return int(df["gameweek"].max())
