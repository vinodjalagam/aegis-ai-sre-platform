"""
Incident repository.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.enums import IncidentStatus
from app.modules.incidents.models import Incident
from app.modules.incidents.schemas import (
    IncidentCreate,
    IncidentUpdate,
)


class IncidentRepository:
    """
    Database operations for incidents.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        incident: IncidentCreate,
    ) -> Incident:
        """
        Create a new incident.
        """

        db_incident = Incident(
            **incident.model_dump()
        )

        self.db.add(db_incident)

        await self.db.commit()
        await self.db.refresh(db_incident)

        return db_incident

    async def get_by_id(
        self,
        incident_id: str,
    ) -> Incident | None:
        """
        Get an incident by ID.
        """

        result = await self.db.execute(
            select(Incident).where(
                Incident.id == incident_id
            )
        )

        return result.scalar_one_or_none()

    async def list(
        self,
    ) -> tuple[list[Incident], int]:
        """
        Return all incidents and total count.
        """

        result = await self.db.execute(
            select(Incident).order_by(
                Incident.created_at.desc()
            )
        )

        incidents = result.scalars().all()

        total = await self.db.scalar(
            select(func.count()).select_from(
                Incident
            )
        )

        return incidents, total or 0

    async def update(
        self,
        incident: Incident,
        data: IncidentUpdate,
    ) -> Incident:
        """
        Update an existing incident.
        """

        values = data.model_dump(
            exclude_unset=True
        )

        for key, value in values.items():
            setattr(
                incident,
                key,
                value,
            )

        await self.db.commit()
        await self.db.refresh(incident)

        return incident

    async def delete(
        self,
        incident: Incident,
    ) -> None:
        """
        Delete an incident.
        """

        await self.db.delete(incident)
        await self.db.commit()

    async def get_open_incident(
        self,
        title: str,
        resource_name: str,
    ) -> Incident | None:
        """
        Return an active OPEN incident for the
        same rule and resource.
        """

        result = await self.db.execute(
            select(Incident).where(
                Incident.title == title,
                Incident.resource_name == resource_name,
                Incident.status.in_(
                    [
                        IncidentStatus.OPEN,
                        IncidentStatus.ACKNOWLEDGED,
                    ]
                ),
                Incident.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()

    async def get_open_incidents(
        self,
        title: str,
    ) -> list[Incident]:
        """
        Return all active OPEN incidents for a rule.
        """

        result = await self.db.execute(
            select(Incident).where(
                Incident.title == title,
                Incident.status.in_(
                    [
                        IncidentStatus.OPEN,
                        IncidentStatus.ACKNOWLEDGED,
                    ]
                ),
                Incident.is_active.is_(True),
            )
        )

        return list(
            result.scalars().all()
        )

    async def resolve(
        self,
        incident: Incident,
    ) -> Incident:
        """
        Mark an incident as resolved and inactive.
        """

        incident.status = IncidentStatus.RESOLVED
        incident.is_active = False

        await self.db.commit()
        await self.db.refresh(incident)

        return incident
    
    
    async def acknowledge(
        self,
        incident: Incident,
    ) -> Incident:
        """
        Mark an incident as acknowledged.
        """

        incident.status = IncidentStatus.ACKNOWLEDGED

        await self.db.commit()
        await self.db.refresh(incident)

        return incident
    
    async def assign(
        self,
        incident: Incident,
        user_id: str | None,
    ) -> Incident:
        """
        Assign or unassign an incident.
        """

        incident.assigned_to = user_id

        await self.db.commit()
        await self.db.refresh(incident)

        return incident
    
    async def get_by_id_for_cluster(
        self,
        incident_id: str,
        cluster_id: str,
    ) -> Incident | None:
        """
        Get an incident only if it belongs to the selected cluster.
        """

        result = await self.db.execute(
            select(Incident).where(
                Incident.id == incident_id,
                Incident.cluster_id == cluster_id,
            )
        )

        return result.scalar_one_or_none()


    async def list_for_cluster(
        self,
        cluster_id: str,
    ) -> tuple[list[Incident], int]:
        """
        Return incidents belonging to a cluster.
        """

        result = await self.db.execute(
            select(Incident)
            .where(Incident.cluster_id == cluster_id)
            .order_by(Incident.created_at.desc())
        )

        incidents = list(result.scalars().all())

        total = await self.db.scalar(
            select(func.count())
            .select_from(Incident)
            .where(Incident.cluster_id == cluster_id)
        )

        return incidents, total or 0