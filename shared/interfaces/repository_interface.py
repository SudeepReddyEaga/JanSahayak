"""
Repository Interface Contracts (Repository Pattern + Dependency Inversion Principle).
Abstracts PostgreSQL/SQLite persistence operations away from domain services.
"""

from abc import ABC, abstractmethod

from shared.domain.models import (
    AgentMemoryAuditEntry,
    EvaluationSummary,
    SchemeDefinition,
    UserProfileMemory,
)


class IProfileMemoryRepository(ABC):
    """Persistence contract for shared UserProfileMemory and per-agent audit trails."""

    @abstractmethod
    def get_memory(self, session_id: str) -> UserProfileMemory | None:
        """Fetch UserProfileMemory by session_id, returning None if not found."""

    @abstractmethod
    def upsert_memory(self, memory: UserProfileMemory) -> UserProfileMemory:
        """Create or update UserProfileMemory along with its latest audit trail."""

    @abstractmethod
    def append_audit_entry(self, session_id: str, entry: AgentMemoryAuditEntry) -> UserProfileMemory:
        """Atomically append an agent read/write audit record to an existing session."""

    @abstractmethod
    def list_sessions(self, limit: int = 20) -> list[UserProfileMemory]:
        """Return the most recently updated citizen sessions."""


class ISchemeRepository(ABC):
    """Persistence contract for government welfare schemes and chunked RAG documents."""

    @abstractmethod
    def list_schemes(self) -> list[SchemeDefinition]:
        """Return all seeded government schemes."""

    @abstractmethod
    def get_scheme(self, scheme_id: str) -> SchemeDefinition | None:
        """Return a single SchemeDefinition by its canonical ID."""

    @abstractmethod
    def upsert_scheme(self, scheme: SchemeDefinition) -> SchemeDefinition:
        """Insert or update a scheme definition and refresh its searchable chunks."""


class IEvaluationRepository(ABC):
    """Persistence contract for storing 10-profile benchmark evaluation runs."""

    @abstractmethod
    def save_evaluation(self, summary: EvaluationSummary) -> EvaluationSummary:
        """Persist an evaluation run summary and its per-profile precision/recall breakdown."""

    @abstractmethod
    def list_evaluations(self, limit: int = 10) -> list[EvaluationSummary]:
        """Return historical evaluation benchmark runs ordered newest-first."""

