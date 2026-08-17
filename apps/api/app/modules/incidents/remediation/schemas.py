from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentRemediationCreate(BaseModel):
    resource_type: str
    resource_name: str
    namespace: str
    proposed_yaml: str | None = None
    applied: bool = False
    status: str = "proposed"
    message: str | None = None
    rollout_json: str | None = None
    verification_json: str | None = None


class IncidentRemediationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    resource_type: str
    resource_name: str
    namespace: str
    proposed_yaml: str | None
    applied: bool
    status: str
    message: str | None
    rollout_json: str | None
    verification_json: str | None
    created_at: datetime
    updated_at: datetime
