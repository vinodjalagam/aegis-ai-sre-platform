from __future__ import annotations

from app.modules.clusters.models import Cluster
from app.modules.clusters.repository import ClusterRepository
from app.modules.clusters.schemas import (
    ClusterCreate,
    ClusterUpdate,
)


class ClusterService:
    """
    Business logic for clusters.
    """

    def __init__(self, repository: ClusterRepository):
        self.repository = repository

    async def create_cluster(
        self,
        data: ClusterCreate,
    ) -> Cluster:
        """
        Create a new cluster.
        """

        existing = await self.repository.get_by_name(data.name)

        if existing:
            raise ValueError("Cluster name already exists")

        cluster = Cluster(
            name=data.name,
            description=data.description,
            provider=data.provider,
            kubeconfig=data.kubeconfig,
            status="offline",
            is_active=True,
        )

        return await self.repository.create(cluster)

    async def get_cluster(
        self,
        cluster_id: str,
    ) -> Cluster | None:
        """
        Get cluster by ID.
        """

        return await self.repository.get_by_id(cluster_id)

    async def list_clusters(self) -> list[Cluster]:
        """
        List all clusters.
        """

        return await self.repository.list()

    async def update_cluster(
        self,
        cluster_id: str,
        data: ClusterUpdate,
    ) -> Cluster | None:
        """
        Update a cluster.
        """

        cluster = await self.repository.get_by_id(cluster_id)

        if not cluster:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(cluster, key, value)

        return await self.repository.update(cluster)

    async def delete_cluster(
        self,
        cluster_id: str,
    ) -> bool:
        """
        Delete a cluster.
        """

        cluster = await self.repository.get_by_id(cluster_id)

        if not cluster:
            return False

        await self.repository.delete(cluster)

        return True