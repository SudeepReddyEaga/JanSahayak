"""
FastAPI Public API Gateway (Port 8000).
Unified entry point for the Interactive UI and REST callers:
  - Routes citizen queries to Agent Orchestrator Service (or in-process MAF pipeline)
  - Records Redis cache telemetry (exact hit, semantic hit, miss) into PostgreSQL
  - Proxies profile memory, scheme knowledge base, and 10-profile evaluation endpoints
  - Exposes Redis cache inspection and invalidation endpoints
  - Serves the interactive SPA UI fallback at `/` for single-port portability
"""

from contextlib import asynccontextmanager
import hashlib
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx
from sqlalchemy import desc, select

from shared.config.settings import AppSettings, get_settings
from shared.domain.models import (
    ApplicationGuideRequest,
    ApplicationGuideResponse,
    EvaluationSummary,
    PreparedSpeechPayload,
    PrepareSpeechRequest,
    SchemeDefinition,
    UserProfileMemory,
    VoiceLocaleSpec,
)
from shared.infrastructure.database import DatabaseManager, QueryCacheAuditORM, get_db_manager
from shared.infrastructure.logging_utils import get_logger
from shared.infrastructure.redis_cache import (
    CacheStoreFactory,
    SemanticQueryCacheService,
)
from services.agent_orchestrator_service.evaluation.evaluator import BenchmarkEvaluator
from services.agent_orchestrator_service.main import create_orchestrator_components
from services.voice_speech_service.service import (
    SpeechTextSanitizerService,
    VoiceLocaleRegistryService,
)

logger = get_logger("api-gateway")

STATIC_UI_DIR = Path(__file__).resolve().parent.parent / "frontend_ui" / "static"


