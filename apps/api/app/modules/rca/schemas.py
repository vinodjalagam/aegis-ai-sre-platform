"""
Root cause analysis schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

class RCACreate(BaseModel):
    """
    Schema for creating an RCA result.
    """

    root_cause: str
    summary: str | None = None
    confidence: float | None = None
    status: str = "completed"
    recommendations_json: list[dict] | None = None
class RCAResponse(BaseModel):
    """
    Root cause analysis response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    incident_id: str
    root_cause: str
    summary: str | None
    confidence: float | None
    status: str
    recommendations_json: list[dict] | None
    created_at: datetime


class RCARecommendation(BaseModel):
    """
    Recommended action for an incident.
    """

    action: str
    reason: str


class RCAAnalysisResponse(BaseModel):
    """
    Complete RCA analysis response.
    """

    incident_id: str
    root_cause: str
    summary: str
    confidence: float
    recommendations: list[RCARecommendation]