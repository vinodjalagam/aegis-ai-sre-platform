"""add incident timeline events

Revision ID: 131f11dd780d
Revises: 78457334c93c
Create Date: 2026-08-08 22:47:31.706654

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "131f11dd780d"
down_revision: Union[str, Sequence[str], None] = "78457334c93c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incident_timeline_events",

        sa.Column(
            "incident_id",
            sa.String(length=26),
            nullable=False,
        ),

        sa.Column(
            "event_type",
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
            "metadata_json",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "id",
            sa.String(length=26),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "created_by",
            sa.String(length=50),
            nullable=True,
        ),

        sa.Column(
            "updated_by",
            sa.String(length=50),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_incident_timeline_events_incident_id",
        "incident_timeline_events",
        ["incident_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_incident_timeline_events_incident_id",
        table_name="incident_timeline_events",
    )

    op.drop_table("incident_timeline_events")