class GatewayServiceFacade:
    """
    Facade Pattern unifying downstream HTTP microservice calls (microservice_http mode)
    and local in-process microservice calls (local_inproc mode) behind a clean API.
    """

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.db_manager: DatabaseManager = get_db_manager(settings.database_url)
        self.cache_store = CacheStoreFactory.get_store(settings.redis_url)
        self.semantic_cache = SemanticQueryCacheService(
            self.cache_store,
            similarity_threshold=settings.semantic_cache_threshold,
            exact_ttl_seconds=settings.redis_exact_ttl_seconds,
            semantic_ttl_seconds=settings.redis_semantic_ttl_seconds,
        )
        self.is_local = settings.orchestration_mode == "local_inproc"
        # Initialize stateless voice adapters for local_inproc mode and resilient fallback
        self.voice_registry = VoiceLocaleRegistryService()
        self.speech_sanitizer = SpeechTextSanitizerService(self.voice_registry)
        if self.is_local:
            # Initialize local in-process pipeline, evaluator, and service adapters
            from services.profile_memory_service.main import create_profile_memory_service
            from services.rag_retrieval_service.main import create_rag_components

            self.pipeline, self.evaluator, _ = create_orchestrator_components(
                settings, force_local_inproc=True
            )
            self.memory_svc = create_profile_memory_service()
            self.scheme_repo, _ = create_rag_components()

    def record_cache_audit(self, query: str, response: ApplicationGuideResponse) -> None:
        """Persist Redis cache telemetry (hit/miss, similarity, latency) to PostgreSQL."""
        q_hash = hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()[:24]
        try:
            with self.db_manager.session_scope() as session:
                session.add(
                    QueryCacheAuditORM(
                        query_hash=q_hash,
                        language=response.detected_language.value,
                        cache_status=response.cache_status.value,
                        similarity_score=response.cache_similarity,
                        latency_ms=response.total_latency_ms,
                    )
                )
        except Exception as exc:
            logger.warning(f"Failed to record cache audit telemetry: {exc}")

    async def handle_guide(self, req: ApplicationGuideRequest) -> ApplicationGuideResponse:
        """Route citizen eligibility query to Agent Orchestrator (or local pipeline) and log telemetry."""
        if self.is_local:
            resp = await self.pipeline.run(req)
        else:
            async with httpx.AsyncClient(timeout=45.0) as client:
                r = await client.post(
                    f"{self.settings.agent_orchestrator_service_url}/orchestrate",
                    json=req.model_dump(),
                )
                r.raise_for_status()
                resp = ApplicationGuideResponse.model_validate(r.json())
        self.record_cache_audit(req.query, resp)
        return resp

    async def stream_guide(self, req: ApplicationGuideRequest):
        """Stream SSE agent execution events from Agent Orchestrator to browser UI."""
        if self.is_local:
            async for chunk in self.pipeline.run_stream(req):
                yield chunk
            return

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.settings.agent_orchestrator_service_url}/orchestrate/stream",
                json=req.model_dump(),
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_text():
                    yield line

    async def get_profile(self, session_id: str) -> UserProfileMemory:
        """Retrieve shared UserProfileMemory for a session."""
        if self.is_local:
            mem = self.memory_svc.get_memory(session_id)
            if mem is None:
                raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
            return mem
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self.settings.profile_memory_service_url}/profiles/{session_id}",
                params={"create_if_missing": False},
            )
            if r.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
            r.raise_for_status()
            return UserProfileMemory.model_validate(r.json())

    async def list_sessions(self, limit: int = 20) -> list[UserProfileMemory]:
        """List recent citizen sessions stored in PostgreSQL."""
        if self.is_local:
            return self.memory_svc.list_sessions(limit=limit)
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self.settings.profile_memory_service_url}/sessions",
                params={"limit": limit},
            )
            r.raise_for_status()
            return [UserProfileMemory.model_validate(x) for x in r.json()]

    async def list_schemes(self) -> list[SchemeDefinition]:
        """Fetch all seeded government schemes from RAG Retrieval Service."""
        if self.is_local:
            return self.scheme_repo.list_schemes()
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.settings.rag_retrieval_service_url}/schemes")
            r.raise_for_status()
            return [SchemeDefinition.model_validate(x) for x in r.json()]

    async def run_evaluation(self) -> EvaluationSummary:
        """Trigger 10-profile Precision/Recall benchmark run."""
        if self.is_local:
            return await self.evaluator.run_evaluation(persist=True)
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self.settings.agent_orchestrator_service_url}/evaluate")
            r.raise_for_status()
            return EvaluationSummary.model_validate(r.json())

    async def evaluation_history(self, limit: int = 10) -> list[EvaluationSummary]:
        """Fetch historical benchmark evaluation runs."""
        if self.is_local:
            return self.memory_svc.list_evaluation_runs(limit=limit)
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self.settings.agent_orchestrator_service_url}/evaluation-history",
                params={"limit": limit},
            )
            r.raise_for_status()
            return [EvaluationSummary.model_validate(x) for x in r.json()]

    async def list_voice_locales(self) -> list[VoiceLocaleSpec]:
        """Fetch all 12 citizen voice BCP-47 locale specs from Voice & Speech Service."""
        if self.is_local:
            return self.voice_registry.list_locales()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.settings.voice_speech_service_url}/voice/locales")
                r.raise_for_status()
                return [VoiceLocaleSpec.model_validate(x) for x in r.json()]
        except Exception as exc:
            logger.warning(f"Voice service unavailable ({exc}); serving safe local voice locales fallback.")
            return self.voice_registry.list_locales()

    async def prepare_speech(self, req: PrepareSpeechRequest) -> PreparedSpeechPayload:
        """Prepare sanitized spoken segments via Voice & Speech Service with safe fallback."""
        if self.is_local:
            return self.speech_sanitizer.prepare_speech(text=req.text, language=req.language)
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                r = await client.post(
                    f"{self.settings.voice_speech_service_url}/voice/prepare-speech",
                    json=req.model_dump(),
                )
                r.raise_for_status()
                return PreparedSpeechPayload.model_validate(r.json())
        except Exception as exc:
            logger.warning(f"Voice service speech prepare failed ({exc}); using local sanitizer fallback.")
            return self.speech_sanitizer.prepare_speech(text=req.text, language=req.language)

    def get_cache_stats(self) -> dict[str, Any]:
        """Combine live Redis cache metrics with recent DB query latency audit records."""
        stats = self.cache_store.stats()
        recent_audits: list[dict[str, Any]] = []
        try:
            with self.db_manager.session_scope() as session:
                rows = session.scalars(
                    select(QueryCacheAuditORM).order_by(desc(QueryCacheAuditORM.id)).limit(15)
                ).all()
                recent_audits = [
                    {
                        "query_hash": r.query_hash,
                        "language": r.language,
                        "cache_status": r.cache_status,
                        "similarity_score": r.similarity_score,
                        "latency_ms": r.latency_ms,
                    }
                    for r in rows
                ]
        except Exception:
            pass
        stats["recent_query_audits"] = recent_audits
        return stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Gateway facade, pre-warm Redis cache from DB, and verify connections at startup."""
    settings = get_settings()
    gateway = GatewayServiceFacade(settings)
    app.state.gateway = gateway
    try:
        # Pre-warm Redis cache with all DB schemes, policy chunks, and past citizen queries
        warmed = gateway.semantic_cache.prewarm_cache_from_db(gateway.db_manager)
        logger.info(
            f"API Gateway started (mode={settings.orchestration_mode}, pre-warmed={warmed} items into Redis)."
        )
    except Exception as exc:
        logger.warning(f"Cache pre-warming skipped on startup: {exc}")
    yield


app = FastAPI(
    title="Multilingual Government Scheme Eligibility Guide API Gateway",
    description="Multi-Agent Welfare Guide built on Microsoft Agent Framework, Microservices, Voice Support, PostgreSQL & Redis.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable permissive CORS for separate frontend container or local browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static interactive SPA assets if present
if STATIC_UI_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_UI_DIR)), name="static")


@app.get("/")
def serve_ui_root():
    """Serve the interactive SPA dashboard at root for zero-setup access."""
    index_file = STATIC_UI_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "API Gateway active. Access Swagger docs at /docs."}


@app.get("/health")
async def aggregated_health() -> dict[str, Any]:
    """Return aggregated health status across Gateway, Microservices, DB, and Redis."""
    gw: GatewayServiceFacade = app.state.gateway
    services_health: dict[str, str] = {"api_gateway": "healthy"}

    if gw.is_local:
        services_health["profile_memory_service"] = "healthy (in-proc)"
        services_health["rag_retrieval_service"] = "healthy (in-proc)"
        services_health["agent_orchestrator_service"] = "healthy (in-proc)"
        services_health["voice_speech_service"] = "healthy (in-proc)"
    else:
        targets = {
            "profile_memory_service": f"{gw.settings.profile_memory_service_url}/health",
            "rag_retrieval_service": f"{gw.settings.rag_retrieval_service_url}/health",
            "agent_orchestrator_service": f"{gw.settings.agent_orchestrator_service_url}/health",
            "voice_speech_service": f"{gw.settings.voice_speech_service_url}/health",
        }
        async with httpx.AsyncClient(timeout=2.5) as client:
            for name, url in targets.items():
                try:
                    r = await client.get(url)
                    services_health[name] = "healthy" if r.status_code == 200 else f"degraded ({r.status_code})"
                except Exception:
                    services_health[name] = "unreachable"

    return {
        "status": "healthy",
        "mode": gw.settings.orchestration_mode,
        "cache_backend": gw.cache_store.stats().get("backend"),
        "services": services_health,
    }


@app.post("/api/v1/guide", response_model=ApplicationGuideResponse)
async def create_eligibility_guide(request: ApplicationGuideRequest) -> ApplicationGuideResponse:
    """Process a citizen welfare eligibility query through the 6-agent sequential pipeline."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.handle_guide(request)


