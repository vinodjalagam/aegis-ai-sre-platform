"""align incident evidence timestamps

Revision ID: 78457334c93c
Revises: f596a4227830
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "78457334c93c"
down_revision: Union[str, Sequence[str], None] = "f596a4227830"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the original timestamp column
    op.drop_column(
        "incident_evidence",
        "collected_at",
    )

    # Add BaseModel timestamp columns
    op.add_column(
        "incident_evidence",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.add_column(
        "incident_evidence",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Add BaseModel audit columns
    op.add_column(
        "incident_evidence",
        sa.Column(
            "created_by",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "incident_evidence",
        sa.Column(
            "updated_by",
            sa.String(length=50),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "incident_evidence",
        "updated_by",
    )

    op.drop_column(
        "incident_evidence",
        "created_by",
    )

    op.drop_column(
        "incident_evidence",
        "updated_at",
    )

    op.drop_column(
        "incident_evidence",
        "created_at",
    )

    op.add_column(
        "incident_evidence",
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )