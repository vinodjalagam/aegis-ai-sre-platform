"""
Request ID middleware.

This middleware ensures every request has a unique request identifier.
"""

from __future__ import annotations

from fastapi import Request, Response

from app.middleware.base import BaseMiddleware
from app.middleware.request_context import RequestContext
from app.shared.constants.headers import REQUEST_ID_HEADER
from app.shared.helpers.id_generator import generate_request_id
from app.shared.validators.id_validator import is_request_id


class RequestIDMiddleware(BaseMiddleware):
    """
    Middleware responsible for managing request identifiers.
    """

    async def before_request(self, request: Request) -> None:
        """
        Resolve or generate the request identifier.
        """

        request_id = request.headers.get(REQUEST_ID_HEADER)

        if not request_id or not is_request_id(request_id):
            request_id = generate_request_id()

        RequestContext.set_request_id(request_id)

        request.state.request_id = request_id

    async def after_response(
        self,
        request: Request,
        response: Response,
    ) -> Response:
        """
        Add the request identifier to the response headers.
        """

        request_id = RequestContext.get_request_id()

        if request_id:
            response.headers[REQUEST_ID_HEADER] = request_id

        return response

    async def cleanup(self, request: Request) -> None:
        """
        Clear request-scoped context.
        """

        RequestContext.clear()