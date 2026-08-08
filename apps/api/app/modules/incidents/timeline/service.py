from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.timeline.models import IncidentTimelineEvent
from app.modules.incidents.timeline.repository import (
    IncidentTimelineRepository,
)
from app.modules.incidents.timeline.schemas import (
    IncidentTimelineEventCreate,
)


class IncidentTimelineService:

    def __init__(self, db: AsyncSession):
        self.repository = IncidentTimelineRepository(db)

    async def create(
        self,
        incident_id: str,
        data: IncidentTimelineEventCreate,
    ) -> IncidentTimelineEvent:

        event = IncidentTimelineEvent(
            incident_id=incident_id,
            **data.model_dump(),
        )

        return await self.repository.create(event)

    async def list_by_incident(
        self,
        incident_id: str,
    ) -> list[IncidentTimelineEvent]:

        return await self.repository.list_by_incident(
            incident_id
        )
