"""
Root cause analysis API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security.dependencies import get_current_user_id

from app.modules.clusters.access.repository import (
    ClusterAccessRepository,
)

from app.modules.incidents.service import IncidentService
from app.modules.rca.service import RCAService
from app.modules.rca.schemas import (
    RCAAnalysisResponse,
    RCAResponse,
)


router = APIRouter(
    prefix="/incidents",
    tags=["Root Cause Analysis"],
)


@router.get(
    "/{incident_id}/rca",
    response_model=RCAResponse,
)
async def get_incident_rca(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get RCA for an incident only if the authenticated
    user has access to the incident's cluster.
    """

    incident_service = IncidentService(db)

    incident = await incident_service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    service = RCAService(db)

    rca = await service.get_by_incident(
        incident_id
    )

    if rca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RCA not found for incident",
        )

    return rca


@router.post(
    "/{incident_id}/rca/analyze",
    response_model=RCAAnalysisResponse,
)
async def analyze_incident_rca(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate RCA only if the authenticated user has
    owner/admin access to the incident's cluster.
    """

    incident_service = IncidentService(db)

    incident = await incident_service.get_user_incident(
        user_id=current_user_id,
        incident_id=incident_id,
        cluster_id=cluster_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or you do not have access",
        )

    # ---------------------------------------------
    # Check cluster role
    # ---------------------------------------------

    access_repository = ClusterAccessRepository(db)

    access = await access_repository.get(
        current_user_id,
        cluster_id,
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    if access.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to analyze incidents",
        )

    # ---------------------------------------------
    # Generate RCA
    # ---------------------------------------------

    service = RCAService(db)

    try:
        return await service.analyze_incident(
            incident_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc