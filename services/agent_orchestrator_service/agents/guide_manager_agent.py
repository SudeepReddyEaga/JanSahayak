"""
Module 5: Guide Manager Agent (Separate Agent Module).
Responsibilities:
  - Read CitizenProfile, eligibility_results, and document_checklist from shared memory.
  - Execute the GroundingGate check to guarantee every scheme, reason, and document
    is backed by RAG chunk evidence and deterministic rule passes.
  - Compile the structured citizen guide in the citizen's language containing:
      1) Eligible schemes (with official scheme names kept intact!)
      2) Rule-based reasons for each scheme
      3) Consolidated document checklist
      4) Step-by-step application instructions, official portals & helplines
  - Write draft_guide_text and grounding_report into shared UserProfileMemory.
"""

from typing import Any

from agent_framework import SupportsChatGetResponse

from shared.data.language_packs import LanguagePackRegistry
from shared.domain.enums import AgentStage, EligibilityStatus, LanguageCode
from shared.domain.models import AgentStepTrace, UserProfileMemory
from shared.interfaces.agent_interface import IGroundingVerifier
from services.agent_orchestrator_service.agents.base_specialized_agent import (
    SpecializedPipelineAgent,
)
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)


# Concise native-language action prefix appended alongside official portal URLs across all 12 languages
_LOCALIZED_PORTAL_ACTION: dict[str, str] = {
    "en": "Apply online or at CSC via",
    "hi": "आधिकारिक पोर्टल या नजदीकी CSC केंद्र पर आवेदन करें:",
    "pa": "ਅਧਿਕਾਰਤ ਪੋਰਟਲ ਜਾਂ ਨੇੜਲੇ CSC ਕੇਂਦਰ ਰਾਹੀਂ ਅਰਜ਼ੀ ਦਿਓ:",
    "te": "అధికారిక పోర్టల్ లేదా సమీప CSC/మీసేవా కేంద్రంలో దరఖాస్తు చేయండి:",
    "ta": "அதிகாரப்பூர்வ இணையதளம் அல்லது அருகிலுள்ள CSC மையத்தில் விண்ணப்பிக்கவும்:",
    "bn": "অফিশিয়াল পোর্টাল বা নিকটস্থ CSC কেন্দ্রে আবেদন করুন:",
    "mr": "अधिकृत पोर्टलवर किंवा जवळच्या CSC केंद्रात अर्ज करा:",
    "kn": "ಅಧಿಕೃತ ಪೋರ್ಟಲ್ ಅಥವಾ ಹತ್ತಿರದ CSC ಕೇಂದ್ರದಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ:",
    "gu": "સત્તાવાર પોર્ટલ અથવા નજીકના CSC કેન્દ્ર પર અરજી કરો:",
    "ml": "ഔദ്യോഗിക പോർട്ടൽ അല്ലെങ്കിൽ അടുത്തുള്ള അക്ഷയ/CSC കേന്ദ്രം വഴി അപേക്ഷിക്കുക:",
    "or": "ଅଧିକୃତ ପୋର୍ଟାଲ୍ କିମ୍ବା ନିକଟସ୍ଥ CSC/ମୋ ସେବା କେନ୍ଦ୍ରରେ ଆବେଦନ করুন:",
    "ur": "سرکاری پورٹل یا قریبی CSC مرکز کے ذریعے درخواست دیں:",
}


