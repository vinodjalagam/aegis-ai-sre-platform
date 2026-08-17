import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.remediation.models import (
    IncidentRemediation,
)
from app.modules.incidents.remediation.repository import (
    IncidentRemediationRepository,
)
from app.modules.incidents.remediation.schemas import (
    IncidentRemediationCreate,
)


class IncidentRemediationService:

    def __init__(self, db: AsyncSession):
        self.repository = IncidentRemediationRepository(db)

    async def create(
        self,
        incident_id: str,
        data: IncidentRemediationCreate,
    ) -> IncidentRemediation:

        remediation = IncidentRemediation(
            incident_id=incident_id,
            **data.model_dump(),
        )

        return await self.repository.create(
            remediation
        )

    async def record_result(
        self,
        remediation_id: str,
        *,
        applied: bool,
        status: str,
        message: str | None = None,
        rollout: dict | None = None,
        verification: dict | None = None,
    ) -> IncidentRemediation | None:

        remediation = await self.repository.get_by_id(
            remediation_id
        )

        if remediation is None:
            return None

        remediation.applied = applied
        remediation.status = status
        remediation.message = message

        remediation.rollout_json = (
            json.dumps(rollout)
            if rollout is not None
            else None
        )

        remediation.verification_json = (
            json.dumps(verification)
            if verification is not None
            else None
        )

        return await self.repository.update(
            remediation
        )

    async def list_by_incident(
        self,
        incident_id: str,
    ) -> list[IncidentRemediation]:

        return await self.repository.list_by_incident(
            incident_id
        )
