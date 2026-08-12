"""
Repository for cluster access.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clusters.access_models import ClusterAccess
from app.modules.clusters.models import Cluster


class ClusterAccessRepository:
    """
    Database operations for user-to-cluster access.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def grant_access(
        self,
        user_id: str,
        cluster_id: str,
        role: str = "viewer",
    ) -> ClusterAccess:

        result = await self.session.execute(
            select(ClusterAccess).where(
                ClusterAccess.user_id == user_id,
                ClusterAccess.cluster_id == cluster_id,
            )
        )

        access = result.scalar_one_or_none()

        if access:
            access.role = role
        else:
            access = ClusterAccess(
                user_id=user_id,
                cluster_id=cluster_id,
                role=role,
            )

            self.session.add(access)

        await self.session.commit()
        await self.session.refresh(access)

        return access

    async def revoke_access(
        self,
        user_id: str,
        cluster_id: str,
    ) -> bool:

        result = await self.session.execute(
            select(ClusterAccess).where(
                ClusterAccess.user_id == user_id,
                ClusterAccess.cluster_id == cluster_id,
            )
        )

        access = result.scalar_one_or_none()

        if not access:
            return False

        await self.session.delete(access)
        await self.session.commit()

        return True

    async def get_access(
        self,
        user_id: str,
        cluster_id: str,
    ) -> ClusterAccess | None:

        result = await self.session.execute(
            select(ClusterAccess).where(
                ClusterAccess.user_id == user_id,
                ClusterAccess.cluster_id == cluster_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_user_clusters(
        self,
        user_id: str,
    ) -> list[Cluster]:

        result = await self.session.execute(
            select(Cluster)
            .join(
                ClusterAccess,
                ClusterAccess.cluster_id == Cluster.id,
            )
            .where(
                ClusterAccess.user_id == user_id,
                Cluster.is_active.is_(True),
            )
            .order_by(
                Cluster.created_at.desc()
            )
        )

        return list(result.scalars().all())
