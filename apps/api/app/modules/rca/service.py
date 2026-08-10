"""
Root cause analysis service.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.ai.gemini import GeminiProvider

from app.modules.incidents.evidence.repository import (
    IncidentEvidenceRepository,
)
from app.modules.rca.models import IncidentRCA
from app.modules.rca.repository import RCARepository
from app.modules.rca.schemas import (
    RCACreate,
    RCAAnalysisResponse,
    RCARecommendation,
)
from app.modules.kubernetes.service import KubernetesService

class RCAService:
    """
    Business logic for root cause analysis.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.repository = RCARepository(db)
        self.evidence_repository = IncidentEvidenceRepository(db)
        self.kubernetes_service = KubernetesService()
        self.ai_provider = GeminiProvider()

    async def create(
        self,
        incident_id: str,
        data: RCACreate,
    ) -> IncidentRCA:
        """
        Create an RCA result for an incident.
        """

        rca = IncidentRCA(
            incident_id=incident_id,
            **data.model_dump(),
        )

        return await self.repository.create(rca)

    async def get_by_incident(
        self,
        incident_id: str,
    ) -> IncidentRCA | None:
        """
        Return RCA for an incident.
        """

        return await self.repository.get_by_incident(
            incident_id
        )
    def _collect_kubernetes_context(
        self,
        namespace: str | None,
        resource_name: str | None,
    ) -> dict:
        """
        Collect Kubernetes context for the affected resource.
        """

        if not namespace or not resource_name:
            return {}

        # -------------------------------------------------
        # Pod lookup
        # -------------------------------------------------

        try:
            pod = self.kubernetes_service.find_pod_by_resource(
                namespace,
                resource_name,
            )
        except Exception:
            pod = None

        if pod:
            pod_name = pod["name"]
            container_name = pod.get("container")

            # Pod details are the most important RCA evidence.
            try:
                details = self.kubernetes_service.get_pod_details(
                    namespace,
                    pod_name,
                )
            except Exception:
                details = None

            # Events are supplementary evidence.
            try:
                events = self.kubernetes_service.get_pod_events(
                    namespace,
                    pod_name,
                )
            except Exception:
                events = []

            # Logs are supplementary evidence.
            try:
                logs = self.kubernetes_service.get_pod_logs(
                    namespace,
                    pod_name,
                    container_name,
                    previous=True,
                )
            except Exception:
                logs = ""

            return {
                "resource_type": "pod",
                "pod": pod,
                "details": details,
                "events": events,
                "logs": logs,
            }

        # -------------------------------------------------
        # Node lookup
        # -------------------------------------------------

        try:
            node_name = self.kubernetes_service.find_node_by_resource(
                resource_name,
            )
        except Exception:
            node_name = None

        if node_name:
            try:
                node_details = (
                    self.kubernetes_service.get_node_details(
                        node_name
                    )
                )
            except Exception:
                node_details = None

            return {
                "resource_type": "node",
                "node": node_name,
                "details": node_details,
            }

        return {}
    def _build_ai_prompt(
        self,
        incident_id: str,
        evidence: list,
        kubernetes_context: dict,
    ) -> str:
        """
        Build the RCA prompt from real incident evidence.
        """

        evidence_data = []

        for item in evidence:
            evidence_data.append(
                {
                    "title": item.title,
                    "description": item.description,
                    "query": item.query,
                    "evidence_type": item.evidence_type,
                    "resource_name": item.resource_name,
                    "namespace": item.namespace,
                }
            )

        prompt = f"""
    You are an experienced Site Reliability Engineer.

    Analyze the following production incident using ONLY the
    evidence provided below.

    Incident ID:
    {incident_id}

    Incident evidence:
    {evidence_data}

    Kubernetes context:
    {kubernetes_context}

    Requirements:

    1. Determine the most likely root cause.
    2. Explain the reasoning using the available evidence.
    3. Provide a concise incident summary.
    4. Assign a confidence score between 0.0 and 1.0.
    5. Provide practical recommendations for an SRE.
    6. Do not invent evidence that is not present.
    7. If the evidence is insufficient, explicitly say that the
    root cause cannot be determined with high confidence.
    8. Recommendations must be based on the available evidence.

    Return the result using the required structured format.
    """

        return prompt
    async def analyze_incident(
        self,
        incident_id: str,
    ) -> RCAAnalysisResponse:
        """
        Analyze incident evidence using the configured AI provider.
        """

        evidence = await self.evidence_repository.list_by_incident(
            incident_id
        )

        if not evidence:
            raise ValueError(
                "No evidence found for incident"
            )

        latest = evidence[-1]

        kubernetes_context = self._collect_kubernetes_context(
            latest.namespace,
            latest.resource_name,
        )

        prompt = self._build_ai_prompt(
            incident_id,
            evidence,
            kubernetes_context,
        )

        ai_result = await self.ai_provider.analyze(
            prompt
        )

        existing = await self.repository.get_by_incident(
            incident_id
        )

        if existing:
            existing.recommendations_json = [
                item.model_dump()
                for item in ai_result.recommendations
            ]

            await self.repository.db.commit()
            await self.repository.db.refresh(existing)

        else:
            await self.create(
                incident_id=incident_id,
                data=RCACreate(
                    root_cause=ai_result.root_cause,
                    summary=ai_result.summary,
                    confidence=ai_result.confidence,
                    status="completed",
                    recommendations_json=[
                        item.model_dump()
                        for item in ai_result.recommendations
                    ],
                ),
            )

        recommendations = [
            RCARecommendation(
                action=item.action,
                reason=item.reason,
            )
            for item in ai_result.recommendations
        ]

        return RCAAnalysisResponse(
            incident_id=incident_id,
            root_cause=ai_result.root_cause,
            summary=ai_result.summary,
            confidence=ai_result.confidence,
            recommendations=recommendations,
        )