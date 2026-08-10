from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentEvidenceCreate(BaseModel):
    evidence_type: str
    title: str
    description: str | None = None
    query: str | None = None
    resource_name: str | None = None
    namespace: str | None = None
    metric_value: str | None = None
    metadata_json: dict | None = None


class IncidentEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    evidence_type: str
    title: str
    description: str | None
    query: str | None
    resource_name: str | None
    namespace: str | None
    metric_value: str | None
    metadata_json: dict | None
    created_at: datetime