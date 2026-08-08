from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.models import Incident

from app.modules.incidents.enums import IncidentStatus
from app.modules.incidents.schemas import (
    IncidentCreate,
    IncidentUpdate,
)


class IncidentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        incident: IncidentCreate,
    ) -> Incident:

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

        result = await self.db.execute(
            select(Incident).where(
                Incident.id == incident_id
            )
        )

        return result.scalar_one_or_none()

    async def list(
        self,
    ) -> tuple[list[Incident], int]:

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

        await self.db.delete(incident)
        await self.db.commit()

    async def get_open_incident(
        self,
        title: str,
        resource_name: str,
    ) -> Incident | None:
        """
        Check whether an active OPEN incident
        already exists for the same resource.
        """

        result = await self.db.execute(
            select(Incident).where(
                Incident.title == title,
                Incident.resource_name == resource_name,
                Incident.status == "open",
                Incident.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()
    async def get_open_incidents(
        self,
        title: str,
    ) :
        """
        Return all open incidents for a rule.
        """

        result = await self.db.execute(
            select(Incident).where(
                Incident.title == title,
                Incident.status == IncidentStatus.OPEN,
                Incident.is_active.is_(True),
            )
        )

        return list(result.scalars().all())
    
    async def resolve(
        self,
        incident: Incident,
        ):
        """
        Mark incident as resolved.
        """

        incident.status = IncidentStatus.RESOLVED

        await self.db.commit()

        await self.db.refresh(incident)

        return incident