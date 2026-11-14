"""
Domain Enumerations for the Multilingual Government Scheme Eligibility Guide.
Using explicit Enums guarantees type safety, eliminates magic strings across
microservices, and documents supported languages, agents, rules, and cache states.
"""

from enum import Enum


class LanguageCode(str, Enum):
    """Supported citizen communication and voice interaction languages (12 languages)."""

    ENGLISH = "en"
    HINDI = "hi"
    PUNJABI = "pa"
    TELUGU = "te"
    TAMIL = "ta"
    BENGALI = "bn"
    MARATHI = "mr"
    KANNADA = "kn"
    GUJARATI = "gu"
    MALAYALAM = "ml"
    ODIA = "or"
    URDU = "ur"


class AgentStage(str, Enum):
    """Ordered stages in the Microsoft Agent Framework Sequential Pipeline."""

    PROFILE_INTAKE = "profile_intake_agent"
    SCHEME_RETRIEVAL = "scheme_retrieval_agent"
    ELIGIBILITY_RULE = "eligibility_rule_agent"
    DOCUMENT_CHECKLIST = "document_checklist_agent"
    GUIDE_MANAGER = "guide_manager_agent"
    LANGUAGE_REVIEWER = "language_reviewer_agent"


class EligibilityStatus(str, Enum):
    """Tri-state eligibility outcome computed by the Deterministic Rule Engine."""

    ELIGIBLE = "eligible"
    POTENTIAL = "potential"  # Missing 1-2 optional/unstated citizen profile attributes
    INELIGIBLE = "ineligible"


class RuleOperator(str, Enum):
    """Supported deterministic comparison operators for the Rule Engine Strategy Pattern."""

    EQ = "eq"
    NEQ = "neq"
    GTE = "gte"
    LTE = "lte"
    GT = "gt"
    LT = "lt"
    IN = "in"
    NOT_IN = "not_in"
    BOOL_IS = "bool_is"


class CacheStatus(str, Enum):
    """Redis query cache resolution status returned in API responses."""

    EXACT_HIT = "exact_hit"
    SEMANTIC_HIT = "semantic_hit"
    MISS = "miss"
    BYPASSED = "bypassed"

