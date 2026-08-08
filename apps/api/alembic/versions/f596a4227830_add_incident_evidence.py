"""add incident evidence

Revision ID: f596a4227830
Revises: d4701efec161
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f596a4227830"
down_revision: Union[str, Sequence[str], None] = "d4701efec161"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incident_evidence",
        sa.Column(
            "id",
            sa.String(length=26),
            nullable=False,
        ),
        sa.Column(
            "incident_id",
            sa.String(length=26),
            nullable=False,
        ),
        sa.Column(
            "evidence_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "query",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "resource_name",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "namespace",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "metric_value",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_incident_evidence_incident_id",
        "incident_evidence",
        ["incident_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_incident_evidence_incident_id",
        table_name="incident_evidence",
    )

    op.drop_table("incident_evidence")