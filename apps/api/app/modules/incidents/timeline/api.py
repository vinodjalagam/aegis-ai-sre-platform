from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security.dependencies import get_current_user_id

from app.modules.clusters.access.repository import (
    ClusterAccessRepository,
)

from app.modules.incidents.timeline.schemas import (
    IncidentTimelineEventCreate,
    IncidentTimelineEventResponse,
)

from app.modules.incidents.timeline.service import (
    IncidentTimelineService,
)

from app.modules.incidents.service import IncidentService


router = APIRouter(
    prefix="/incidents",
    tags=["Incident Timeline"],
)


@router.get(
    "/{incident_id}/timeline",
    response_model=list[IncidentTimelineEventResponse],
)
async def list_incident_timeline(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    List timeline events only if the authenticated
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

    service = IncidentTimelineService(db)

    return await service.list_by_incident(
        incident_id
    )


@router.post(
    "/{incident_id}/timeline",
    response_model=IncidentTimelineEventResponse,
)
async def create_incident_timeline(
    incident_id: str,
    data: IncidentTimelineEventCreate,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a timeline event only if the authenticated
    user has owner/admin access to the incident's cluster.
    """

    incident_service = IncidentService(db)

    # ---------------------------------------------
    # 1. Verify incident belongs to accessible cluster
    # ---------------------------------------------

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
    # 2. Check cluster role
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
            detail="You do not have permission to create timeline events",
        )

    # ---------------------------------------------
    # 3. Create timeline event
    # ---------------------------------------------

    service = IncidentTimelineService(db)

    return await service.create(
        incident_id=incident_id,
        data=data,
    )