"""Centralized application logging."""

import logging
import os

from ufc_predictor.config import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(settings.LOG_LEVEL)
    formatter = logging.Formatter(settings.LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(settings.LOG_LEVEL)

    logger.addHandler(stream_handler)
    if os.getenv("RENDER") != "true":
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(settings.APP_LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(settings.LOG_LEVEL)
        logger.addHandler(file_handler)
    return logger