class GuideManagerAgent(SpecializedPipelineAgent):
    """Compiles the grounded multilingual eligibility guide after verifying GroundingGate."""

    def __init__(
        self,
        *,
        chat_client: SupportsChatGetResponse[Any],
        memory_provider: SharedProfileMemoryContextProvider,
        trace_collector: list[AgentStepTrace],
        grounding_verifier: IGroundingVerifier,
    ) -> None:
        super().__init__(
            stage=AgentStage.GUIDE_MANAGER,
            agent_name="GuideManagerAgent",
            description="Compiles verified eligible schemes, reasons, documents, and application steps.",
            instructions=(
                "You are the Guide Manager. Enforce the GroundingGate verification check and compile "
                "a citizen-friendly guide in their language containing eligible schemes, reasons, "
                "document checklist, and application steps while keeping official scheme names intact."
            ),
            chat_client=chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
        )
        self._grounding_verifier = grounding_verifier

    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Verify grounding invariants and assemble localized welfare guidance text."""
        grounding_report = self._grounding_verifier.verify(memory)
        memory.grounding_report = grounding_report

        lang: LanguageCode = memory.profile.language
        tpl = LanguagePackRegistry.get_template(lang)
        verified_set = set(grounding_report.verified_scheme_ids)

        eligible = [
            r
            for r in memory.eligibility_results
            if r.status == EligibilityStatus.ELIGIBLE and r.scheme_id in verified_set
        ]
        potential = [
            r for r in memory.eligibility_results if r.status == EligibilityStatus.POTENTIAL
        ]

        lines: list[str] = [tpl["greeting"], ""]

        if not eligible:
            lines.append(tpl["no_schemes"])
        else:
            lines.append(f"### {tpl['eligible_heading']} ({len(eligible)})")
            for idx, item in enumerate(eligible, start=1):
                # Keep official scheme name verbatim intact across all languages!
                lines.append(f"{idx}. **{item.official_name}**")
                lines.append(f"   - {tpl['benefit_label']}: {item.localized_benefit_summary or item.benefit_summary}")
                lines.append(f"   - {tpl['reason_label']}: {item.localized_reason or item.reason}")
                lines.append(f"   - {tpl['portal_label']}: {item.official_portal} | {tpl['helpline_label']}: {item.helpline}")

            # Consolidated Document Checklist
            lines.append("")
            lines.append(f"### {tpl['docs_heading']}")
            for doc in memory.document_checklist:
                doc_name = doc.localized_names.get(lang.value, doc.name)
                linked = ", ".join(doc.required_for_schemes)
                lines.append(f"- {doc_name} [{linked}] — {tpl['where_label']}: {doc.where_to_obtain}")

            # Step-by-Step Application Guidance
            lines.append("")
            lines.append(f"### {tpl['steps_heading']}")
            portal_action = _LOCALIZED_PORTAL_ACTION.get(lang.value, _LOCALIZED_PORTAL_ACTION["en"])
            for item in eligible:
                lines.append(f"**{item.official_name}**")
                lines.append(f"  {tpl['step_prefix']} 1: {portal_action} {item.official_portal}")
                for s_idx, step_text in enumerate(item.application_steps, start=2):
                    lines.append(f"  {tpl['step_prefix']} {s_idx}: {step_text}")

        if potential:
            lines.append("")
            lines.append(f"### {tpl['potential_heading']} ({len(potential)})")
            learn_lbl = tpl.get("learn_more_label", tpl["portal_label"])
            for item in potential:
                missing_str = ", ".join(item.missing_fields)
                portal_str = f" | {learn_lbl}: {item.official_portal}" if item.official_portal else ""
                lines.append(
                    f"- **{item.official_name}** ({tpl['missing_fields_note']}: {missing_str}){portal_str}"
                )

        ineligible = [
            r for r in memory.eligibility_results if r.status == EligibilityStatus.INELIGIBLE
        ]
        if ineligible:
            lines.append("")
            other_hdr = tpl.get(
                "other_schemes_heading",
                "Other Government Welfare Schemes Evaluated (Direct Official Portals to Learn More)",
            )
            learn_lbl = tpl.get("learn_more_label", tpl["portal_label"])
            lines.append(f"### {other_hdr} ({len(ineligible)})")
            for item in ineligible:
                lines.append(f"- **{item.official_name}**")
                lines.append(f"   - {tpl['reason_label']}: {item.localized_reason or item.reason}")
                if item.official_portal:
                    lines.append(f"   - {learn_lbl}: {item.official_portal}")

        lines.append("")
        lines.append(f"_{tpl['grounding_note']}_")

        draft_text = "\n".join(lines).strip()
        memory.draft_guide_text = draft_text

        trace = AgentStepTrace(
            stage=self.stage,
            agent_name=self.agent_name,
            status="completed",
            memory_reads=["profile.language", "eligibility_results", "document_checklist"],
            memory_writes=["grounding_report", "draft_guide_text"],
            output_summary=(
                f"Grounding passed={grounding_report.passed} "
                f"(verified={len(grounding_report.verified_scheme_ids)}, coverage={grounding_report.citation_coverage:.0%}); "
                f"compiled draft in '{lang.value}' ({len(draft_text)} chars)."
            ),
        )
        return memory, trace

