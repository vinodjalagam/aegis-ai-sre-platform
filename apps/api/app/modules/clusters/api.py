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
    current_user_id: str = Depends(
        get_current_user_id
    ),
    service: ClusterService = Depends(
        get_cluster_service
    ),
):
    """
    Create a new Kubernetes cluster.
    """

    try:
        cluster = await service.create_cluster(
            payload,
            current_user_id,
        )

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
    List clusters accessible to the authenticated user.
    """

    clusters = await service.list_user_clusters(
        current_user_id
    )

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
    current_user_id: str = Depends(
        get_current_user_id
    ),
    service: ClusterService = Depends(
        get_cluster_service
    ),
):
    """
    Get a cluster accessible to the authenticated user.
    """

    cluster = await service.get_user_cluster(
        current_user_id,
        cluster_id,
    )

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
    current_user_id: str = Depends(
        get_current_user_id
    ),
    service: ClusterService = Depends(
        get_cluster_service
    ),
):
    """
    Update a cluster.

    Only owners and admins can update a cluster.
    """

    try:
        await service.authorize_cluster_action(
            current_user_id,
            cluster_id,
            ["owner", "admin"],
        )

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

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

@router.delete("/{cluster_id}")
async def delete_cluster(
    cluster_id: str,
    current_user_id: str = Depends(
        get_current_user_id
    ),
    service: ClusterService = Depends(
        get_cluster_service
    ),
):
    """
    Delete a cluster.

    Only cluster owners can delete a cluster.
    """

    try:
        await service.authorize_cluster_action(
            current_user_id,
            cluster_id,
            ["owner"],
        )

        deleted = await service.delete_cluster(
            cluster_id
        )

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

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc