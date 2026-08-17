from __future__ import annotations

from app.modules.ai.agent import AIAgent
from app.modules.ai.gemini import GeminiProvider
from app.modules.ai.schemas import AIAnalysisResult
from app.modules.ai.evidence.provider import EvidenceProvider
from app.modules.ai.evidence.kubernetes import KubernetesEvidenceProvider
from app.modules.ai.evidence.prometheus import (
    PrometheusEvidenceProvider,
)

class AegisAgent(AIAgent):
    """
    Initial Aegis AI agent.

    The agent currently delegates analysis to the configured
    AI provider. SRE tools such as Kubernetes, Prometheus,
    and RAG will be added later.
    """

    def __init__(self, kubeconfig: str) -> None:
        self.provider = GeminiProvider()

        kubernetes_provider = KubernetesEvidenceProvider(
            kubeconfig
        )

        self.evidence_providers: list[EvidenceProvider] = [
            kubernetes_provider,
        ]

        try:
            prometheus_provider = PrometheusEvidenceProvider(
                kubeconfig
            )

            self.evidence_providers.append(
                prometheus_provider
            )
        except Exception:
            # Prometheus is optional.
            pass

    async def analyze_incident(
        self,
        incident_id: str,
        context: dict,
    ) -> AIAnalysisResult:
        """
        Analyze an incident using Kubernetes investigation
        data and the supplied incident context.
        """

        context = dict(context)

        agent_evidence = await self.collect_evidence(
            context={
                "namespace": (
                    context.get("evidence", [{}])[-1].get("namespace")
                ),
                "resource_name": (
                    context.get("evidence", [{}])[-1].get(
                        "resource_name"
                    )
                ),
            },
            providers=self.evidence_providers,
        )

        if agent_evidence:
            context["agent_investigation"] = agent_evidence
        prompt = self._build_prompt(
            incident_id,
            context,
        )

        return await self.provider.analyze(prompt)

    def _build_prompt(
        self,
        incident_id: str,
        context: dict,
    ) -> str:
        """
        Build the initial agent reasoning prompt.
        """

        return f"""
You are the Aegis SRE AI Agent.

Analyze the following incident using ONLY the
provided incident context.

Incident ID:
{incident_id}

Incident context:
{context}

Requirements:

1. Determine the most likely root cause.
2. Explain the reasoning using the available evidence.
3. Provide a concise incident summary.
4. Assign a confidence score between 0.0 and 1.0.
5. Provide practical SRE recommendations.
6. Do not invent evidence.
7. If evidence is insufficient, explicitly state that.
8. Recommendations must be based on available evidence.

Return the required structured analysis.

"""
    
    async def collect_evidence(
        self,
        context: dict,
        providers: list[EvidenceProvider],
    ) -> dict:
        """
        Collect evidence sequentially.

        Later providers can consume evidence produced
        by earlier providers.

        Individual provider failures do not stop RCA.
        """

        collected: dict = {}

        for provider in providers:
            try:
                provider_context = dict(context)

                if collected:
                    provider_context["previous_evidence"] = collected
                    provider_context["kubernetes_evidence"] = collected

                evidence = await provider.collect(
                    provider_context
                )

                if evidence:
                    collected.update(evidence)

            except Exception:
                # Optional evidence providers must never
                # break the RCA pipeline.
                continue

        return collected