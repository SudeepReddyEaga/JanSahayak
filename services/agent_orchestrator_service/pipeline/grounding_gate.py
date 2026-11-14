"""
Explicit Grounding Verification Gate (IGroundingVerifier implementation).
Audits every recommended scheme, eligibility rule justification, and required
document against RAG retrieval citations and deterministic rule evaluation logs.
"""

from shared.domain.enums import EligibilityStatus
from shared.domain.models import GroundingReport, UserProfileMemory
from shared.interfaces.agent_interface import IGroundingVerifier


class GroundingGate(IGroundingVerifier):
    """
    Pipeline Grounding Gate executed prior to final citizen response compilation.
    Ensures zero ungrounded scheme recommendations or hallucinated eligibility claims.
    """

    def verify(self, memory: UserProfileMemory) -> GroundingReport:
        """
        Verify three strict grounding invariants on shared UserProfileMemory:
          1. Every eligible scheme was retrieved by RAG with positive relevance & chunk IDs.
          2. Every eligible scheme passed deterministic rule checks with zero failed rules.
          3. Every document checklist item traces back to at least one verified eligible scheme.
        """
        retrieved_set = set(memory.retrieved_scheme_ids)
        eligible_results = [
            r for r in memory.eligibility_results if r.status == EligibilityStatus.ELIGIBLE
        ]
        eligible_id_set = {r.scheme_id for r in eligible_results}

        verified_ids: list[str] = []
        ungrounded_claims: list[str] = []
        notes: list[str] = []
        cited_count = 0

        for res in eligible_results:
            has_rag_grounding = res.scheme_id in retrieved_set and bool(res.evidence_chunk_ids)
            has_rule_grounding = len(res.failed_rules) == 0 and len(res.passed_rules) > 0

            if has_rag_grounding and has_rule_grounding:
                verified_ids.append(res.scheme_id)
                cited_count += 1
            else:
                reason = []
                if not has_rag_grounding:
                    reason.append("missing RAG chunk citation")
                if not has_rule_grounding:
                    reason.append("deterministic rule check incomplete")
                ungrounded_claims.append(f"{res.scheme_id}: {', '.join(reason)}")

        # Audit document checklist grounding against verified eligible schemes
        for doc in memory.document_checklist:
            if eligible_id_set and not any(sid in eligible_id_set for sid in doc.required_for_schemes):
                ungrounded_claims.append(
                    f"Document '{doc.doc_id}' is not linked to any verified eligible scheme."
                )

        if not eligible_results:
            notes.append("Zero schemes qualified deterministically; negative-result grounding verified.")
            coverage = 1.0
        else:
            coverage = round(cited_count / len(eligible_results), 4)
            notes.append(
                f"Verified {len(verified_ids)}/{len(eligible_results)} eligible schemes against "
                "RAG document chunks and deterministic rules."
            )

        passed = len(ungrounded_claims) == 0
        return GroundingReport(
            passed=passed,
            verified_scheme_ids=verified_ids,
            ungrounded_claims=ungrounded_claims,
            citation_coverage=coverage,
            notes=notes,
        )

