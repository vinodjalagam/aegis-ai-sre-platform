"""
HTTP request logging middleware.
"""

from __future__ import annotations

import time

from fastapi import Request, Response

from app.core.logging.logger import get_logger
from app.middleware.base import BaseMiddleware

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseMiddleware):
    """
    Logs every HTTP request and response.
    """

    async def before_request(self, request: Request) -> None:
        request.state.start_time = time.perf_counter()

    async def after_response(
        self,
        request: Request,
        response: Response,
    ) -> Response:

        start_time = getattr(request.state, "start_time", None)

        if start_time is not None:
            duration_ms = (time.perf_counter() - start_time) * 1000
        else:
            duration_ms = 0.0

        logger.info(
            "%s %s | %d | %.2f ms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response