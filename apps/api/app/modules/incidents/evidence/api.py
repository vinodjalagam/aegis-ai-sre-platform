from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security.dependencies import get_current_user_id

from app.modules.incidents.evidence.schemas import (
    IncidentEvidenceResponse,
)
from app.modules.incidents.evidence.service import (
    IncidentEvidenceService,
)
from app.modules.incidents.service import IncidentService


router = APIRouter(
    prefix="/incidents",
    tags=["Incident Evidence"],
)


@router.get(
    "/{incident_id}/evidence",
    response_model=list[IncidentEvidenceResponse],
)
async def list_incident_evidence(
    incident_id: str,
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    List incident evidence only if the authenticated
    user has access to the incident's cluster.
    """

    # ---------------------------------------------
    # 1. Verify incident belongs to accessible cluster
    # ---------------------------------------------

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
    # 2. Get evidence
    # ---------------------------------------------

    service = IncidentEvidenceService(db)

    return await service.list_by_incident(
        incident_id
    )