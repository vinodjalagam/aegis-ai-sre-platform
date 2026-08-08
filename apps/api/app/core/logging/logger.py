"""
Central logging configuration.
"""

from __future__ import annotations

import logging
import sys

from app.core.logging.config import (
    DATE_FORMAT,
    LOG_FORMAT,
    LOG_LEVEL,
)
from app.core.logging.filters import AegisLogFilter
from app.core.logging.formatter import AegisFormatter


def configure_logging() -> None:
    """
    Configure the root logger.
    """

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        AegisFormatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
    )

    handler.addFilter(AegisLogFilter())

    root_logger = logging.getLogger()

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(LOG_LEVEL)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.
    """

    return logging.getLogger(name)