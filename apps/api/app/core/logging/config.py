"""
Logging configuration.
"""

from __future__ import annotations

import logging

LOG_LEVEL = logging.INFO

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(service)s | "
    "%(request_id)s | "
    "%(correlation_id)s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"