@app.post("/api/v1/guide/stream")
async def stream_eligibility_guide(request: ApplicationGuideRequest) -> StreamingResponse:
    """Stream step-by-step Microsoft Agent Framework agent events over SSE."""
    gw: GatewayServiceFacade = app.state.gateway
    return StreamingResponse(gw.stream_guide(request), media_type="text/event-stream")


@app.get("/api/v1/profiles/{session_id}", response_model=UserProfileMemory)
async def get_profile_memory(session_id: str) -> UserProfileMemory:
    """Inspect shared UserProfileMemory & per-agent audit trail for a citizen session."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.get_profile(session_id)


@app.get("/api/v1/sessions", response_model=list[UserProfileMemory])
async def list_recent_sessions(limit: int = 20) -> list[UserProfileMemory]:
    """List recent citizen profile sessions stored in PostgreSQL."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.list_sessions(limit=limit)


@app.get("/api/v1/schemes", response_model=list[SchemeDefinition])
async def list_schemes() -> list[SchemeDefinition]:
    """Retrieve all 17 seeded welfare scheme documents and deterministic rules."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.list_schemes()


@app.post("/api/v1/evaluate", response_model=EvaluationSummary)
async def evaluate_benchmark() -> EvaluationSummary:
    """Run the 10-profile benchmark evaluation and report Precision, Recall & F1."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.run_evaluation()


@app.get("/api/v1/evaluation-history", response_model=list[EvaluationSummary])
async def get_evaluation_history(limit: int = 10) -> list[EvaluationSummary]:
    """Fetch persisted 10-profile benchmark evaluation summaries."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.evaluation_history(limit=limit)


@app.get("/api/v1/benchmark-profiles")
def get_benchmark_profiles() -> list[dict]:
    """Return the 10 labeled ground-truth citizen profiles used for CO3/CO4 evaluation."""
    return BenchmarkEvaluator.load_profiles()


@app.get("/api/v1/cache/stats")
def get_cache_stats() -> dict[str, Any]:
    """Inspect Redis exact + semantic cache metrics and recent query latency telemetry."""
    gw: GatewayServiceFacade = app.state.gateway
    return gw.get_cache_stats()


@app.post("/api/v1/cache/flush")
def flush_cache() -> dict[str, int | str]:
    """Invalidate all cached guide and RAG entries inside Redis."""
    gw: GatewayServiceFacade = app.state.gateway
    removed = gw.cache_store.flush_prefix("scheme_guide:v1:")
    return {"status": "flushed", "keys_removed": removed}


@app.get("/api/v1/voice/locales", response_model=list[VoiceLocaleSpec])
async def get_voice_locales() -> list[VoiceLocaleSpec]:
    """Return speech recognition & synthesis BCP-47 locales for all 12 citizen languages."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.list_voice_locales()


@app.post("/api/v1/voice/prepare-speech", response_model=PreparedSpeechPayload)
async def prepare_speech_audio_payload(request: PrepareSpeechRequest) -> PreparedSpeechPayload:
    """Convert rich welfare guidance Markdown into browser-safe speech utterance chunks."""
    gw: GatewayServiceFacade = app.state.gateway
    return await gw.prepare_speech(request)

