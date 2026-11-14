"""
Profile Memory Service Layer implementing Write-Through Redis Caching + Database Persistence.
Provides fast sub-millisecond reads during sequential agent orchestration while ensuring
every citizen profile and agent audit record is durably persisted in PostgreSQL.
"""

from shared.domain.models import (
    AgentMemoryAuditEntry,
    CitizenProfile,
    EvaluationSummary,
    UserProfileMemory,
    utc_now_iso,
)
from shared.interfaces.cache_interface import ICacheStore
from shared.interfaces.repository_interface import (
    IEvaluationRepository,
    IProfileMemoryRepository,
)


class ProfileMemoryService:
    """Coordinating service managing shared UserProfileMemory across Redis & Database."""

    CACHE_PREFIX = "scheme_guide:v1:profile_mem:"

    def __init__(
        self,
        repository: IProfileMemoryRepository,
        eval_repository: IEvaluationRepository,
        cache_store: ICacheStore,
        *,
        profile_ttl_seconds: int = 86400,
    ) -> None:
        self._repo = repository
        self._eval_repo = eval_repository
        self._cache = cache_store
        self._ttl = profile_ttl_seconds

    def _cache_key(self, session_id: str) -> str:
        """Build namespaced Redis key for session working memory."""
        return f"{self.CACHE_PREFIX}{session_id}"

    def get_or_create_memory(self, session_id: str, citizen_id: str = "anonymous") -> UserProfileMemory:
        """
        Read-through lookup: checks Redis hot cache first, then Database,
        or initializes a fresh UserProfileMemory if session is brand new.
        """
        cached = self._cache.get_json(self._cache_key(session_id))
        if cached is not None:
            return UserProfileMemory.model_validate(cached)

        stored = self._repo.get_memory(session_id)
        if stored is not None:
            self._cache.set_json(self._cache_key(session_id), stored.model_dump(), ttl_seconds=self._ttl)
            return stored

        fresh = UserProfileMemory(
            session_id=session_id,
            citizen_id=citizen_id,
            profile=CitizenProfile(),
        )
        return self.save_memory(fresh)

    def get_memory(self, session_id: str) -> UserProfileMemory | None:
        """Fetch existing session memory from Redis or Database without creating a blank record."""
        cached = self._cache.get_json(self._cache_key(session_id))
        if cached is not None:
            return UserProfileMemory.model_validate(cached)

        stored = self._repo.get_memory(session_id)
        if stored is not None:
            self._cache.set_json(self._cache_key(session_id), stored.model_dump(), ttl_seconds=self._ttl)
        return stored

    def save_memory(self, memory: UserProfileMemory) -> UserProfileMemory:
        """Write-through persistence: updates Database first, then refreshes Redis hot cache."""
        memory.updated_at = utc_now_iso()
        saved = self._repo.upsert_memory(memory)
        self._cache.set_json(self._cache_key(memory.session_id), saved.model_dump(), ttl_seconds=self._ttl)
        return saved

    def record_agent_access(self, session_id: str, entry: AgentMemoryAuditEntry) -> UserProfileMemory:
        """Record an agent read/write event and refresh both DB and Redis cache."""
        mem = self.get_or_create_memory(session_id)
        mem.audit_log.append(entry)
        return self.save_memory(mem)

    def list_sessions(self, limit: int = 20) -> list[UserProfileMemory]:
        """Return recent citizen profile sessions from database."""
        return self._repo.list_sessions(limit=limit)

    def save_evaluation_run(self, summary: EvaluationSummary) -> EvaluationSummary:
        """Persist 10-profile evaluation summary in database."""
        return self._eval_repo.save_evaluation(summary)

    def list_evaluation_runs(self, limit: int = 10) -> list[EvaluationSummary]:
        """List stored 10-profile evaluation runs."""
        return self._eval_repo.list_evaluations(limit=limit)

