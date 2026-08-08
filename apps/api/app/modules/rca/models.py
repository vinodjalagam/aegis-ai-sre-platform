"""
Root cause analysis ORM model.
"""

from sqlalchemy import ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base_model import BaseModel


class IncidentRCA(BaseModel):
    """
    Root cause analysis result for an incident.
    """

    __tablename__ = "incident_rca"

    incident_id: Mapped[str] = mapped_column(
        ForeignKey(
            "incidents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    root_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",
    )