from __future__ import annotations

from app.middleware.context import (
    correlation_id_ctx,
    request_id_ctx,
    span_id_ctx,
    tenant_id_ctx,
    trace_id_ctx,
    user_id_ctx,
)


class RequestContext:
    """Utility class for accessing request-scoped context."""

    @staticmethod
    def set_request_id(value: str) -> None:
        request_id_ctx.set(value)

    @staticmethod
    def get_request_id() -> str | None:
        return request_id_ctx.get()

    @staticmethod
    def set_correlation_id(value: str) -> None:
        correlation_id_ctx.set(value)

    @staticmethod
    def get_correlation_id() -> str | None:
        return correlation_id_ctx.get()

    @staticmethod
    def set_user_id(value: str) -> None:
        user_id_ctx.set(value)

    @staticmethod
    def get_user_id() -> str | None:
        return user_id_ctx.get()

    @staticmethod
    def set_tenant_id(value: str) -> None:
        tenant_id_ctx.set(value)

    @staticmethod
    def get_tenant_id() -> str | None:
        return tenant_id_ctx.get()

    @staticmethod
    def set_trace_id(value: str) -> None:
        trace_id_ctx.set(value)

    @staticmethod
    def get_trace_id() -> str | None:
        return trace_id_ctx.get()

    @staticmethod
    def set_span_id(value: str) -> None:
        span_id_ctx.set(value)

    @staticmethod
    def get_span_id() -> str | None:
        return span_id_ctx.get()

    @staticmethod
    def clear() -> None:
        """Clear all request-scoped values."""

        request_id_ctx.set(None)
        correlation_id_ctx.set(None)
        user_id_ctx.set(None)
        tenant_id_ctx.set(None)
        trace_id_ctx.set(None)
        span_id_ctx.set(None)