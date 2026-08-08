from __future__ import annotations

from contextvars import ContextVar
from typing import Optional


# Request-scoped context variables
request_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "request_id",
    default=None,
)

correlation_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "correlation_id",
    default=None,
)

user_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "user_id",
    default=None,
)

tenant_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "tenant_id",
    default=None,
)

trace_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "trace_id",
    default=None,
)

span_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "span_id",
    default=None,
)