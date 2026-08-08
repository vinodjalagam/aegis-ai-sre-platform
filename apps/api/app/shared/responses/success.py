"""
Success response models.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from app.shared.responses.response import ApiResponse

T = TypeVar("T")


class SuccessResponse(ApiResponse[T], Generic[T]):
    """
    Standard success response.
    """

    success: bool = True


def success_response(data: T) -> SuccessResponse[T]:
    """
    Helper to return a standard success response.
    """
    return SuccessResponse(
        success=True,
        data=data,
    )