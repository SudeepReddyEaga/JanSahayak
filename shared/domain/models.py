"""
Core Domain Value Objects & Data Transfer Objects (DTOs).
Every microservice communicates using these validated Pydantic v2 models,
ensuring strict contract consistency across HTTP boundaries and inside
Microsoft Agent Framework sequential pipeline memory.
"""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

from shared.domain.enums import (
    AgentStage,
    CacheStatus,
    EligibilityStatus,
    LanguageCode,
    RuleOperator,
)


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp string for audit trails."""
    return datetime.now(timezone.utc).isoformat()


# ==============================================================================
# 1. Citizen Profile & Shared User-Profile Memory Models
# ==============================================================================


class CitizenProfile(BaseModel):
    """Structured citizen profile extracted and updated by Profile Intake Agent."""

    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Detected or preferred citizen language")
    raw_query: str = Field(default="", description="Latest raw message submitted by the citizen")
    age: int | None = Field(default=None, ge=0, le=120, description="Citizen age in years")
    gender: str | None = Field(default=None, description="Gender: male, female, other")
    marital_status: str | None = Field(default=None, description="Marital status: single, married, widowed, divorced")
    occupation: str | None = Field(default=None, description="Primary occupation category")
    residence_type: str | None = Field(default=None, description="rural, urban, or semi_urban")
    annual_income_inr: int | None = Field(default=None, ge=0, description="Annual household income in INR")
    social_category: str | None = Field(default=None, description="General, OBC, SC, ST, EBC, DNT, Minority")
    education_level: str | None = Field(default=None, description="Current/highest education level")
    state: str | None = Field(default=None, description="Indian State or Union Territory")
    owns_cultivable_land: bool | None = Field(default=None, description="Whether citizen owns agricultural land")
    land_acres: float | None = Field(default=None, ge=0.0, description="Agricultural landholding in acres")
    owns_pucca_house: bool | None = Field(default=None, description="Whether household owns a permanent pucca house")
    has_bpl_card: bool | None = Field(default=None, description="Whether citizen holds a BPL / Antyodaya card")
    has_lpg_connection: bool | None = Field(default=None, description="Whether household already has an LPG gas connection")
    is_pregnant_or_lactating: bool | None = Field(default=None, description="Whether applicant is pregnant or lactating mother")
    has_disability: bool | None = Field(default=None, description="Whether citizen has a benchmark disability")
    disability_percentage: int | None = Field(default=None, ge=0, le=100, description="Certified disability percentage")
    has_girl_child_under_10: bool | None = Field(default=None, description="Whether citizen is parent/guardian of girl child < 10 yrs")
    is_govt_employee: bool | None = Field(default=None, description="Whether citizen is a regular government employee")

    def canonical_signature(self) -> dict[str, Any]:
        """
        Return a normalized, deterministic dictionary of demographic facts (excluding raw_query)
        used for accurate Redis semantic cache profile-equivalence checks.
        """
        data = self.model_dump(exclude={"raw_query"})
        # Normalize string attributes to lowercase for consistent hashing
        return {
            k: (v.value if isinstance(v, LanguageCode) else v.lower() if isinstance(v, str) else v)
            for k, v in data.items()
            if v is not None
        }


class AgentMemoryAuditEntry(BaseModel):
    """Records every read or write performed on shared UserProfileMemory by an agent."""

    agent: str
    action: str  # "read" or "write"
    fields_accessed: list[str] = Field(default_factory=list)
    summary: str = ""
    timestamp: str = Field(default_factory=utc_now_iso)


# ==============================================================================
# 2. Scheme Knowledge Base, Rules & RAG Chunk Models
# ==============================================================================


class RuleCondition(BaseModel):
    """Single atomic deterministic eligibility criterion."""

    field: str = Field(description="Attribute name on CitizenProfile")
    operator: RuleOperator = Field(description="Deterministic comparison operator")
    value: Any = Field(description="Expected threshold or allowed values list")
    description: str = Field(description="Human-readable rule description grounded in scheme policy")


class EligibilityRuleGroup(BaseModel):
    """
    Composite rule block supporting AND (`all_of`) and OR (`any_of`) criteria.
    Enables modeling complex real-world government rules cleanly and declaratively.
    """

    all_of: list[RuleCondition] = Field(default_factory=list)
    any_of_groups: list[list[RuleCondition]] = Field(
        default_factory=list,
        description="Each inner list represents an OR branch (at least one condition in the branch must pass)",
    )


class DocumentRequirement(BaseModel):
    """Structured paper/document required to apply for one or more schemes."""

    doc_id: str
    name: str
    localized_names: dict[str, str] = Field(default_factory=dict)
    description: str
    where_to_obtain: str
    mandatory: bool = True
    required_for_schemes: list[str] = Field(default_factory=list)


class SchemeDefinition(BaseModel):
    """Canonical representation of a Government Welfare Scheme stored in PostgreSQL & RAG."""

    scheme_id: str
    official_name: str
    short_code: str
    ministry: str
    benefit_summary: str
    localized_summaries: dict[str, str] = Field(default_factory=dict)
    target_tags: list[str] = Field(default_factory=list)
    multilingual_keywords: list[str] = Field(default_factory=list)
    full_document_text: str
    rules: EligibilityRuleGroup
    documents: list[DocumentRequirement] = Field(default_factory=list)
    application_steps: list[str] = Field(default_factory=list)
    localized_application_steps: dict[str, list[str]] = Field(default_factory=dict)
    official_portal: str
    helpline: str


class RetrievedSchemeChunk(BaseModel):
    """Single RAG chunk returned by rag-retrieval-service with similarity provenance."""

    chunk_id: str
    scheme_id: str
    official_name: str
    chunk_text: str
    bm25_score: float = 0.0
    vector_score: float = 0.0
    hybrid_score: float = 0.0
    matched_keywords: list[str] = Field(default_factory=list)


class RAGQueryRequest(BaseModel):
    """Request DTO sent by Scheme Retrieval Agent to rag-retrieval-service."""

    query_text: str
    language: LanguageCode = LanguageCode.ENGLISH
    profile: CitizenProfile | None = None
    top_k: int = Field(default=10, ge=1, le=20)
    bypass_cache: bool = False


class RAGQueryResponse(BaseModel):
    """Response DTO returned by rag-retrieval-service with retrieved chunks & cache state."""

    query_text: str
    expanded_query: str
    chunks: list[RetrievedSchemeChunk] = Field(default_factory=list)
    unique_scheme_ids: list[str] = Field(default_factory=list)
    cache_hit: bool = False
    retrieval_latency_ms: float = 0.0


# ==============================================================================
# 3. Eligibility Rule Evaluation, Grounding & Language Review Models
# ==============================================================================


class RuleCheckDetail(BaseModel):
    """Detailed evaluation trace for one atomic Eligibility Rule."""

    field: str
    operator: str
    expected_value: Any
    actual_value: Any
    passed: bool | None = Field(description="True=passed, False=failed, None=profile field missing")
    description: str


class SchemeEligibilityResult(BaseModel):
    """Complete deterministic + RAG-grounded assessment for a single scheme."""

    scheme_id: str
    official_name: str
    ministry: str
    benefit_summary: str
    localized_benefit_summary: str = ""
    status: EligibilityStatus
    reason: str
    localized_reason: str = ""
    passed_rules: list[RuleCheckDetail] = Field(default_factory=list)
    failed_rules: list[RuleCheckDetail] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    rag_score: float = 0.0
    evidence_chunk_ids: list[str] = Field(default_factory=list)
    application_steps: list[str] = Field(default_factory=list)
    official_portal: str = ""
    helpline: str = ""


class GroundingReport(BaseModel):
    """Verification report emitted by the Grounding Gate inside the sequential pipeline."""

    passed: bool
    verified_scheme_ids: list[str] = Field(default_factory=list)
    ungrounded_claims: list[str] = Field(default_factory=list)
    citation_coverage: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: list[str] = Field(default_factory=list)


class LanguageReviewReport(BaseModel):
    """
    Verification report emitted by the Group-of-3 Language-Consistency Reviewer Agent.
    Checks that the reply is written in the citizen's language AND preserves
    all official scheme names intact without corruption or mistranslation.
    """

    target_language: LanguageCode
    detected_reply_language: str
    language_consistent: bool
    script_match_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    scheme_names_checked: list[str] = Field(default_factory=list)
    intact_scheme_names: list[str] = Field(default_factory=list)
    missing_or_altered_scheme_names: list[str] = Field(default_factory=list)
    scheme_names_intact: bool = True
    repairs_applied: list[str] = Field(default_factory=list)
    reviewer_notes: str = ""


class UserProfileMemory(BaseModel):
    """
    Shared User-Profile Memory persisted across PostgreSQL + Redis and accessed
    (read & write) by every specialized agent during sequential orchestration.
    """

    session_id: str
    citizen_id: str = "anonymous"
    profile: CitizenProfile = Field(default_factory=CitizenProfile)
    missing_profile_fields: list[str] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedSchemeChunk] = Field(default_factory=list)
    retrieved_scheme_ids: list[str] = Field(default_factory=list)
    eligibility_results: list[SchemeEligibilityResult] = Field(default_factory=list)
    eligible_scheme_ids: list[str] = Field(default_factory=list)
    potential_scheme_ids: list[str] = Field(default_factory=list)
    document_checklist: list[DocumentRequirement] = Field(default_factory=list)
    draft_guide_text: str = ""
    grounding_report: GroundingReport | None = None
    language_review_report: LanguageReviewReport | None = None
    final_reply_text: str = ""
    audit_log: list[AgentMemoryAuditEntry] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


# ==============================================================================
# 4. API Gateway & Orchestration Request/Response Models
# ==============================================================================


class AgentStepTrace(BaseModel):
    """Observability record for one agent step inside Microsoft Agent Framework SequentialBuilder."""

    stage: AgentStage
    agent_name: str
    status: str = "completed"
    duration_ms: float = 0.0
    memory_reads: list[str] = Field(default_factory=list)
    memory_writes: list[str] = Field(default_factory=list)
    output_summary: str = ""


class ApplicationGuideRequest(BaseModel):
    """Citizen request accepted by API Gateway and Agent Orchestrator."""

    query: str = Field(min_length=1, description="Citizen's natural-language query in any supported language")
    session_id: str | None = Field(default=None, description="Optional session ID to continue an existing conversation")
    preferred_language: LanguageCode | None = Field(
        default=None,
        description="Optional explicit language override; auto-detected when omitted",
    )
    profile_overrides: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured form attributes provided interactively from the UI",
    )
    bypass_cache: bool = Field(default=False, description="Skip Redis cache lookup when testing live pipeline execution")


class ApplicationGuideResponse(BaseModel):
    """Complete structured & localized response returned to the citizen UI and API callers."""

    session_id: str
    detected_language: LanguageCode
    citizen_profile: CitizenProfile
    missing_profile_fields: list[str] = Field(default_factory=list)
    eligible_schemes: list[SchemeEligibilityResult] = Field(default_factory=list)
    potential_schemes: list[SchemeEligibilityResult] = Field(default_factory=list)
    ineligible_schemes: list[SchemeEligibilityResult] = Field(default_factory=list)
    document_checklist: list[DocumentRequirement] = Field(default_factory=list)
    final_reply: str
    grounding_report: GroundingReport
    language_review_report: LanguageReviewReport
    pipeline_traces: list[AgentStepTrace] = Field(default_factory=list)
    memory_audit_log: list[AgentMemoryAuditEntry] = Field(default_factory=list)
    cache_status: CacheStatus = CacheStatus.MISS
    cache_similarity: float | None = None
    total_latency_ms: float = 0.0
    framework: str = "Microsoft Agent Framework (SequentialBuilder)"


# ==============================================================================
# 5. 10-Profile Evaluation Benchmark Models
# ==============================================================================


class EvaluationProfileResult(BaseModel):
    """Evaluation outcome for a single ground-truth citizen profile."""

    profile_id: str
    label: str
    language: LanguageCode
    query: str
    expected_scheme_ids: list[str]
    predicted_scheme_ids: list[str]
    true_positives: list[str]
    false_positives: list[str]
    false_negatives: list[str]
    precision: float
    recall: float
    f1_score: float
    exact_match: bool
    grounding_passed: bool
    language_consistent: bool
    scheme_names_intact: bool
    latency_ms: float


class EvaluationSummary(BaseModel):
    """Aggregated precision, recall, F1, grounding, and language consistency metrics across 10 profiles."""

    run_id: str
    timestamp: str = Field(default_factory=utc_now_iso)
    total_profiles: int
    macro_precision: float
    macro_recall: float
    macro_f1: float
    micro_precision: float
    micro_recall: float
    micro_f1: float
    exact_match_rate: float
    grounding_pass_rate: float
    language_consistency_rate: float
    scheme_name_preservation_rate: float
    avg_latency_ms: float
    profile_results: list[EvaluationProfileResult] = Field(default_factory=list)


# ==============================================================================
# 6. Voice & Speech Microservice Models (STT / TTS Locale Support)
# ==============================================================================


class VoiceLocaleSpec(BaseModel):
    """Describes browser & service speech support metadata for one citizen language."""

    language: LanguageCode
    display_name: str
    native_name: str
    bcp47_tag: str
    tts_rate_default: float = 1.0
    rtl: bool = False
    sample_spoken_prompt: str = ""


class PrepareSpeechRequest(BaseModel):
    """Request DTO sent to voice-speech-service to convert Markdown reply to spoken text."""

    text: str = Field(min_length=1)
    language: LanguageCode = LanguageCode.ENGLISH


class PreparedSpeechPayload(BaseModel):
    """Sanitized spoken text chunks and BCP-47 speech parameters returned by voice service."""

    language: LanguageCode
    bcp47_tag: str
    display_name: str
    rtl: bool = False
    spoken_text: str
    segments: list[str] = Field(default_factory=list)
    recommended_rate: float = 1.0


