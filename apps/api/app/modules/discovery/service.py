from __future__ import annotations

from kubernetes import client
from kubernetes.config import load_kube_config

from app.modules.discovery.schemas import (
    DiscoveryResponse,
    ServiceDiscovery,
)


class DiscoveryService:
    """
    Automatically discovers Kubernetes platform services.
    """

    def __init__(self, kubeconfig: str):
        load_kube_config(config_file=kubeconfig)
        self.core_v1 = client.CoreV1Api()

    def _find_service(
        self,
        namespace: str,
        keywords: list[str],
    ) -> ServiceDiscovery | None:
        """
        Find a service in a namespace using keywords.
        """

        services = self.core_v1.list_namespaced_service(namespace)

        for svc in services.items:
            name = svc.metadata.name.lower()

            if any(keyword in name for keyword in keywords):
                port = svc.spec.ports[0].port

                return ServiceDiscovery(
                    namespace=namespace,
                    service=svc.metadata.name,
                    port=port,
                )

        return None

    def discover(self) -> DiscoveryResponse:
        """
        Discover supported platform services.
        """

        return DiscoveryResponse(
            prometheus=self._find_service(
                "monitoring",
                ["prometheus"],
            ),
            grafana=self._find_service(
                "monitoring",
                ["grafana"],
            ),
            metrics_server=self._find_service(
                "kube-system",
                ["metrics-server"],
            ),
            ingress_controller=self._find_service(
                "kube-system",
                ["ingress-nginx", "nginx"],
            ),
        )