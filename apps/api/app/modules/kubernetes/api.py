from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.incidents.remediation.schemas import (
    IncidentRemediationCreate,
)
from app.modules.incidents.remediation.service import (
    IncidentRemediationService,
)
from app.modules.incidents.timeline.service import (
    IncidentTimelineService,
)
from app.modules.incidents.timeline.schemas import (
    IncidentTimelineEventCreate,
)
from app.core.security.dependencies import get_current_user_id
from app.modules.kubernetes.dependencies import get_kubernetes_service
from app.modules.kubernetes.schemas import (
    ClusterSummaryResponse,
    DeploymentResponse,
    ReplicaSetResponse,
    StatefulSetResponse,
    DaemonSetResponse,
    NamespaceResponse,
    NodeResponse,
    PodResponse,
    ServiceResponse,
    ResourceManifestResponse,
    ResourceYamlResponse,
    ResourceValidateRequest,
    ResourceValidateResponse,
    ResourceDiffRequest,
    ResourceDiffResponse,
    ResourceApplyRequest,
    ResourceApplyResponse,
)
from app.modules.incidents.service import IncidentService
from app.modules.kubernetes.service import KubernetesService
from app.shared.responses.success import success_response

router = APIRouter(
    prefix="/kubernetes",
    tags=["Kubernetes"],
)


@router.get("/summary")
async def get_cluster_summary(
    cluster_id: str,
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
    cluster_id: str,
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
    cluster_id: str,
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
    cluster_id: str,
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
    cluster_id: str,
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
    cluster_id: str,
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
    
@router.get("/replicasets")
async def get_replicasets(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes ReplicaSets.
    """

    replicasets = service.get_replicasets()

    return success_response(
        [
            ReplicaSetResponse(**replicaset)
            for replicaset in replicasets
        ]
    )
    
@router.get("/statefulsets")
async def get_statefulsets(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes StatefulSets.
    """

    statefulsets = service.get_statefulsets()

    return success_response(
        [
            StatefulSetResponse(**statefulset)
            for statefulset in statefulsets
        ]
    )
    
@router.get("/daemonsets")
async def get_daemonsets(
    cluster_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    List Kubernetes DaemonSets.
    """

    daemonsets = service.get_daemonsets()

    return success_response(
        [
            DaemonSetResponse(**daemonset)
            for daemonset in daemonsets
        ]
    )

@router.get("/resource")
async def get_resource_manifest(
    cluster_id: str,
    namespace: str,
    resource_type: str,
    resource_name: str,
    current_user_id: str = Depends(get_current_user_id),
    service: KubernetesService = Depends(get_kubernetes_service),
):
    """
    Get the manifest of a Kubernetes resource.
    Read-only operation.
    """

    manifest = service.get_resource_manifest(
        namespace=namespace,
        resource_type=resource_type,
        resource_name=resource_name,
    )

    if manifest is None:
        raise HTTPException(
            status_code=404,
            detail="Kubernetes resource not found",
        )

    return success_response(
        ResourceManifestResponse(
            resource_type=resource_type,
            name=resource_name,
            namespace=namespace,
            manifest=manifest,
        )
    )

@router.get("/resource/yaml")
async def get_resource_yaml(
    cluster_id: str,
    namespace: str,
    resource_type: str,
    resource_name: str,
    service: KubernetesService = Depends(
        get_kubernetes_service
    ),
):
    """
    Return a clean YAML representation of a Kubernetes resource.
    """

    yaml_content = service.get_resource_yaml(
        namespace=namespace,
        resource_type=resource_type,
        resource_name=resource_name,
    )

    if yaml_content is None:
        raise HTTPException(
            status_code=404,
            detail="Kubernetes resource not found",
        )

    return success_response(
        ResourceYamlResponse(
            resource_type=resource_type,
            name=resource_name,
            namespace=namespace,
            yaml=yaml_content,
        )
    )
    
@router.post("/resource/yaml/validate")
async def validate_resource_yaml(
    cluster_id: str,
    namespace: str,
    resource_type: str,
    resource_name: str,
    request: ResourceValidateRequest,
    service: KubernetesService = Depends(
        get_kubernetes_service
    ),
):
    """
    Validate Kubernetes YAML without modifying the cluster.
    """

    result = service.validate_resource_yaml(
        namespace=namespace,
        resource_type=resource_type,
        resource_name=resource_name,
        yaml_content=request.yaml,
    )

    return success_response(
        ResourceValidateResponse(**result)
    )

@router.post("/resource/yaml/diff")
async def diff_resource_yaml(
    cluster_id: str,
    namespace: str,
    resource_type: str,
    resource_name: str,
    request: ResourceDiffRequest,
    service: KubernetesService = Depends(
        get_kubernetes_service
    ),
):
    """
    Show changes without modifying Kubernetes.
    """

    result = service.diff_resource_yaml(
        namespace=namespace,
        resource_type=resource_type,
        resource_name=resource_name,
        yaml_content=request.yaml,
    )

    return success_response(
        ResourceDiffResponse(**result)
    )
    
@router.post("/resource/yaml/apply")
async def apply_resource_yaml(
    cluster_id: str,
    incident_id: str,
    namespace: str,
    resource_type: str,
    resource_name: str,
    request: ResourceApplyRequest,
    service: KubernetesService = Depends(
        get_kubernetes_service
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Explicitly apply a validated Kubernetes resource update
    and persist the remediation result against the incident.
    """

    remediation_service = IncidentRemediationService(db)

    remediation = await remediation_service.create(
        incident_id=incident_id,
        data=IncidentRemediationCreate(
            resource_type=resource_type,
            resource_name=resource_name,
            namespace=namespace,
            proposed_yaml=request.yaml,
        ),
    )

    result = service.apply_resource_yaml(
        namespace=namespace,
        resource_type=resource_type,
        resource_name=resource_name,
        yaml_content=request.yaml,
    )

    if not result.get("applied"):
        status = "failed"

    elif (
        result.get("verification")
        and result["verification"].get("status") == "resolved"
        and result["verification"].get("healthy") is True
    ):
        status = "resolved"

    elif (
        result.get("rollout")
        and not result["rollout"].get("healthy", False)
    ):
        status = "rollout_failed"

    else:
        status = "not_resolved"

    await remediation_service.record_result(
        remediation.id,
        applied=result.get("applied", False),
        status=status,
        message=result.get("message"),
        rollout=result.get("rollout"),
        verification=result.get("verification"),
    )

    if status == "resolved":
        incident_service = IncidentService(db)

        incident = await incident_service.get_incident(
            incident_id
        )

        if incident is not None and incident.is_active:

            timeline_service = IncidentTimelineService(db)

            await timeline_service.create(
                incident_id=incident_id,
                data=IncidentTimelineEventCreate(
                    event_type="remediation_applied",
                    title="Remediation applied",
                    description=(
                        f"Remediation applied successfully to "
                        f"{resource_type}/{resource_name} "
                        f"in namespace {namespace}"
                    ),
                ),
            )

            await incident_service.auto_resolve_incident(
                incident
            )
        return success_response(
            ResourceApplyResponse(**result)
        )