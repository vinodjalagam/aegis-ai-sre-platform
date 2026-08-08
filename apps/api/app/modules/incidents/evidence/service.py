"""
Incident evidence service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.evidence.models import IncidentEvidence
from app.modules.incidents.evidence.repository import (
    IncidentEvidenceRepository,
)
from app.modules.incidents.evidence.schemas import (
    IncidentEvidenceCreate,
)


class IncidentEvidenceService:
    """
    Business logic for incident evidence.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.repository = IncidentEvidenceRepository(db)

    async def create(
        self,
        incident_id: str,
        data: IncidentEvidenceCreate,
    ) -> IncidentEvidence:
        """
        Create evidence for an incident.
        """

        evidence = IncidentEvidence(
            incident_id=incident_id,
            **data.model_dump(),
        )

        return await self.repository.create(
            evidence
        )

    async def list_by_incident(
        self,
        incident_id: str,
    ) -> list[IncidentEvidence]:
        """
        Return all evidence for an incident.
        """

        return await self.repository.list_by_incident(
            incident_id
        )