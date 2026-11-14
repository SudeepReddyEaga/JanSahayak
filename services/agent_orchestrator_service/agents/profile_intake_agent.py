"""
Module 1: Profile Intake Agent (Separate Agent Module).
Responsibilities:
  - Detect the citizen's language across 7 supported languages (en, hi, te, ta, bn, mr, kn).
  - Extract structured demographic and socioeconomic attributes from multilingual text.
  - Merge interactive UI form overrides when provided.
  - Identify missing critical attributes so downstream agents or the citizen can confirm them.
  - Write the normalized CitizenProfile into shared UserProfileMemory.
"""

from typing import Any

from agent_framework import SupportsChatGetResponse

from shared.data.language_packs import LanguagePackRegistry
from shared.domain.enums import AgentStage, LanguageCode
from shared.domain.models import AgentStepTrace, CitizenProfile, UserProfileMemory
from services.agent_orchestrator_service.agents.base_specialized_agent import (
    SpecializedPipelineAgent,
)
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)


class ProfileIntakeAgent(SpecializedPipelineAgent):
    """Collects and normalizes the citizen's profile in their native language."""

    # Core fields checked to compute missing-info hints for interactive users
    RECOMMENDED_FIELDS = ("age", "occupation", "residence_type", "annual_income_inr")

    def __init__(
        self,
        *,
        chat_client: SupportsChatGetResponse[Any],
        memory_provider: SharedProfileMemoryContextProvider,
        trace_collector: list[AgentStepTrace],
        raw_query: str,
        preferred_language: LanguageCode | None = None,
        profile_overrides: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            stage=AgentStage.PROFILE_INTAKE,
            agent_name="ProfileIntakeAgent",
            description="Detects citizen language and extracts structured welfare profile into shared memory.",
            instructions=(
                "You are the Profile Intake Agent. Detect the citizen's language accurately, "
                "extract age, gender, marital status, occupation, rural/urban residence, income, "
                "social category, disability, housing, LPG, and landholding details into shared UserProfileMemory."
            ),
            chat_client=chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
        )
        self._raw_query = raw_query
        self._preferred_language = preferred_language
        self._overrides = profile_overrides

    @classmethod
    def extract_quick_profile(
        cls,
        *,
        raw_query: str,
        preferred_language: LanguageCode | None = None,
        profile_overrides: dict[str, Any] | None = None,
        existing_profile: CitizenProfile | None = None,
    ) -> CitizenProfile:
        """
        Stateless helper shared with Redis Semantic Cache Lookup so incoming queries
        can be canonicalized into a profile signature prior to cache lookup.
        """
        return LanguagePackRegistry.extract_profile_from_text(
            raw_query,
            existing=existing_profile,
            preferred_language=preferred_language,
            overrides=profile_overrides,
        )

    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Extract multilingual profile fields and persist them to shared UserProfileMemory."""
        # Preserve prior session fields only when continuing a multi-turn session, updating from new query + overrides
        extracted = self.extract_quick_profile(
            raw_query=self._raw_query,
            preferred_language=self._preferred_language,
            profile_overrides=self._overrides,
            existing_profile=memory.profile if memory.profile.raw_query else None,
        )
        memory.profile = extracted

        # Identify which key baseline demographic fields remain unspecified
        missing = [
            f for f in self.RECOMMENDED_FIELDS if getattr(extracted, f, None) is None
        ]
        memory.missing_profile_fields = missing

        # Clear stale downstream artifacts if profile is being re-evaluated on a new turn
        memory.retrieved_chunks = []
        memory.retrieved_scheme_ids = []
        memory.eligibility_results = []
        memory.eligible_scheme_ids = []
        memory.potential_scheme_ids = []
        memory.document_checklist = []
        memory.draft_guide_text = ""
        memory.grounding_report = None
        memory.language_review_report = None
        memory.final_reply_text = ""

        extracted_fields = sorted(extracted.canonical_signature().keys())
        trace = AgentStepTrace(
            stage=self.stage,
            agent_name=self.agent_name,
            status="completed",
            memory_reads=["raw_query", "existing_profile"],
            memory_writes=["profile", "missing_profile_fields"],
            output_summary=(
                f"Detected language='{extracted.language.value}', extracted {len(extracted_fields)} profile "
                f"fields ({', '.join(extracted_fields[:8])}); missing={missing}."
            ),
        )
        return memory, trace

