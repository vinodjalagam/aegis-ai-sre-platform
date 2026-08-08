from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.timeline.models import IncidentTimelineEvent


class IncidentTimelineRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        event: IncidentTimelineEvent,
    ) -> IncidentTimelineEvent:

        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def list_by_incident(
        self,
        incident_id: str,
    ) -> list[IncidentTimelineEvent]:

        result = await self.db.execute(
            select(IncidentTimelineEvent)
            .where(
                IncidentTimelineEvent.incident_id == incident_id
            )
            .order_by(
                IncidentTimelineEvent.created_at.asc()
            )
        )

        return list(result.scalars().all())

    async def delete(
        self,
        event: IncidentTimelineEvent,
    ) -> None:

        await self.db.delete(event)
        await self.db.commit()
