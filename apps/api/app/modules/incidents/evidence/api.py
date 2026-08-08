from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.incidents.evidence.schemas import (
    IncidentEvidenceResponse,
)
from app.modules.incidents.evidence.service import (
    IncidentEvidenceService,
)

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
    db: AsyncSession = Depends(get_db),
):
    service = IncidentEvidenceService(db)

    return await service.list_by_incident(
        incident_id
    )