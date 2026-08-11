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
        keywords: list[str],
        preferred_ports: list[int] | None = None,
    ) -> ServiceDiscovery | None:
        """
        Find the best matching Kubernetes service across all namespaces.
        """

        services = self.core_v1.list_service_for_all_namespaces()

        candidates = []

        for svc in services.items:
            name = (svc.metadata.name or "").lower()

            if not any(keyword in name for keyword in keywords):
                continue

            ports = [
                port.port
                for port in (svc.spec.ports or [])
                if port.port is not None
            ]

            if not ports:
                continue

            score = 0

            # Prefer the expected service port.
            if preferred_ports:
                if any(port in preferred_ports for port in ports):
                    score += 100

            # Prefer exact/common service names.
            if name in keywords:
                score += 50

            # Prefer names ending in the service keyword.
            for keyword in keywords:
                if name.endswith(keyword):
                    score += 20

            candidates.append(
                (
                    score,
                    svc,
                    ports,
                )
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        _, svc, ports = candidates[0]

        selected_port = ports[0]

        if preferred_ports:
            for port in ports:
                if port in preferred_ports:
                    selected_port = port
                    break

        return ServiceDiscovery(
            namespace=svc.metadata.namespace,
            service=svc.metadata.name,
            port=selected_port,
        )

    def discover(self) -> DiscoveryResponse:
        """
        Discover supported platform services.
        """

        return DiscoveryResponse(
            prometheus=self._find_service(
                ["prometheus"],
                preferred_ports=[9090],
            ),
            grafana=self._find_service(
                ["grafana"],
                preferred_ports=[3000, 80],
            ),
            metrics_server=self._find_service(
                ["metrics-server"],
                preferred_ports=[443, 4443],
            ),
            ingress_controller=self._find_service(
                ["ingress-nginx", "nginx"],
                preferred_ports=[80, 443],
            ),
        )