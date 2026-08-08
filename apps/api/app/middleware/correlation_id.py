"""
Correlation ID middleware.
"""

from fastapi import Request, Response

from app.middleware.base import BaseMiddleware
from app.middleware.request_context import RequestContext
from app.shared.constants.headers import CORRELATION_ID_HEADER
from app.shared.helpers.id_generator import generate_correlation_id
from app.shared.validators.id_validator import is_correlation_id


class CorrelationIDMiddleware(BaseMiddleware):

    async def before_request(self, request: Request) -> None:

        correlation_id = request.headers.get(CORRELATION_ID_HEADER)

        if not correlation_id or not is_correlation_id(correlation_id):
            correlation_id = generate_correlation_id()

        RequestContext.set_correlation_id(correlation_id)

        request.state.correlation_id = correlation_id

    async def after_response(
        self,
        request: Request,
        response: Response,
    ) -> Response:

        correlation_id = RequestContext.get_correlation_id()

        if correlation_id:
            response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response