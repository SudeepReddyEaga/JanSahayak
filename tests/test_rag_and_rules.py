"""Tests for Hybrid RAG Retrieval, Deterministic Rule Boundaries, and GroundingGate."""

from shared.data.schemes_catalog import get_scheme_by_id
from shared.domain.enums import EligibilityStatus, LanguageCode
from shared.domain.models import (
    CitizenProfile,
    DocumentRequirement,
    RuleCheckDetail,
    SchemeEligibilityResult,
    UserProfileMemory,
)
from services.agent_orchestrator_service.agents.eligibility_rule_agent import EligibilityRuleAgent
from services.agent_orchestrator_service.pipeline.grounding_gate import GroundingGate


def test_rag_hybrid_retrieval_and_cache(pipeline_bundle):
    """Verify hybrid BM25+Vector RAG retrieves relevant schemes and caches repeat queries."""
    retriever = pipeline_bundle["retriever"]
    profile = CitizenProfile(
        language=LanguageCode.HINDI,
        age=65,
        occupation="farmer",
        residence_type="rural",
        owns_cultivable_land=True,
        has_bpl_card=True,
        owns_pucca_house=False,
    )

    r1 = retriever.retrieve_with_cache(
        query_text="किसान योजना और घर",
        language=LanguageCode.HINDI,
        profile=profile,
        top_k=10,
    )
    assert r1.cache_hit is False
    assert "PM-KISAN" in r1.unique_scheme_ids
    assert "PMAY-G" in r1.unique_scheme_ids

    r2 = retriever.retrieve_with_cache(
        query_text="किसान योजना और घर",
        language=LanguageCode.HINDI,
        profile=profile,
        top_k=10,
    )
    assert r2.cache_hit is True
    assert r2.unique_scheme_ids == r1.unique_scheme_ids

    # Verify runtime scheme upsert refreshes chunks via shared upsert_scheme_orm helper
    scheme_repo = pipeline_bundle["scheme_repo"]
    pm_kisan = scheme_repo.get_scheme("PM-KISAN")
    assert pm_kisan is not None
    updated = pm_kisan.model_copy(update={"helpline": "155261-VERIFIED"})
    scheme_repo.upsert_scheme(updated)
    reloaded = scheme_repo.get_scheme("PM-KISAN")
    assert reloaded is not None and reloaded.helpline == "155261-VERIFIED"


def test_deterministic_rule_boundaries():
    """Verify boundary conditions across age, income, disability percentage, and govt status."""
    ignoaps = get_scheme_by_id("IGNOAPS")
    assert ignoaps is not None

    # Age 59 fails IGNOAPS while Age 60 passes
    p59 = CitizenProfile(age=59, has_bpl_card=True, annual_income_inr=100000)
    p60 = CitizenProfile(age=60, has_bpl_card=True, annual_income_inr=100000)
    assert EligibilityRuleAgent.evaluate_scheme(scheme=ignoaps, profile=p59, rag_score=0.9, chunk_ids=["c1"]).status == EligibilityStatus.INELIGIBLE
    assert EligibilityRuleAgent.evaluate_scheme(scheme=ignoaps, profile=p60, rag_score=0.9, chunk_ids=["c1"]).status == EligibilityStatus.ELIGIBLE

    # IGNDPS severe disability threshold >= 80%
    igndps = get_scheme_by_id("IGNDPS")
    assert igndps is not None
    p79 = CitizenProfile(age=40, has_disability=True, disability_percentage=79, has_bpl_card=True)
    p80 = CitizenProfile(age=40, has_disability=True, disability_percentage=80, has_bpl_card=True)
    assert EligibilityRuleAgent.evaluate_scheme(scheme=igndps, profile=p79, rag_score=0.9, chunk_ids=["c1"]).status == EligibilityStatus.INELIGIBLE
    assert EligibilityRuleAgent.evaluate_scheme(scheme=igndps, profile=p80, rag_score=0.9, chunk_ids=["c1"]).status == EligibilityStatus.ELIGIBLE


def test_grounding_gate_blocks_ungrounded_claims():
    """Ensure GroundingGate flags schemes missing RAG citations or passing rules."""
    gate = GroundingGate()
    memory = UserProfileMemory(
        session_id="ground-test",
        retrieved_scheme_ids=["PM-KISAN"],
        eligibility_results=[
            SchemeEligibilityResult(
                scheme_id="FAKE-UNRETRIEVED",
                official_name="Fake Unretrieved Scheme",
                ministry="Test",
                benefit_summary="Test",
                status=EligibilityStatus.ELIGIBLE,
                reason="None",
                passed_rules=[
                    RuleCheckDetail(
                        field="age",
                        operator="gte",
                        expected_value=18,
                        actual_value=30,
                        passed=True,
                        description="age >= 18",
                    )
                ],
                evidence_chunk_ids=[],  # Missing chunk citation!
            )
        ],
        document_checklist=[
            DocumentRequirement(
                doc_id="ORPHAN-DOC",
                name="Orphan Paper",
                description="Ungrounded",
                where_to_obtain="Nowhere",
                required_for_schemes=["NON-EXISTENT"],
            )
        ],
    )
    report = gate.verify(memory)
    assert report.passed is False
    assert len(report.ungrounded_claims) >= 2

