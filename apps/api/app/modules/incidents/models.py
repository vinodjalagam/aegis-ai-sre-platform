from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base_model import BaseModel
from app.modules.incidents.enums import (
    IncidentSeverity,
    IncidentSource,
    IncidentStatus,
)


class Incident(BaseModel):
    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity),
        nullable=False,
    )

    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus),
        nullable=False,
        default=IncidentStatus.OPEN,
    )

    source: Mapped[IncidentSource] = mapped_column(
        Enum(IncidentSource),
        nullable=False,
    )

    resource_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    namespace: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    cluster_id: Mapped[str] = mapped_column(
        ForeignKey("clusters.id"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )