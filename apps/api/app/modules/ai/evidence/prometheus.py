from __future__ import annotations

from app.modules.ai.evidence.provider import EvidenceProvider
from app.modules.metrics.service import MetricsService


class PrometheusEvidenceProvider(EvidenceProvider):
    """
    Optional Prometheus evidence provider.

    Prometheus being unavailable must never stop RCA.
    """

    def __init__(self, kubeconfig: str) -> None:
        self.metrics_service = MetricsService(
            kubeconfig
    )

    async def collect(
        self,
        context: dict,
    ) -> dict:
        """
        Collect Prometheus evidence for the affected resource.
        """

        namespace = context.get("namespace")
        resource_name = context.get("resource_name")
        kubernetes_evidence = context.get(
            "kubernetes_evidence",
            {},
        )

        if not namespace:
            return {}

        pod = kubernetes_evidence.get("pod") or {}
        pod_name = pod.get("name")

        target_name = pod_name or resource_name

        if not target_name:
            return {}

        queries = self._build_queries(
            namespace,
            target_name,
        )

        collected: dict[str, list[dict]] = {}

        for name, promql in queries.items():
            result = await self.metrics_service.query(
                promql
            )

            if result:
                collected[name] = result

        if not collected:
            return {}

        return {
            
           "prometheus": collected,
        }
    
    def _build_queries(
        self,
        namespace: str | None,
        resource_name: str,
    ) -> dict[str, str]:
        """
        Build conservative PromQL queries.

        These are read-only queries.
        """

        queries = {}

        if namespace:
            queries["pod_memory_usage"] = (
                f'container_memory_working_set_bytes'
                f'{{namespace="{namespace}",'
                f'pod="{resource_name}"}}'
            )

            queries["pod_cpu_usage"] = (
                f'rate(container_cpu_usage_seconds_total'
                f'{{namespace="{namespace}",'
                f'pod="{resource_name}"}}[5m])'
            )

        return queries
