"""
Incident service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.repository import IncidentRepository
from app.modules.incidents.schemas import (
    IncidentCreate,
    IncidentUpdate,
)


class IncidentService:
    """
    Business logic for incidents.
    """

    def __init__(self, db: AsyncSession):
        self.repository = IncidentRepository(db)

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

        return await self.repository.resolve(
            incident
        )