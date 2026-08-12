from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import get_current_user_id
from app.db.session import get_db
from app.modules.clusters.access.repository import (
    ClusterAccessRepository,
)
from app.modules.clusters.repository import ClusterRepository
from app.modules.clusters.service import ClusterService
from app.modules.kubernetes.service import KubernetesService


async def get_kubernetes_service(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> KubernetesService:
    """
    Return a KubernetesService for the selected cluster.

    The authenticated user must have access to the cluster.
    """

    cluster_repository = ClusterRepository(db)
    access_repository = ClusterAccessRepository(db)

    cluster_service = ClusterService(
        repository=cluster_repository,
        access_repository=access_repository,
    )

    cluster = await cluster_service.get_user_cluster(
        user_id=current_user_id,
        cluster_id=cluster_id,
    )

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or you do not have access",
        )

    return KubernetesService(
        cluster.kubeconfig
    )