"""
Module 3: Eligibility Rule Agent (Separate Agent Module).
Responsibilities:
  - Read CitizenProfile and RAG-retrieved candidate schemes from shared UserProfileMemory.
  - Evaluate deterministic EligibilityRuleGroup conditions using the Strategy Pattern
    over RuleOperator comparators.
  - Classify each retrieved scheme as ELIGIBLE, POTENTIAL (missing 1-2 facts), or INELIGIBLE.
  - Provide rule-by-rule audit reasons grounded in scheme RAG chunks.
  - Write eligibility_results, eligible_scheme_ids, and potential_scheme_ids to shared memory.
"""

from collections.abc import Callable
from typing import Any

from agent_framework import SupportsChatGetResponse

from shared.data.language_packs import LanguagePackRegistry
from shared.domain.enums import AgentStage, EligibilityStatus, LanguageCode, RuleOperator
from shared.domain.models import (
    AgentStepTrace,
    CitizenProfile,
    RuleCheckDetail,
    RuleCondition,
    SchemeDefinition,
    SchemeEligibilityResult,
    UserProfileMemory,
)
from services.agent_orchestrator_service.agents.base_specialized_agent import (
    SpecializedPipelineAgent,
)
from services.agent_orchestrator_service.clients.rag_client import IRAGRetrievalClient
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)


def _normalize_scalar(value: Any) -> Any:
    """Normalize enum/string scalars for deterministic case-insensitive comparisons."""
    if isinstance(value, str):
        return value.strip().lower()
    return value


# Strategy table mapping RuleOperator enum values to pure deterministic comparator functions
_OPERATOR_STRATEGIES: dict[RuleOperator, Callable[[Any, Any], bool]] = {
    RuleOperator.EQ: lambda actual, expected: _normalize_scalar(actual) == _normalize_scalar(expected),
    RuleOperator.NEQ: lambda actual, expected: _normalize_scalar(actual) != _normalize_scalar(expected),
    RuleOperator.GTE: lambda actual, expected: actual >= expected,
    RuleOperator.LTE: lambda actual, expected: actual <= expected,
    RuleOperator.GT: lambda actual, expected: actual > expected,
    RuleOperator.LT: lambda actual, expected: actual < expected,
    RuleOperator.IN: lambda actual, expected: _normalize_scalar(actual) in [_normalize_scalar(v) for v in expected],
    RuleOperator.NOT_IN: lambda actual, expected: _normalize_scalar(actual) not in [_normalize_scalar(v) for v in expected],
    RuleOperator.BOOL_IS: lambda actual, expected: bool(actual) is bool(expected),
}


