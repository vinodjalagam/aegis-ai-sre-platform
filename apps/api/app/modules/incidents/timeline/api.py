from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.incidents.timeline.schemas import (
    IncidentTimelineEventCreate,
    IncidentTimelineEventResponse,
)
from app.modules.incidents.timeline.service import (
    IncidentTimelineService,
)

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
    db: AsyncSession = Depends(get_db),
):
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
    db: AsyncSession = Depends(get_db),
):
    service = IncidentTimelineService(db)

    return await service.create(
        incident_id=incident_id,
        data=data,
    )