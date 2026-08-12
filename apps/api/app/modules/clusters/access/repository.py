from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clusters.access.models import ClusterAccess


class ClusterAccessRepository:
    """
    Database operations for cluster access.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        access: ClusterAccess,
    ) -> ClusterAccess:
        self.db.add(access)

        await self.db.commit()
        await self.db.refresh(access)

        return access

    async def get(
        self,
        user_id: str,
        cluster_id: str,
    ) -> ClusterAccess | None:

        result = await self.db.execute(
            select(ClusterAccess).where(
                ClusterAccess.user_id == user_id,
                ClusterAccess.cluster_id == cluster_id,
            )
        )

        return result.scalar_one_or_none()
    async def get_user_cluster(
        self,
        user_id: str,
        cluster_id: str,
    ) -> ClusterAccess | None:
        """
        Return the user's access record for a cluster.
        """

        result = await self.db.execute(
            select(ClusterAccess).where(
                ClusterAccess.user_id == user_id,
                ClusterAccess.cluster_id == cluster_id,
            )
        )

        return result.scalar_one_or_none()
    async def list_user_clusters(
        self,
        user_id: str,
    ) -> list[ClusterAccess]:

        result = await self.db.execute(
            select(ClusterAccess).where(
                ClusterAccess.user_id == user_id
            )
        )

        return list(result.scalars().all())

    async def delete(
        self,
        access: ClusterAccess,
    ) -> None:

        await self.db.delete(access)
        await self.db.commit()
