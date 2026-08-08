from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.clusters.repository import ClusterRepository
from app.modules.clusters.service import ClusterService


def get_cluster_repository(
    session: AsyncSession = Depends(get_db),
) -> ClusterRepository:
    """
    Return a ClusterRepository instance.
    """
    return ClusterRepository(session)


def get_cluster_service(
    repository: ClusterRepository = Depends(get_cluster_repository),
) -> ClusterService:
    """
    Return a ClusterService instance.
    """
    return ClusterService(repository)