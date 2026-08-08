"""
Middleware registration.
"""

from fastapi import FastAPI

from app.middleware.correlation_id import CorrelationIDMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

def register_middlewares(app: FastAPI) -> None:
    """
    Register all middleware in execution order.
    """

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(RequestIDMiddleware)