"""
Incident comment schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentCommentCreate(BaseModel):
    """
    Schema for creating an incident comment.
    """

    content: str


class IncidentCommentResponse(BaseModel):
    """
    Incident comment response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    incident_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime
