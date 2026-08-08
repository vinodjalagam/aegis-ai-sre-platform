"""
Incident API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.incidents.schemas import (
    IncidentCreate,
    IncidentUpdate,
)
from app.modules.incidents.service import IncidentService

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    incident: IncidentCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new incident.
    """

    service = IncidentService(db)

    created = await service.create_incident(incident)

    return {
        "success": True,
        "data": created,
    }


@router.get("")
async def list_incidents(
    db: AsyncSession = Depends(get_db),
):
    """
    List all incidents.
    """

    service = IncidentService(db)

    incidents, total = await service.list_incidents()

    return {
        "success": True,
        "data": {
            "items": incidents,
            "total": total,
        },
    }


@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single incident.
    """

    service = IncidentService(db)

    incident = await service.get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return {
        "success": True,
        "data": incident,
    }


@router.patch("/{incident_id}")
async def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an incident.
    """

    service = IncidentService(db)

    incident = await service.update_incident(
        incident_id,
        data,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return {
        "success": True,
        "data": incident,
    }


@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an incident.
    """

    service = IncidentService(db)

    deleted = await service.delete_incident(
        incident_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return {
        "success": True,
        "message": "Incident deleted successfully",
    }