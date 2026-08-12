from __future__ import annotations

from app.modules.discovery.service import DiscoveryService
from app.modules.metrics.client import PrometheusClient


class MetricsService:
    """
    Service for optional Prometheus metrics access.
    """

    def __init__(
        self,
        kubeconfig: str,
    ) -> None:
        self.discovery = DiscoveryService(
            kubeconfig
        )

    async def query(
        self,
        promql: str,
    ) -> list[dict]:
        """
        Execute PromQL when Prometheus is available.

        Prometheus is optional. If it is unavailable,
        return an empty result instead of failing RCA.
        """

        try:
            platform = self.discovery.discover()

            if not platform.prometheus:
                return []

            prometheus = PrometheusClient(
                core_v1=self.discovery.core_v1,
                namespace=platform.prometheus.namespace,
                service=platform.prometheus.service,
                port=platform.prometheus.port,
            )

            return await prometheus.query(
                promql
            )

        except Exception:
            return []