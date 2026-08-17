from __future__ import annotations

from pydantic import BaseModel


class ClusterSummaryResponse(BaseModel):
    """
    Cluster summary response.
    """

    cluster_version: str
    nodes: int
    namespaces: int
    pods: int
    services: int
    deployments: int


class NodeResponse(BaseModel):
    """
    Kubernetes node response.
    """

    name: str
    status: str
    roles: str
    kubelet_version: str
    os: str
    architecture: str


class NamespaceResponse(BaseModel):
    """
    Kubernetes namespace response.
    """

    name: str


class PodResponse(BaseModel):
    """
    Kubernetes pod response.
    """

    name: str
    namespace: str
    status: str
    node: str | None = None


class ServiceResponse(BaseModel):
    """
    Kubernetes service response.
    """

    name: str
    namespace: str
    type: str
    cluster_ip: str


class DeploymentResponse(BaseModel):
    """
    Kubernetes deployment response.
    """

    name: str
    namespace: str
    replicas: int | None = None
    available: int
    
class ReplicaSetResponse(BaseModel):
    """
    Kubernetes ReplicaSet response.
    """

    name: str
    namespace: str
    replicas: int | None = None
    ready: int | None = None
    
class StatefulSetResponse(BaseModel):
    """
    Kubernetes StatefulSet response.
    """

    name: str
    namespace: str
    replicas: int | None = None
    ready: int | None = None
    
class DaemonSetResponse(BaseModel):
    """
    Kubernetes DaemonSet response.
    """

    name: str
    namespace: str
    desired: int | None = None
    ready: int | None = None
    
class ResourceManifestResponse(BaseModel):
    """
    Kubernetes resource manifest response.
    """

    resource_type: str
    name: str
    namespace: str
    manifest: dict

class ResourceYamlResponse(BaseModel):
    """
    Kubernetes resource YAML response.
    """

    resource_type: str
    name: str
    namespace: str
    yaml: str
    
class ResourceApplyRequest(BaseModel):
    yaml: str
    
    
class ResourceValidateRequest(BaseModel):
    yaml: str


class ResourceValidateResponse(BaseModel):
    valid: bool
    resource_type: str | None = None
    name: str | None = None
    namespace: str | None = None
    message: str
    
class ResourceDiffRequest(BaseModel):
    yaml: str


class ResourceDiffResponse(BaseModel):
    changed: bool
    diff: str
    message: str
    
class ResourceApplyRequest(BaseModel):
    yaml: str

class ResourceApplyResponse(BaseModel):
    """
    Kubernetes resource apply response.
    """

    applied: bool
    resource_type: str
    name: str
    namespace: str
    message: str
    rollout: dict | None = None
    verification: dict | None = None