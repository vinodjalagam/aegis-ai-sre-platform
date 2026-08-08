from pydantic import BaseModel, ConfigDict

from app.modules.incidents.enums import (
    IncidentSeverity,
    IncidentSource,
    IncidentStatus,
)


class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    severity: IncidentSeverity
    source: IncidentSource
    resource_name: str | None = None
    namespace: str | None = None
    cluster_id: str


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    resource_name: str | None = None
    namespace: str | None = None
    is_active: bool | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    severity: IncidentSeverity
    status: IncidentStatus
    source: IncidentSource
    resource_name: str | None
    namespace: str | None
    cluster_id: str
    is_active: bool


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int