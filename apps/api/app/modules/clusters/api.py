from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security.dependencies import get_current_user_id
from app.modules.clusters.dependencies import get_cluster_service
from app.modules.clusters.schemas import (
    ClusterCreate,
    ClusterListResponse,
    ClusterResponse,
    ClusterUpdate,
)
from app.modules.clusters.service import ClusterService
from app.shared.responses.success import success_response

router = APIRouter(
    prefix="/clusters",
    tags=["Clusters"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_cluster(
    payload: ClusterCreate,
    service: ClusterService = Depends(get_cluster_service),
):
    """
    Create a new Kubernetes cluster.
    """
    try:
        cluster = await service.create_cluster(payload)

        return success_response(
            ClusterResponse.model_validate(cluster)
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("")
async def list_clusters(
    current_user_id: str = Depends(get_current_user_id),
    service: ClusterService = Depends(get_cluster_service),
):
    """
    List all clusters.
    """

    clusters = await service.list_clusters()

    response = ClusterListResponse(
        items=[
            ClusterResponse.model_validate(cluster)
            for cluster in clusters
        ],
        total=len(clusters),
    )

    return success_response(response)


@router.get("/{cluster_id}")
async def get_cluster(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: ClusterService = Depends(get_cluster_service),
):
    """
    Get cluster by ID.
    """

    cluster = await service.get_cluster(cluster_id)

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    return success_response(
        ClusterResponse.model_validate(cluster)
    )


@router.put("/{cluster_id}")
async def update_cluster(
    cluster_id: str,
    payload: ClusterUpdate,
    current_user_id: str = Depends(get_current_user_id),
    service: ClusterService = Depends(get_cluster_service),
):
    """
    Update a cluster.
    """

    cluster = await service.update_cluster(
        cluster_id,
        payload,
    )

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    return success_response(
        ClusterResponse.model_validate(cluster)
    )


@router.delete("/{cluster_id}")
async def delete_cluster(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: ClusterService = Depends(get_cluster_service),
):
    """
    Delete a cluster.
    """

    deleted = await service.delete_cluster(cluster_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    return success_response(
        {
            "message": "Cluster deleted successfully",
        }
    )