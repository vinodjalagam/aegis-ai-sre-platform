"""add metadata to incident evidence

Revision ID: 0c5389577576
Revises: 86a6f9c108e7
Create Date: 2026-08-09 23:00:08.627839

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0c5389577576"
down_revision: Union[str, Sequence[str], None] = "86a6f9c108e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "incident_evidence",
        sa.Column(
            "metadata_json",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "incident_evidence",
        "metadata_json",
    )