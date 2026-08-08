from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security.dependencies import get_current_user_id
from app.modules.discovery.dependencies import get_discovery_service
from app.modules.discovery.service import DiscoveryService
from app.shared.responses.success import success_response


router = APIRouter(
    prefix="/discovery",
    tags=["Discovery"],
)


@router.post("/{cluster_id}")
async def discover_cluster(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    discovery_service: DiscoveryService = Depends(get_discovery_service),
):
    """
    Discover platform services installed in a cluster.
    """

    try:
        result = discovery_service.discover()
        return success_response(result)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc