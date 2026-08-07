from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
async def health() -> dict[str, str]:
    """
    Basic health endpoint.
    """
    return {
        "status": "healthy",
        "service": "aegis-api",
    }