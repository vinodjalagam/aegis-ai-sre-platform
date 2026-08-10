"""add incident assignment

Revision ID: 2962a1467374
Revises: 0c5389577576
Create Date: 2026-08-10 14:39:08.394411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2962a1467374'
down_revision: Union[str, Sequence[str], None] = '0c5389577576'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "incidents",
        sa.Column(
            "assigned_to",
            sa.String(length=26),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_incidents_assigned_to"),
        "incidents",
        ["assigned_to"],
        unique=False,
    )

    op.create_foreign_key(
        None,
        "incidents",
        "users",
        ["assigned_to"],
        ["id"],
        ondelete="SET NULL",
    )

def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        None,
        "incidents",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_incidents_assigned_to"),
        table_name="incidents",
    )

    op.drop_column(
        "incidents",
        "assigned_to",
    )
