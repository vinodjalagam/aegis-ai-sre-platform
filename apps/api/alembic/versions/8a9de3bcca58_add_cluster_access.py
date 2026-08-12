"""add cluster access

Revision ID: 8a9de3bcca58
Revises: 848f2941c44b
Create Date: 2026-08-11 15:54:38.968023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a9de3bcca58'
down_revision: Union[str, Sequence[str], None] = '848f2941c44b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "cluster_access",
        sa.Column(
            "user_id",
            sa.String(length=26),
            nullable=False,
        ),
        sa.Column(
            "cluster_id",
            sa.String(length=26),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
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
            ["cluster_id"],
            ["clusters.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "cluster_id",
            name="uq_cluster_access_user_cluster",
        ),
    )

    op.create_index(
        op.f("ix_cluster_access_cluster_id"),
        "cluster_access",
        ["cluster_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_cluster_access_user_id"),
        "cluster_access",
        ["user_id"],
        unique=False,
    )

def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_cluster_access_user_id"),
        table_name="cluster_access",
    )

    op.drop_index(
        op.f("ix_cluster_access_cluster_id"),
        table_name="cluster_access",
    )

    op.drop_table("cluster_access")