"""
Incident evidence ORM model.
"""

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base_model import BaseModel


class IncidentEvidence(BaseModel):
    """
    Evidence collected for an incident.
    """

    __tablename__ = "incident_evidence"

    incident_id: Mapped[str] = mapped_column(
        ForeignKey(
            "incidents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    query: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resource_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    namespace: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    metric_value: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    
    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )