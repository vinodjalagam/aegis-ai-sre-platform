from fastapi import APIRouter

from app.core.logging.logger import get_logger
from app.shared.responses.success import SuccessResponse

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health Check",
    response_model=SuccessResponse[dict[str, str]],
)
async def health() -> SuccessResponse[dict[str, str]]:
    """
    Basic health endpoint.
    """

    logger.info("Health endpoint called")

    return SuccessResponse(
        data={
            "status": "healthy",
            "service": "aegis-api",
        }
    )