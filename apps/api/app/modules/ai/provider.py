from abc import ABC, abstractmethod

from app.modules.ai.schemas import AIAnalysisResult


class AIProvider(ABC):
    """
    Abstract interface for AI providers.

    RCA business logic depends on this interface,
    not on a specific AI vendor.
    """

    @abstractmethod
    async def analyze(
        self,
        prompt: str,
    ) -> AIAnalysisResult:
        """
        Analyze the supplied prompt and return
        a structured AI analysis.
        """
        raise NotImplementedError
