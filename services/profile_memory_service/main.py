"""
FastAPI Microservice Entrypoint for Profile Memory Service (Port 8001).
Manages shared citizen profile memory, per-agent audit trails, and evaluation storage.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from shared.config.settings import get_settings
from shared.domain.models import (
    AgentMemoryAuditEntry,
    EvaluationSummary,
    UserProfileMemory,
)
from shared.infrastructure.database import get_db_manager
from shared.infrastructure.logging_utils import get_logger
from shared.infrastructure.redis_cache import CacheStoreFactory
from services.profile_memory_service.repository import (
    SqlEvaluationRepository,
    SqlProfileMemoryRepository,
)
from services.profile_memory_service.service import ProfileMemoryService

logger = get_logger("profile-memory-service")


def create_profile_memory_service() -> ProfileMemoryService:
    """Dependency-injection factory wiring concrete repository and Redis cache implementations."""
    settings = get_settings()
    db_manager = get_db_manager(settings.database_url)
    cache_store = CacheStoreFactory.get_store(settings.redis_url)
    return ProfileMemoryService(
        repository=SqlProfileMemoryRepository(db_manager),
        eval_repository=SqlEvaluationRepository(db_manager),
        cache_store=cache_store,
        profile_ttl_seconds=settings.redis_profile_ttl_seconds,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB tables and service dependencies cleanly at startup."""
    app.state.memory_service = create_profile_memory_service()
    logger.info("Profile Memory Service started and database tables verified.")
    yield


app = FastAPI(
    title="Profile Memory Microservice",
    description="Shared User-Profile Memory & Agent Audit Log Service backed by PostgreSQL & Redis.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Container liveness and readiness probe."""
    return {"status": "healthy", "service": "profile-memory-service"}


@app.get("/profiles/{session_id}", response_model=UserProfileMemory)
def get_profile_memory(session_id: str, create_if_missing: bool = True) -> UserProfileMemory:
    """Retrieve shared UserProfileMemory for a session (or initialize one if requested)."""
    svc: ProfileMemoryService = app.state.memory_service
    if create_if_missing:
        return svc.get_or_create_memory(session_id)
    mem = svc.get_memory(session_id)
    if mem is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return mem


@app.put("/profiles/{session_id}", response_model=UserProfileMemory)
def put_profile_memory(session_id: str, payload: UserProfileMemory) -> UserProfileMemory:
    """Persist updated shared UserProfileMemory from an agent step."""
    payload.session_id = session_id
    svc: ProfileMemoryService = app.state.memory_service
    return svc.save_memory(payload)


@app.post("/profiles/{session_id}/audit", response_model=UserProfileMemory)
def append_audit_entry(session_id: str, entry: AgentMemoryAuditEntry) -> UserProfileMemory:
    """Record a fine-grained agent read/write audit entry on shared memory."""
    svc: ProfileMemoryService = app.state.memory_service
    return svc.record_agent_access(session_id, entry)


@app.get("/sessions", response_model=list[UserProfileMemory])
def list_sessions(limit: int = 20) -> list[UserProfileMemory]:
    """Return recent citizen profile memory sessions for UI inspection."""
    svc: ProfileMemoryService = app.state.memory_service
    return svc.list_sessions(limit=limit)


@app.post("/evaluations", response_model=EvaluationSummary)
def save_evaluation(summary: EvaluationSummary) -> EvaluationSummary:
    """Store a completed 10-profile evaluation run summary."""
    svc: ProfileMemoryService = app.state.memory_service
    return svc.save_evaluation_run(summary)


@app.get("/evaluations", response_model=list[EvaluationSummary])
def list_evaluations(limit: int = 10) -> list[EvaluationSummary]:
    """Fetch recent evaluation benchmark summaries."""
    svc: ProfileMemoryService = app.state.memory_service
    return svc.list_evaluation_runs(limit=limit)

