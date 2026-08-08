"""
Incident service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.repository import IncidentRepository
from app.modules.incidents.schemas import (
    IncidentCreate,
    IncidentUpdate,
)
from app.modules.incidents.timeline.service import (
    IncidentTimelineService,
)
from app.modules.incidents.timeline.schemas import (
    IncidentTimelineEventCreate,
)


class IncidentService:
    """
    Business logic for incidents.
    """

    def __init__(self, db: AsyncSession):
        self.repository = IncidentRepository(db)
        self.timeline_service = IncidentTimelineService(db)

    async def create_incident(self, incident: IncidentCreate):
        return await self.repository.create(incident)

    async def get_incident(self, incident_id: str):
        return await self.repository.get_by_id(incident_id)

    async def list_incidents(self):
        return await self.repository.list()

    async def update_incident(
        self,
        incident_id: str,
        data: IncidentUpdate,
    ):
        incident = await self.repository.get_by_id(incident_id)

        if incident is None:
            return None

        return await self.repository.update(incident, data)

    async def delete_incident(self, incident_id: str):
        incident = await self.repository.get_by_id(incident_id)

        if incident is None:
            return False

        await self.repository.delete(incident)
        return True
    
    async def resolve_incident(
        self,
        incident,
    ):
        """
        Resolve an incident.
        """

        resolved = await self.repository.resolve(
            incident
        )

        await self.timeline_service.create(
            incident_id=incident.id,
            data=IncidentTimelineEventCreate(
                event_type="resolved",
                title="Incident resolved",
                description="Incident manually resolved",
            ),
        )

        return resolved
        
    async def acknowledge_incident(
        self,
        incident,
    ):
        """
        Acknowledge an incident.
        """

        acknowledged = await self.repository.acknowledge(
            incident
        )

        await self.timeline_service.create(
            incident_id=incident.id,
            data=IncidentTimelineEventCreate(
                event_type="acknowledged",
                title="Incident acknowledged",
                description="Incident acknowledged by user",
            ),
        )

        return acknowledged
    
    async def auto_resolve_incident(
        self,
        incident,
    ):
        """
        Automatically resolve an incident when
        the Prometheus rule is no longer triggered.
        """

        resolved = await self.repository.resolve(
            incident
        )

        await self.timeline_service.create(
            incident_id=incident.id,
            data=IncidentTimelineEventCreate(
                event_type="resolved",
                title="Incident resolved",
                description="Incident automatically resolved because the rule is no longer triggered",
            ),
        )

        return resolved