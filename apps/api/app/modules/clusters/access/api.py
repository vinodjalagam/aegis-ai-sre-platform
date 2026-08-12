from __future__ import annotations
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security.dependencies import get_current_user_id
from app.db.session import get_db
from app.modules.clusters.access.repository import ClusterAccessRepository
from app.modules.clusters.access.service import ClusterAccessService
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/clusters/{cluster_id}/access",
    tags=["Cluster Access"],
)


class ClusterAccessCreate(BaseModel):
    user_id: str
    role: Literal["viewer", "admin", "owner"] = "viewer"


def get_access_service(
    db: AsyncSession = Depends(get_db),
) -> ClusterAccessService:
    repository = ClusterAccessRepository(db)
    return ClusterAccessService(repository)


@router.post("")
async def grant_cluster_access(
    cluster_id: str,
    payload: ClusterAccessCreate,
    current_user_id: str = Depends(get_current_user_id),
    service: ClusterAccessService = Depends(get_access_service),
):
    """
    Grant a user access to a Kubernetes cluster.

    Only cluster owners can grant access.
    """

    try:
        await service.require_access(
            current_user_id,
            cluster_id,
            ["owner"],
        )

        access = await service.grant_access(
            user_id=payload.user_id,
            cluster_id=cluster_id,
            role=payload.role,
        )

        return {
            "success": True,
            "data": {
                "id": access.id,
                "user_id": access.user_id,
                "cluster_id": access.cluster_id,
                "role": access.role,
            },
        }

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc