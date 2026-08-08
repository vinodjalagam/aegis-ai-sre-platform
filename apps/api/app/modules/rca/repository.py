"""
Root cause analysis repository.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rca.models import IncidentRCA


class RCARepository:
    """
    Database operations for RCA.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        rca: IncidentRCA,
    ) -> IncidentRCA:
        """
        Create and persist an RCA result.
        """

        self.db.add(rca)

        await self.db.commit()
        await self.db.refresh(rca)

        return rca

    async def get_by_incident(
        self,
        incident_id: str,
    ) -> IncidentRCA | None:
        """
        Return RCA for an incident.
        """

        result = await self.db.execute(
            select(IncidentRCA).where(
                IncidentRCA.incident_id == incident_id
            )
        )

        return result.scalar_one_or_none()

    async def delete(
        self,
        rca: IncidentRCA,
    ) -> None:
        """
        Delete an RCA result.
        """

        await self.db.delete(rca)
        await self.db.commit()