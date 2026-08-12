from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clusters.models import Cluster
from app.modules.clusters.access.models import ClusterAccess


class ClusterRepository:
    """
    Repository for Cluster database operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, cluster: Cluster) -> Cluster:
        self.session.add(cluster)
        await self.session.commit()
        await self.session.refresh(cluster)
        return cluster

    async def get_by_id(
        self,
        cluster_id: str,
    ) -> Cluster | None:
        result = await self.session.execute(
            select(Cluster).where(
                Cluster.id == cluster_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Cluster | None:
        result = await self.session.execute(
            select(Cluster).where(
                Cluster.name == name
            )
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[Cluster]:
        """
        Return all clusters.
        """

        result = await self.session.execute(
            select(Cluster).order_by(
                Cluster.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def list_for_user(
        self,
        user_id: str,
    ) -> list[Cluster]:
        """
        Return active clusters accessible to the user.
        """

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
            .order_by(Cluster.created_at.desc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        cluster: Cluster,
    ) -> Cluster:
        self.session.add(cluster)
        await self.session.commit()
        await self.session.refresh(cluster)
        return cluster

    async def delete(
        self,
        cluster: Cluster,
    ) -> None:
        await self.session.delete(cluster)
        await self.session.commit()