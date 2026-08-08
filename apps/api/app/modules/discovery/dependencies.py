from __future__ import annotations

from fastapi import Depends

from app.modules.clusters.dependencies import get_cluster_service
from app.modules.clusters.service import ClusterService
from app.modules.discovery.service import DiscoveryService


async def get_discovery_service(
    cluster_id: str,
    cluster_service: ClusterService = Depends(get_cluster_service),
) -> DiscoveryService:
    """
    Return a DiscoveryService for the given cluster.
    """

    cluster = await cluster_service.get_cluster(cluster_id)

    if not cluster:
        raise ValueError("Cluster not found")

    return DiscoveryService(cluster.kubeconfig)