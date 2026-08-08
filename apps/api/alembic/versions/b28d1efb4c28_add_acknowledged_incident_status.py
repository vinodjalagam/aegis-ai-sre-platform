"""add acknowledged incident status

Revision ID: b28d1efb4c28
Revises: 131f11dd780d
Create Date: 2026-08-08 23:50:12.086458

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b28d1efb4c28"
down_revision: Union[str, Sequence[str], None] = "131f11dd780d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ACKNOWLEDGED to incidentstatus enum."""

    op.execute(
        "ALTER TYPE incidentstatus "
        "ADD VALUE IF NOT EXISTS 'ACKNOWLEDGED'"
    )


def downgrade() -> None:
    """PostgreSQL enum values are not safely removed here."""

    pass