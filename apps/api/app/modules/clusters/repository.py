from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clusters.models import Cluster


class ClusterRepository:
    """
    Repository for Cluster database operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, cluster: Cluster) -> Cluster:
        """
        Create a new cluster.
        """
        self.session.add(cluster)
        await self.session.commit()
        await self.session.refresh(cluster)
        return cluster

    async def get_by_id(self, cluster_id: str) -> Cluster | None:
        """
        Get a cluster by ID.
        """
        result = await self.session.execute(
            select(Cluster).where(Cluster.id == cluster_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Cluster | None:
        """
        Get a cluster by name.
        """
        result = await self.session.execute(
            select(Cluster).where(Cluster.name == name)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[Cluster]:
        """
        Return all clusters.
        """
        result = await self.session.execute(
            select(Cluster).order_by(Cluster.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, cluster: Cluster) -> Cluster:
        """
        Persist updates.
        """
        await self.session.commit()
        await self.session.refresh(cluster)
        return cluster

    async def delete(self, cluster: Cluster) -> None:
        """
        Delete a cluster.
        """
        await self.session.delete(cluster)
        await self.session.commit()