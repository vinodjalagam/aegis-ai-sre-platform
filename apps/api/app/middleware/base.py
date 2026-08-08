"""
Base middleware implementation for the Aegis API.
"""

from __future__ import annotations

from abc import ABC
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

RequestHandler = Callable[[Request], Awaitable[Response]]


class BaseMiddleware(BaseHTTPMiddleware, ABC):
    """
    Base class for all HTTP middleware in the platform.

    Every middleware should inherit from this class to ensure
    a consistent lifecycle.
    """

    async def before_request(self, request: Request) -> None:
        """Executed before the request reaches the route."""
        return None

    async def after_response(
        self,
        request: Request,
        response: Response,
    ) -> Response:
        """Executed before sending the response."""
        return response

    async def cleanup(self, request: Request) -> None:
        """Executed after the response (or exception)."""
        return None

    async def dispatch(
        self,
        request: Request,
        call_next: RequestHandler,
    ) -> Response:
        """
        Middleware execution pipeline.
        """
        await self.before_request(request)

        try:
            response = await call_next(request)
            response = await self.after_response(request, response)
            return response
        finally:
            await self.cleanup(request)