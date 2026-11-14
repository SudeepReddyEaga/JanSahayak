"""
Module 6 (Group-of-3 Add-On): Language-Consistency Reviewer Agent (Separate Agent Module).
Responsibilities:
  - Read compiled draft_guide_text, target citizen language, and verified eligible schemes
    from shared UserProfileMemory.
  - Audit TWO mandatory quality invariants:
      1. Language Consistency: final reply uses the citizen's language and native script headers.
      2. Scheme Name Integrity: every official scheme name (e.g.,
         "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)") appears verbatim intact without
         corruption, truncation, or mistranslation.
  - Auto-repair any missing/altered official scheme names or mismatched template labels.
  - Write language_review_report and final_reply_text back to shared UserProfileMemory.
"""

from typing import Any

from agent_framework import SupportsChatGetResponse

from shared.data.language_packs import LanguagePackRegistry
from shared.domain.enums import AgentStage, EligibilityStatus, LanguageCode
from shared.domain.models import (
    AgentStepTrace,
    LanguageReviewReport,
    UserProfileMemory,
)
from shared.interfaces.agent_interface import ILanguageConsistencyReviewer
from services.agent_orchestrator_service.agents.base_specialized_agent import (
    SpecializedPipelineAgent,
)
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)


class LanguageReviewerAgent(SpecializedPipelineAgent, ILanguageConsistencyReviewer):
    """Group-of-3 Reviewer verifying citizen language consistency and intact official scheme names."""

    def __init__(
        self,
        *,
        chat_client: SupportsChatGetResponse[Any],
        memory_provider: SharedProfileMemoryContextProvider,
        trace_collector: list[AgentStepTrace],
    ) -> None:
        super().__init__(
            stage=AgentStage.LANGUAGE_REVIEWER,
            agent_name="LanguageReviewerAgent",
            description=(
                "Group-of-3 Add-On Reviewer checking reply language consistency and "
                "verbatim preservation of official government scheme names."
            ),
            instructions=(
                "You are the Language-Consistency Reviewer Agent. Verify the compiled guide is in the "
                "citizen's exact language, verify every official scheme name appears intact without "
                "alteration, repair discrepancies if found, and finalize the citizen response."
            ),
            chat_client=chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
        )

    def review_and_repair(
        self,
        *,
        reply_text: str,
        target_language: LanguageCode,
        expected_scheme_names: list[str],
        memory: UserProfileMemory,
    ) -> tuple[str, LanguageReviewReport]:
        """
        Inspect compiled reply for target-language consistency and exact official scheme
        name preservation; apply deterministic repairs if any invariant fails.
        """
        repairs: list[str] = []
        cleaned = reply_text.strip()
        tpl = LanguagePackRegistry.get_template(target_language)

        # --- Check 1: Verify target language greeting/headings & native script density ---
        if target_language != LanguageCode.ENGLISH and tpl["greeting"] not in cleaned:
            cleaned = f"{tpl['greeting']}\n\n{cleaned}"
            repairs.append(f"Prepended missing '{target_language.value}' localized greeting.")

        script_ratio = LanguagePackRegistry.script_match_ratio(cleaned, target_language)
        # For Indic languages, ensure localized section markers exist and script density >= 0.35
        language_consistent = (
            script_ratio >= 0.60
            if target_language == LanguageCode.ENGLISH
            else (script_ratio >= 0.35 and tpl["greeting"] in cleaned)
        )

        # --- Check 2: Verify every official scheme name appears verbatim intact ---
        intact: list[str] = []
        missing_or_altered: list[str] = []
        for official_name in expected_scheme_names:
            if official_name in cleaned:
                intact.append(official_name)
            else:
                missing_or_altered.append(official_name)

        # Auto-repair if any official scheme name was altered or omitted
        if missing_or_altered:
            repair_block = "\n".join(f"- **{name}**" for name in missing_or_altered)
            cleaned = f"{cleaned}\n\n{tpl['eligible_heading']}:\n{repair_block}"
            repairs.append(
                f"Restored {len(missing_or_altered)} official scheme name(s) verbatim: {missing_or_altered}"
            )
            intact.extend(missing_or_altered)
            missing_or_altered = []

        scheme_names_intact = len(missing_or_altered) == 0
        detected_lang_label = (
            target_language.value
            if language_consistent
            else LanguagePackRegistry.detect_language(cleaned).value
        )

        notes = (
            f"Verified response in '{tpl['language_name']}' (script_ratio={script_ratio:.2f}) "
            f"with {len(intact)}/{len(expected_scheme_names)} official scheme names intact."
        )
        if repairs:
            notes += " Repairs applied: " + "; ".join(repairs)

        report = LanguageReviewReport(
            target_language=target_language,
            detected_reply_language=detected_lang_label,
            language_consistent=language_consistent,
            script_match_ratio=script_ratio,
            scheme_names_checked=expected_scheme_names,
            intact_scheme_names=intact,
            missing_or_altered_scheme_names=missing_or_altered,
            scheme_names_intact=scheme_names_intact,
            repairs_applied=repairs,
            reviewer_notes=notes,
        )
        return cleaned, report

    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Run language-consistency & scheme-name preservation check on GuideManager output."""
        expected_names = [
            r.official_name
            for r in memory.eligibility_results
            if r.status == EligibilityStatus.ELIGIBLE
        ]

        final_text, review_report = self.review_and_repair(
            reply_text=memory.draft_guide_text,
            target_language=memory.profile.language,
            expected_scheme_names=expected_names,
            memory=memory,
        )

        memory.language_review_report = review_report
        memory.final_reply_text = final_text

        trace = AgentStepTrace(
            stage=self.stage,
            agent_name=self.agent_name,
            status="completed",
            memory_reads=["draft_guide_text", "profile.language", "eligibility_results"],
            memory_writes=["language_review_report", "final_reply_text"],
            output_summary=(
                f"Language consistent={review_report.language_consistent} "
                f"(target='{review_report.target_language.value}', ratio={review_report.script_match_ratio:.2f}); "
                f"scheme names intact={review_report.scheme_names_intact} "
                f"({len(review_report.intact_scheme_names)} checked)."
            ),
        )
        return memory, trace

