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
from app.modules.users.repository import UserRepository

class IncidentService:
    """
    Business logic for incidents.
    """

    def __init__(self, db: AsyncSession):
        self.repository = IncidentRepository(db)
        self.timeline_service = IncidentTimelineService(db)
        self.user_repository = UserRepository(db)
        
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
        Automatically resolve an incident after
        successful remediation verification.
        """

        resolved = await self.repository.resolve(
            incident
        )

        await self.timeline_service.create(
            incident_id=incident.id,
            data=IncidentTimelineEventCreate(
                event_type="resolved",
                title="Incident resolved",
                description=(
                    "Incident automatically resolved after "
                    "successful remediation and verification."
                ),
            ),
        )

        return resolved
    
    async def assign_incident(
        self,
        incident,
        user_id: str | None,
    ):
        """
        Assign or unassign an incident.
        """

        previous_user_id = incident.assigned_to

        if user_id is not None:
            user = await self.user_repository.get_by_id(user_id)

            if user is None:
                raise ValueError("User not found")

            if not user.is_active:
                raise ValueError("User is inactive")

        assigned = await self.repository.assign(
            incident,
            user_id,
        )

        if user_id is not None:
            event_type = "assigned"
            title = "Incident assigned"
            description = (
                f"Incident assigned to user {user_id}"
            )
        else:
            event_type = "unassigned"
            title = "Incident unassigned"
            description = "Incident assignment removed"

        await self.timeline_service.create(
            incident_id=incident.id,
            data=IncidentTimelineEventCreate(
                event_type=event_type,
                title=title,
                description=description,
            ),
        )

        return assigned
    
    async def get_user_incident(
        self,
        user_id: str,
        incident_id: str,
        cluster_id: str,
    ):
        """
        Return an incident only if the user has access
        to the cluster that owns the incident.
        """

        from app.modules.clusters.access.repository import (
            ClusterAccessRepository,
        )

        access_repository = ClusterAccessRepository(
            self.repository.db
        )

        access = await access_repository.get(
            user_id,
            cluster_id,
        )

        if access is None:
            return None

        return await self.repository.get_by_id_for_cluster(
            incident_id,
            cluster_id,
        )


    async def list_user_incidents(
        self,
        user_id: str,
        cluster_id: str,
    ):
        """
        Return incidents only from a cluster the user can access.
        """

        from app.modules.clusters.access.repository import (
            ClusterAccessRepository,
        )

        access_repository = ClusterAccessRepository(
            self.repository.db
        )

        access = await access_repository.get(
            user_id,
            cluster_id,
        )

        if access is None:
            return [], 0

        return await self.repository.list_for_cluster(
            cluster_id
        )