class EligibilityRuleAgent(SpecializedPipelineAgent):
    """Applies deterministic eligibility rules over RAG-retrieved scheme candidates."""

    def __init__(
        self,
        *,
        chat_client: SupportsChatGetResponse[Any],
        memory_provider: SharedProfileMemoryContextProvider,
        trace_collector: list[AgentStepTrace],
        rag_client: IRAGRetrievalClient,
    ) -> None:
        super().__init__(
            stage=AgentStage.ELIGIBILITY_RULE,
            agent_name="EligibilityRuleAgent",
            description="Applies deterministic policy rules against citizen profile and retrieved schemes.",
            instructions=(
                "You are the Eligibility Rule Agent. Evaluate ONLY schemes retrieved by RAG using "
                "deterministic eligibility rules, recording every passed and failed rule with reasons."
            ),
            chat_client=chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
        )
        self._rag_client = rag_client

    @staticmethod
    def evaluate_condition(profile: CitizenProfile, cond: RuleCondition) -> RuleCheckDetail:
        """
        Evaluate one atomic RuleCondition against CitizenProfile.
        Returns passed=None if the required citizen attribute has not been provided yet.
        """
        actual = getattr(profile, cond.field, None)
        if actual is None:
            return RuleCheckDetail(
                field=cond.field,
                operator=cond.operator.value,
                expected_value=cond.value,
                actual_value=None,
                passed=None,
                description=cond.description,
            )

        comparator = _OPERATOR_STRATEGIES[cond.operator]
        try:
            outcome = bool(comparator(actual, cond.value))
        except TypeError:
            outcome = False

        return RuleCheckDetail(
            field=cond.field,
            operator=cond.operator.value,
            expected_value=cond.value,
            actual_value=actual,
            passed=outcome,
            description=cond.description,
        )

    @classmethod
    def evaluate_scheme(
        cls,
        *,
        scheme: SchemeDefinition,
        profile: CitizenProfile,
        rag_score: float,
        chunk_ids: list[str],
    ) -> SchemeEligibilityResult:
        """Evaluate composite all_of + any_of_groups eligibility rules for one scheme."""
        passed_rules: list[RuleCheckDetail] = []
        failed_rules: list[RuleCheckDetail] = []
        missing_fields: list[str] = []

        # 1. Evaluate mandatory AND (`all_of`) conditions
        for cond in scheme.rules.all_of:
            detail = cls.evaluate_condition(profile, cond)
            if detail.passed is True:
                passed_rules.append(detail)
            elif detail.passed is False:
                failed_rules.append(detail)
            else:
                if cond.field not in missing_fields:
                    missing_fields.append(cond.field)

        # 2. Evaluate OR branches (`any_of_groups`): each branch passes if >= 1 condition passes
        or_missing: list[str] = []
        for branch in scheme.rules.any_of_groups:
            branch_details = [cls.evaluate_condition(profile, c) for c in branch]
            branch_passed = [d for d in branch_details if d.passed is True]
            branch_unknown = [d for d in branch_details if d.passed is None]

            if branch_passed:
                passed_rules.extend(branch_passed)
            elif branch_unknown:
                # At least one branch criterion is unknown; record as missing confirmation
                for d in branch_unknown:
                    if d.field not in or_missing:
                        or_missing.append(d.field)
            else:
                # Every option in the OR branch evaluated to False -> explicit failure
                failed_rules.extend(branch_details)

        # Merge missing fields from OR branches only if no branch already passed
        for f in or_missing:
            if f not in missing_fields:
                missing_fields.append(f)

        # 3. Determine final tri-state EligibilityStatus
        if failed_rules:
            status = EligibilityStatus.INELIGIBLE
        elif not missing_fields and passed_rules:
            status = EligibilityStatus.ELIGIBLE
        elif passed_rules and len(missing_fields) <= 2:
            status = EligibilityStatus.POTENTIAL
        else:
            status = EligibilityStatus.INELIGIBLE

        # 4. Build concise English + localized rule justification
        lang: LanguageCode = profile.language
        tpl = LanguagePackRegistry.get_template(lang)
        localized_summary = scheme.localized_summaries.get(lang.value, scheme.benefit_summary)

        if status == EligibilityStatus.ELIGIBLE:
            criteria_text = "; ".join(
                f"{d.field}={d.actual_value} ({d.description})" for d in passed_rules
            )
            reason = f"Qualified all criteria: {criteria_text}."
            localized_reason = f"{tpl['reason_prefix']}: {', '.join(f'{d.field}={d.actual_value}' for d in passed_rules)}."
        elif status == EligibilityStatus.POTENTIAL:
            reason = (
                f"Matched {len(passed_rules)} criteria, pending confirmation of: "
                f"{', '.join(missing_fields)}."
            )
            localized_reason = f"{tpl['missing_fields_note']}: {', '.join(missing_fields)}."
        else:
            fail_text = "; ".join(
                f"{d.field}={d.actual_value} != {d.expected_value}" for d in failed_rules
            ) or f"missing required fields ({', '.join(missing_fields)})"
            reason = f"Excluded due to: {fail_text}."
            localized_reason = reason

        return SchemeEligibilityResult(
            scheme_id=scheme.scheme_id,
            official_name=scheme.official_name,
            ministry=scheme.ministry,
            benefit_summary=scheme.benefit_summary,
            localized_benefit_summary=localized_summary,
            status=status,
            reason=reason,
            localized_reason=localized_reason,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            missing_fields=missing_fields,
            rag_score=rag_score,
            evidence_chunk_ids=chunk_ids,
            application_steps=scheme.application_steps,
            official_portal=scheme.official_portal,
            helpline=scheme.helpline,
        )

    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Evaluate every RAG-retrieved candidate scheme against deterministic policy rules."""
        chunk_map: dict[str, tuple[float, list[str]]] = {}
        for chunk in memory.retrieved_chunks:
            score, cids = chunk_map.get(chunk.scheme_id, (0.0, []))
            chunk_map[chunk.scheme_id] = (max(score, chunk.hybrid_score), [*cids, chunk.chunk_id])

        results: list[SchemeEligibilityResult] = []
        for scheme_id in memory.retrieved_scheme_ids:
            scheme = await self._rag_client.get_scheme(scheme_id)
            if scheme is None:
                continue
            rag_score, chunk_ids = chunk_map.get(scheme_id, (0.0, []))
            res = self.evaluate_scheme(
                scheme=scheme,
                profile=memory.profile,
                rag_score=rag_score,
                chunk_ids=chunk_ids,
            )
            results.append(res)

        # Sort eligible schemes first, then potential, then ineligible, preserving RAG score order
        priority = {
            EligibilityStatus.ELIGIBLE: 0,
            EligibilityStatus.POTENTIAL: 1,
            EligibilityStatus.INELIGIBLE: 2,
        }
        results.sort(key=lambda r: (priority[r.status], -r.rag_score))

        eligible_ids = [r.scheme_id for r in results if r.status == EligibilityStatus.ELIGIBLE]
        potential_ids = [r.scheme_id for r in results if r.status == EligibilityStatus.POTENTIAL]

        memory.eligibility_results = results
        memory.eligible_scheme_ids = eligible_ids
        memory.potential_scheme_ids = potential_ids

        trace = AgentStepTrace(
            stage=self.stage,
            agent_name=self.agent_name,
            status="completed",
            memory_reads=["profile", "retrieved_scheme_ids", "retrieved_chunks"],
            memory_writes=["eligibility_results", "eligible_scheme_ids", "potential_scheme_ids"],
            output_summary=(
                f"Evaluated {len(results)} RAG candidates: "
                f"{len(eligible_ids)} eligible {eligible_ids}, "
                f"{len(potential_ids)} potential {potential_ids}."
            ),
        )
        return memory, trace

