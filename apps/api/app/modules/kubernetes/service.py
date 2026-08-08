from __future__ import annotations

from kubernetes.client import ApiException

from app.modules.kubernetes.client import KubernetesClient


class KubernetesService:
    """
    Service for interacting with Kubernetes clusters.
    """

    def __init__(self):
        self.client = KubernetesClient()
        self.client.connect()

    def connect(self) -> bool:
        """
        Verify cluster connectivity.
        """
        return self.client.is_connected()

    def get_cluster_summary(self) -> dict:
        """
        Return a summary of the cluster.
        """

        core = self.client.core_v1
        apps = self.client.apps_v1
        version = self.client.version_api

        nodes = core.list_node().items
        namespaces = core.list_namespace().items
        pods = core.list_pod_for_all_namespaces().items
        services = core.list_service_for_all_namespaces().items
        deployments = apps.list_deployment_for_all_namespaces().items
        version_info = version.get_code()

        return {
            "cluster_version": version_info.git_version,
            "nodes": len(nodes),
            "namespaces": len(namespaces),
            "pods": len(pods),
            "services": len(services),
            "deployments": len(deployments),
        }

    def get_nodes(self) -> list[dict]:
        """
        Return all cluster nodes.
        """

        nodes = self.client.core_v1.list_node().items

        result = []

        for node in nodes:

            roles = []

            labels = node.metadata.labels

            if "node-role.kubernetes.io/control-plane" in labels:
                roles.append("control-plane")

            if "node-role.kubernetes.io/master" in labels:
                roles.append("master")

            if not roles:
                roles.append("worker")

            status = "Unknown"

            for condition in node.status.conditions:
                if (
                    condition.type == "Ready"
                    and condition.status == "True"
                ):
                    status = "Ready"

            result.append(
                {
                    "name": node.metadata.name,
                    "status": status,
                    "roles": ", ".join(roles),
                    "kubelet_version": node.status.node_info.kubelet_version,
                    "os": node.status.node_info.operating_system,
                    "architecture": node.status.node_info.architecture,
                }
            )

        return result

    def get_namespaces(self) -> list[str]:
        """
        Return all namespaces.
        """

        namespaces = self.client.core_v1.list_namespace().items

        return [
            namespace.metadata.name
            for namespace in namespaces
        ]

    def get_pods(self) -> list[dict]:
        """
        Return all pods.
        """

        pods = self.client.core_v1.list_pod_for_all_namespaces().items

        result = []

        for pod in pods:

            result.append(
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                }
            )

        return result

    def get_services(self) -> list[dict]:
        """
        Return all services.
        """

        services = (
            self.client.core_v1
            .list_service_for_all_namespaces()
            .items
        )

        result = []

        for service in services:

            result.append(
                {
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "type": service.spec.type,
                    "cluster_ip": service.spec.cluster_ip,
                }
            )

        return result

    def get_deployments(self) -> list[dict]:
        """
        Return all deployments.
        """

        deployments = (
            self.client.apps_v1
            .list_deployment_for_all_namespaces()
            .items
        )

        result = []

        for deployment in deployments:

            result.append(
                {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "replicas": deployment.spec.replicas,
                    "available": deployment.status.available_replicas or 0,
                }
            )

        return result