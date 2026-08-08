"""
Custom log formatter.
"""

from __future__ import annotations

import logging

from app.middleware.request_context import RequestContext


class AegisFormatter(logging.Formatter):
    """
    Custom formatter that injects request context into log records.
    """

    def format(self, record: logging.LogRecord) -> str:
        record.request_id = (
            RequestContext.get_request_id() or "-"
        )

        record.correlation_id = (
            RequestContext.get_correlation_id() or "-"
        )

        return super().format(record)