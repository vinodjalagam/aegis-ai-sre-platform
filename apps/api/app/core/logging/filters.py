"""
Logging filters.
"""

from __future__ import annotations

import logging

from app.core.config import settings


class AegisLogFilter(logging.Filter):
    """
    Inject application metadata into log records.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.service = settings.app_name
        record.environment = settings.app_env

        return True