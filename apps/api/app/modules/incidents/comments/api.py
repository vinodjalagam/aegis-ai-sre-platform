"""
Incident comments API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import get_current_user_id
from app.db.session import get_db
from app.modules.incidents.comments.schemas import (
    IncidentCommentCreate,
    IncidentCommentResponse,
)
from app.modules.incidents.comments.service import (
    IncidentCommentService,
)

router = APIRouter(
    prefix="/incidents",
    tags=["Incident Comments"],
)


@router.post(
    "/{incident_id}/comments",
    response_model=IncidentCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    incident_id: str,
    data: IncidentCommentCreate,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a comment to an incident.
    """

    service = IncidentCommentService(db)

    try:
        return await service.create_comment(
            incident_id=incident_id,
            user_id=current_user_id,
            data=data,
        )
    except ValueError as exc:
        if str(exc) == "Incident not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{incident_id}/comments",
    response_model=list[IncidentCommentResponse],
)
async def list_comments(
    incident_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    List comments for an incident.
    """

    service = IncidentCommentService(db)

    try:
        return await service.list_comments(
            incident_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
