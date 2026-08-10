from google import genai
from google.genai import types

from app.core.config.settings import settings
from app.modules.ai.provider import AIProvider
from app.modules.ai.schemas import AIAnalysisResult


class GeminiProvider(AIProvider):
    """
    Gemini implementation of the AI provider.
    """

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

        self.model = settings.gemini_model

    async def analyze(
        self,
        prompt: str,
    ) -> AIAnalysisResult:
        """
        Send the evidence to Gemini and return
        a validated structured RCA result.
        """

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIAnalysisResult,
            ),
        )

        if not response.parsed:
            raise ValueError(
                "Gemini returned an empty or invalid analysis"
            )

        return AIAnalysisResult.model_validate(
            response.parsed
        )
