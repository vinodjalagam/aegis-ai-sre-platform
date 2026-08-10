from pydantic import BaseModel, Field


class AIRecommendation(BaseModel):
    """
    AI-generated remediation recommendation.
    """

    action: str = Field(
        min_length=1,
    )

    reason: str = Field(
        min_length=1,
    )


class AIAnalysisResult(BaseModel):
    """
    Structured result returned by the AI provider.
    """

    root_cause: str = Field(
        min_length=1,
    )

    summary: str = Field(
        min_length=1,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    recommendations: list[AIRecommendation] = Field(
        default_factory=list,
    )
