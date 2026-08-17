from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base_model import BaseModel


class IncidentRemediation(BaseModel):
    """
    Records an automated or approved remediation performed for an incident.
    """

    __tablename__ = "incident_remediations"

    incident_id: Mapped[str] = mapped_column(
        ForeignKey(
            "incidents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    resource_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    namespace: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    proposed_yaml: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    applied: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="proposed",
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rollout_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
