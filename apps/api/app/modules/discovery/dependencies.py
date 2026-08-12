from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.core.security.dependencies import get_current_user_id
from app.modules.clusters.dependencies import get_cluster_service
from app.modules.clusters.service import ClusterService
from app.modules.discovery.service import DiscoveryService


async def get_discovery_service(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    cluster_service: ClusterService = Depends(
        get_cluster_service
    ),
) -> DiscoveryService:
    """
    Return a DiscoveryService for the selected cluster.

    The authenticated user must have access to the cluster.
    """

    cluster = await cluster_service.get_user_cluster(
        user_id=current_user_id,
        cluster_id=cluster_id,
    )

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    return DiscoveryService(
        cluster.kubeconfig
    )