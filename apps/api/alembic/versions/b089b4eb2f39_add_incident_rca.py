"""add incident rca

Revision ID: b089b4eb2f39
Revises: b28d1efb4c28
Create Date: 2026-08-09 00:43:36.094249

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b089b4eb2f39"
down_revision: Union[str, Sequence[str], None] = "b28d1efb4c28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incident_rca",
        sa.Column(
            "incident_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "root_cause",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "confidence",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="completed",
        ),
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.String(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("incident_id"),
    )

    op.create_index(
        "ix_incident_rca_incident_id",
        "incident_rca",
        ["incident_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_incident_rca_incident_id",
        table_name="incident_rca",
    )

    op.drop_table("incident_rca")