"""
Audit mixin.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class AuditMixin:
    """
    Adds audit fields.
    """

    created_by: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    updated_by: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )