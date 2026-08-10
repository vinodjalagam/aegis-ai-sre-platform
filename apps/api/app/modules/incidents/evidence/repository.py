"""
Incident evidence repository.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.evidence.models import IncidentEvidence


class IncidentEvidenceRepository:
    """
    Database operations for incident evidence.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        evidence: IncidentEvidence,
    ) -> IncidentEvidence:
        """
        Create and persist incident evidence.
        """

        self.db.add(evidence)

        await self.db.commit()

        await self.db.refresh(evidence)

        return evidence

    async def list_by_incident(
        self,
        incident_id: str,
    ) -> list[IncidentEvidence]:
        """
        Return all evidence belonging to an incident.
        """

        result = await self.db.execute(
            select(IncidentEvidence)
            .where(
                IncidentEvidence.incident_id == incident_id
            )
            .order_by(
                IncidentEvidence.created_at.asc()
            )
        )

        return list(
            result.scalars().all()
        )
    async def exists(
        self,
        incident_id: str,
        evidence_type: str,
        title: str,
        resource_name: str | None = None,
    ) -> bool:
        """
        Check whether equivalent evidence already exists
        for an incident.
        """

        result = await self.db.execute(
            select(IncidentEvidence.id)
            .where(
                IncidentEvidence.incident_id == incident_id,
                IncidentEvidence.evidence_type == evidence_type,
                IncidentEvidence.title == title,
                IncidentEvidence.resource_name == resource_name,
            )
            .limit(1)
        )

        return result.scalar_one_or_none() is not None

    async def delete(
        self,
        evidence: IncidentEvidence,
    ) -> None:
        """
        Delete incident evidence.
        """

        await self.db.delete(evidence)

        await self.db.commit()