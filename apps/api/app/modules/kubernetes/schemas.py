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