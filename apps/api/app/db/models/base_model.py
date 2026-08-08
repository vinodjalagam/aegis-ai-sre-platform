"""
Base ORM model.
"""

from ulid import ULID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.audit import AuditMixin
from app.db.mixins.timestamp import TimestampMixin


class BaseModel(Base, TimestampMixin, AuditMixin):
    """
    Base model inherited by all ORM models.
    """

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )