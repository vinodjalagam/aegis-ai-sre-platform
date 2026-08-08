from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentTimelineEventCreate(BaseModel):
    event_type: str
    title: str
    description: str | None = None
    metadata_json: str | None = None


class IncidentTimelineEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    event_type: str
    title: str
    description: str | None
    metadata_json: str | None
    created_at: datetime
