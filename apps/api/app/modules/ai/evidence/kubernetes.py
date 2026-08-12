from __future__ import annotations

from app.modules.ai.evidence.provider import EvidenceProvider
from app.modules.ai.tools.kubernetes import KubernetesInvestigationTool


class KubernetesEvidenceProvider(EvidenceProvider):
    """
    Kubernetes evidence provider for the AI agent.

    This provider is read-only.
    """

    def __init__(self, kubeconfig: str) -> None:
        self.tool = KubernetesInvestigationTool(
            kubeconfig
        )
    @property
    def core_v1(self):
        """
        Kubernetes CoreV1 API client used by this provider.
        """

        return self.tool.service.client.core_v1

    async def collect(
        self,
        context: dict,
    ) -> dict:
        """
        Collect Kubernetes evidence.

        Returns an empty result when Kubernetes context
        is unavailable instead of failing the AI analysis.
        """

        namespace = context.get("namespace")
        resource_name = context.get("resource_name")

        if not namespace or not resource_name:
            return {}

        try:
            return self.tool.investigate_resource(
                namespace=namespace,
                resource_name=resource_name,
            )
        except Exception:
            return {}
