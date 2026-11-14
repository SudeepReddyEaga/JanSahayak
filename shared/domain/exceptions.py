"""
Typed Domain Exceptions for clear error propagation and clean HTTP error mapping
across microservices without leaking internal database or stack details.
"""


class DomainError(Exception):
    """Base exception for all domain-level failures."""

    def __init__(self, message: str, *, code: str = "DOMAIN_ERROR") -> None:
        # Store structured machine-readable error code alongside human message
        self.code = code
        super().__init__(message)


class ProfileMemoryError(DomainError):
    """Raised when reading or writing shared user-profile memory fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="PROFILE_MEMORY_ERROR")


class GroundingViolationError(DomainError):
    """Raised when compiled output claims an ungrounded scheme, rule, or document."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="GROUNDING_VIOLATION")


class LanguageConsistencyError(DomainError):
    """Raised when the Language-Consistency Reviewer detects severe language or scheme-name corruption."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="LANGUAGE_CONSISTENCY_ERROR")


class MicroserviceUnavailableError(DomainError):
    """Raised when a downstream microservice fails health or HTTP communication."""

    def __init__(self, service_name: str, detail: str) -> None:
        super().__init__(
            f"Microservice '{service_name}' unavailable: {detail}",
            code="MICROSERVICE_UNAVAILABLE",
        )

