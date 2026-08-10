"""add RCA recommendations

Revision ID: 848f2941c44b
Revises: c1bfbfd9e6ec
Create Date: 2026-08-10 21:58:12.510579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '848f2941c44b'
down_revision: Union[str, Sequence[str], None] = 'c1bfbfd9e6ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'incident_rca',
        sa.Column(
            'recommendations_json',
            sa.JSON(),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        'incident_rca',
        'recommendations_json',
    )
