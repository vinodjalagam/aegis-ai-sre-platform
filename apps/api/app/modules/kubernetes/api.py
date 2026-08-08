from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security.dependencies import get_current_user_id
from app.modules.kubernetes.dependencies import get_kubernetes_service
from app.modules.kubernetes.schemas import (
    ClusterSummaryResponse,
    DeploymentResponse,
    NamespaceResponse,
    NodeResponse,
    PodResponse,
    ServiceResponse,
)
from app.modules.kubernetes.service import KubernetesService
from app.shared.responses.success import success_response

router = APIRouter(
    prefix="/kubernetes",
    tags=["Kubernetes"],
)


@router.get("/summary")
async def get_cluster_summary(
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    Get Kubernetes cluster summary.
    """

    summary = service.get_cluster_summary()

    return success_response(
        ClusterSummaryResponse(**summary)
    )


@router.get("/nodes")
async def get_nodes(
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes nodes.
    """

    nodes = service.get_nodes()

    return success_response(
        [
            NodeResponse(**node)
            for node in nodes
        ]
    )


@router.get("/namespaces")
async def get_namespaces(
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes namespaces.
    """

    namespaces = service.get_namespaces()

    return success_response(
        [
            NamespaceResponse(name=name)
            for name in namespaces
        ]
    )


@router.get("/pods")
async def get_pods(
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes pods.
    """

    pods = service.get_pods()

    return success_response(
        [
            PodResponse(**pod)
            for pod in pods
        ]
    )


@router.get("/services")
async def get_services(
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes services.
    """

    services = service.get_services()

    return success_response(
        [
            ServiceResponse(**service_data)
            for service_data in services
        ]
    )


@router.get("/deployments")
async def get_deployments(
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes deployments.
    """

    deployments = service.get_deployments()

    return success_response(
        [
            DeploymentResponse(**deployment)
            for deployment in deployments
        ]
    )