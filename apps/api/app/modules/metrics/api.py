from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import get_current_user_id
from app.db.session import get_db

from app.modules.clusters.repository import ClusterRepository
from app.modules.discovery.service import DiscoveryService
from app.modules.metrics.client import PrometheusClient

from app.shared.responses.success import success_response


router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)


@router.get("/query")
async def query_metrics(
    query: str = Query(...),
    cluster_id: str = Query(...),
    current_user_id: str = Depends(
        get_current_user_id
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a PromQL query against the selected
    Kubernetes cluster.
    """

    # ---------------------------------------------
    # 1. Get cluster
    # ---------------------------------------------

    cluster_repository = ClusterRepository(db)

    cluster = await cluster_repository.get_by_id(
        cluster_id
    )

    if not cluster:
        raise HTTPException(
            status_code=404,
            detail="Cluster not found",
        )

    # ---------------------------------------------
    # 2. Check user's cluster access
    # ---------------------------------------------

    accessible_clusters = (
        await cluster_repository.list_for_user(
            current_user_id
        )
    )

    has_access = any(
        accessible.id == cluster.id
        for accessible in accessible_clusters
    )

    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this cluster",
        )

    # ---------------------------------------------
    # 3. Discover Prometheus
    # ---------------------------------------------

    discovery = DiscoveryService(
        cluster.kubeconfig
    )

    platform = discovery.discover()

    if not platform.prometheus:
        raise HTTPException(
            status_code=503,
            detail=(
                "Prometheus was not discovered "
                "in the selected cluster"
            ),
        )

    # ---------------------------------------------
    # 4. Create Prometheus client
    # ---------------------------------------------

    prometheus = PrometheusClient(
        core_v1=discovery.core_v1,
        namespace=platform.prometheus.namespace,
        service=platform.prometheus.service,
        port=platform.prometheus.port,
    )

    # ---------------------------------------------
    # 5. Execute PromQL
    # ---------------------------------------------

    result = await prometheus.query(query)

    # ---------------------------------------------
    # 6. Return dashboard response
    # ---------------------------------------------

    return success_response(
        {
            "cluster_id": cluster.id,
            "cluster_name": cluster.name,
            "query": query,
            "result": result,
        }
    )