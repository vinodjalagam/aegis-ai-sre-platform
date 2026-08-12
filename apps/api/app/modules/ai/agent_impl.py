from __future__ import annotations

from app.modules.ai.agent import AIAgent
from app.modules.ai.gemini import GeminiProvider
from app.modules.ai.schemas import AIAnalysisResult
from app.modules.ai.tools.kubernetes import KubernetesInvestigationTool

class AegisAgent(AIAgent):
    """
    Initial Aegis AI agent.

    The agent currently delegates analysis to the configured
    AI provider. SRE tools such as Kubernetes, Prometheus,
    and RAG will be added later.
    """

    def __init__(self, kubeconfig: str) -> None:
        self.provider = GeminiProvider()
        self.kubernetes_tool = KubernetesInvestigationTool(
            kubeconfig
        )

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

        evidence = context.get("evidence", [])

        if evidence:
            latest = evidence[-1]

            namespace = latest.get("namespace")
            resource_name = latest.get("resource_name")

            if namespace and resource_name:
                investigation = (
                    self.kubernetes_tool.investigate_resource(
                        namespace=namespace,
                        resource_name=resource_name,
                    )
                )

                context["agent_investigation"] = investigation
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
    def investigate_pod(
        self,
        namespace: str,
        pod_name: str,
    ) -> dict:
        """
        Investigate a Kubernetes pod using the
        read-only Kubernetes AI tool.
        """

        return self.kubernetes_tool.investigate_pod(
            namespace=namespace,
            pod_name=pod_name,
        )
