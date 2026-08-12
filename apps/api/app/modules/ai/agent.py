from __future__ import annotations

from abc import ABC, abstractmethod

from app.modules.ai.schemas import AIAnalysisResult


class AIAgent(ABC):
    """
    Abstract interface for the Aegis AI agent.

    The agent is responsible for reasoning over incident
    context and eventually using SRE tools such as
    Kubernetes, Prometheus, and RAG.
    """

    @abstractmethod
    async def analyze_incident(
        self,
        incident_id: str,
        context: dict,
    ) -> AIAnalysisResult:
        """
        Analyze an incident using the supplied context.
        """
        raise NotImplementedError
