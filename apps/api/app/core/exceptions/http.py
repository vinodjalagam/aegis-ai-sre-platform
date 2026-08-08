"""
Common HTTP application exceptions.
"""

from __future__ import annotations

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from app.core.exceptions.base import AppException
from app.core.exceptions.codes import ErrorCode


class BadRequestException(AppException):
    """400 Bad Request."""

    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(
            message=message,
            error_code=ErrorCode.BAD_REQUEST,
            status_code=HTTP_400_BAD_REQUEST,
        )


class UnauthorizedException(AppException):
    """401 Unauthorized."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    """403 Forbidden."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=HTTP_403_FORBIDDEN,
        )


class NotFoundException(AppException):
    """404 Not Found."""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            message=f"{resource} not found",
            error_code=ErrorCode.NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
        )


class ConflictException(AppException):
    """409 Conflict."""

    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFLICT,
            status_code=HTTP_409_CONFLICT,
        )