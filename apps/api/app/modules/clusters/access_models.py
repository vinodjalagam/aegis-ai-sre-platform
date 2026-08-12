"""
Cluster access ORM model.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base_model import BaseModel


class ClusterAccess(BaseModel):
    """
    Defines which users can access which Kubernetes clusters.
    """

    __tablename__ = "cluster_access"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cluster_id: Mapped[str] = mapped_column(
        ForeignKey("clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="viewer",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "cluster_id",
            name="uq_cluster_access_user_cluster",
        ),
    )
