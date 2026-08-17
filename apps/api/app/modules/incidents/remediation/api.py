from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.incidents.remediation.schemas import (
    IncidentRemediationResponse,
)
from app.modules.incidents.remediation.service import (
    IncidentRemediationService,
)
from app.shared.responses.success import success_response


router = APIRouter(
    prefix="/incidents",
    tags=["Incident Remediation"],
)


@router.get(
    "/{incident_id}/remediations",
)
async def list_remediations(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Return remediation history for an incident.
    """

    service = IncidentRemediationService(db)

    remediations = await service.list_by_incident(
        incident_id
    )

    return success_response(
        [
            IncidentRemediationResponse.model_validate(
                remediation
            )
            for remediation in remediations
        ]
    )
