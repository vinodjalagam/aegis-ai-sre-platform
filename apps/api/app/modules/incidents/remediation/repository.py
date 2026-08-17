from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.remediation.models import (
    IncidentRemediation,
)


class IncidentRemediationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        remediation: IncidentRemediation,
    ) -> IncidentRemediation:

        self.db.add(remediation)

        await self.db.commit()
        await self.db.refresh(remediation)

        return remediation

    async def get_by_id(
        self,
        remediation_id: str,
    ) -> IncidentRemediation | None:

        result = await self.db.execute(
            select(IncidentRemediation)
            .where(
                IncidentRemediation.id == remediation_id
            )
        )

        return result.scalar_one_or_none()

    async def list_by_incident(
        self,
        incident_id: str,
    ) -> list[IncidentRemediation]:

        result = await self.db.execute(
            select(IncidentRemediation)
            .where(
                IncidentRemediation.incident_id
                == incident_id
            )
            .order_by(
                IncidentRemediation.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def update(
        self,
        remediation: IncidentRemediation,
    ) -> IncidentRemediation:

        await self.db.commit()
        await self.db.refresh(remediation)

        return remediation
