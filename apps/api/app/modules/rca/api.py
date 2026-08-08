"""
Root cause analysis API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.rca.service import RCAService
from app.modules.rca.schemas import (
    RCAAnalysisResponse,
    RCAResponse,
)

router = APIRouter(
    prefix="/incidents",
    tags=["Root Cause Analysis"],
)


@router.get(
    "/{incident_id}/rca",
    response_model=RCAResponse,
)
async def get_incident_rca(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get RCA for an incident.
    """

    service = RCAService(db)

    rca = await service.get_by_incident(
        incident_id
    )

    if rca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RCA not found for incident",
        )

    return rca
@router.post(
    "/{incident_id}/rca/analyze",
    response_model=RCAAnalysisResponse,
)
async def analyze_incident_rca(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate RCA for an incident.
    """

    service = RCAService(db)

    try:
        return await service.analyze_incident(
            incident_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )