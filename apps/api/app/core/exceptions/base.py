"""
Base application exception.
"""

from __future__ import annotations

from app.core.exceptions.codes import ErrorCode


class AppException(Exception):
    """
    Base exception for the application.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.status_code = status_code