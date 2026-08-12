from __future__ import annotations

from abc import ABC, abstractmethod


class EvidenceProvider(ABC):
    """
    Abstract interface for optional AI evidence providers.

    A provider may be unavailable without preventing
    the AI agent from continuing with other evidence.
    """

    @abstractmethod
    async def collect(
        self,
        context: dict,
    ) -> dict:
        """
        Collect additional evidence for the agent.
        """

        raise NotImplementedError
