"""
Agent, Grounding Gate, and Language Reviewer Interface Contracts.
Defines strict responsibilities for each specialized Microsoft Agent Framework participant.
"""

from abc import ABC, abstractmethod

from shared.domain.enums import AgentStage, LanguageCode
from shared.domain.models import (
    AgentStepTrace,
    GroundingReport,
    LanguageReviewReport,
    UserProfileMemory,
)


class ISpecializedAgent(ABC):
    """Base behavioral contract for each specialized agent module in the sequential pipeline."""

    stage: AgentStage
    agent_name: str

    @abstractmethod
    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Read shared memory, run agent logic, write updates back, and return execution trace."""


class IGroundingVerifier(ABC):
    """Contract for verifying every scheme, rule reason, and document claim is grounded in RAG + Rules."""

    @abstractmethod
    def verify(self, memory: UserProfileMemory) -> GroundingReport:
        """Audit compiled guide artifacts against retrieved scheme chunks and deterministic rules."""


class ILanguageConsistencyReviewer(ABC):
    """Contract for Group-of-3 Add-on Language-Consistency Reviewer Agent."""

    @abstractmethod
    def review_and_repair(
        self,
        *,
        reply_text: str,
        target_language: LanguageCode,
        expected_scheme_names: list[str],
        memory: UserProfileMemory,
    ) -> tuple[str, LanguageReviewReport]:
        """
        Verify final reply matches target_language and keeps every official scheme name intact.
        Automatically repairs missing/altered names or mismatched labels and returns (clean_reply, report).
        """

