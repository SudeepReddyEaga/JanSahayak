"""
FastAPI Microservice Entrypoint for Agent Orchestrator Service (Port 8003).
Hosts the Microsoft Agent Framework SequentialBuilder pipeline, SSE streaming
endpoint, and 10-profile evaluation benchmark runner.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from shared.config.settings import AppSettings, get_settings
from shared.data.seed_loader import seed_database_if_empty
from shared.domain.models import (
    ApplicationGuideRequest,
    ApplicationGuideResponse,
    EvaluationSummary,
)
from shared.infrastructure.database import get_db_manager
from shared.infrastructure.logging_utils import get_logger
from shared.infrastructure.redis_cache import (
    CacheStoreFactory,
    SemanticQueryCacheService,
)
from services.agent_orchestrator_service.clients.maf_chat_client import ChatClientFactory
from services.agent_orchestrator_service.clients.profile_client import (
    HttpProfileMemoryClient,
    IProfileMemoryClient,
    LocalProfileMemoryClient,
)
from services.agent_orchestrator_service.clients.rag_client import (
    HttpRAGRetrievalClient,
    IRAGRetrievalClient,
    LocalRAGRetrievalClient,
)
from services.agent_orchestrator_service.evaluation.evaluator import BenchmarkEvaluator
from services.agent_orchestrator_service.pipeline.sequential_pipeline import (
    SequentialSchemePipeline,
)
from services.profile_memory_service.repository import (
    SqlEvaluationRepository,
    SqlProfileMemoryRepository,
)
from services.profile_memory_service.service import ProfileMemoryService
from services.rag_retrieval_service.embeddings import HybridTextEmbedder
from services.rag_retrieval_service.repository import SqlSchemeRepository
from services.rag_retrieval_service.retriever import HybridSchemeRetriever

logger = get_logger("agent-orchestrator-service")


def create_orchestrator_components(
    settings: AppSettings | None = None,
    *,
    force_local_inproc: bool = False,
) -> tuple[SequentialSchemePipeline, BenchmarkEvaluator, IProfileMemoryClient]:
    """
    Factory assembling Microsoft Agent Framework SequentialPipeline + BenchmarkEvaluator.
    Supports both distributed microservice HTTP communication and local in-process execution.
    """
    cfg = settings or get_settings()
    cache_store = CacheStoreFactory.get_store(cfg.redis_url)
    semantic_cache = SemanticQueryCacheService(
        cache_store,
        similarity_threshold=cfg.semantic_cache_threshold,
        exact_ttl_seconds=cfg.redis_exact_ttl_seconds,
        semantic_ttl_seconds=cfg.redis_semantic_ttl_seconds,
    )
    chat_client = ChatClientFactory.create_client(cfg)

    use_local = force_local_inproc or cfg.orchestration_mode == "local_inproc"
    if use_local:
        db_manager = get_db_manager(cfg.database_url)
        seed_database_if_empty(db_manager)
        profile_svc = ProfileMemoryService(
            repository=SqlProfileMemoryRepository(db_manager),
            eval_repository=SqlEvaluationRepository(db_manager),
            cache_store=cache_store,
            profile_ttl_seconds=cfg.redis_profile_ttl_seconds,
        )
        scheme_repo = SqlSchemeRepository(db_manager)
        retriever = HybridSchemeRetriever(
            scheme_repo=scheme_repo,
            embedder=HybridTextEmbedder(),
            cache_store=cache_store,
            rag_ttl_seconds=cfg.redis_rag_ttl_seconds,
        )
        memory_client: IProfileMemoryClient = LocalProfileMemoryClient(profile_svc)
        rag_client: IRAGRetrievalClient = LocalRAGRetrievalClient(retriever, scheme_repo)
    else:
        memory_client = HttpProfileMemoryClient(cfg.profile_memory_service_url)
        rag_client = HttpRAGRetrievalClient(cfg.rag_retrieval_service_url)

    pipeline = SequentialSchemePipeline(
        settings=cfg,
        chat_client=chat_client,
        memory_client=memory_client,
        rag_client=rag_client,
        semantic_cache=semantic_cache,
    )
    evaluator = BenchmarkEvaluator(pipeline=pipeline, memory_client=memory_client)
    return pipeline, evaluator, memory_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize orchestrator pipeline, pre-warm cache from DB, and ready evaluator at FastAPI startup."""
    cfg = get_settings()
    pipeline, evaluator, memory_client = create_orchestrator_components(cfg)
    app.state.pipeline = pipeline
    app.state.evaluator = evaluator
    app.state.memory_client = memory_client
    try:
        from shared.infrastructure.database import get_db_manager
        db_mgr = get_db_manager(cfg.database_url)
        if pipeline._semantic_cache:
            warmed = pipeline._semantic_cache.prewarm_cache_from_db(db_mgr)
            logger.info(f"Agent Orchestrator pre-warmed {warmed} database entries into Redis cache.")
    except Exception as exc:
        logger.warning(f"Orchestrator cache pre-warming skipped: {exc}")
    logger.info("Agent Orchestrator Service initialized with Microsoft Agent Framework SequentialBuilder.")
    yield


app = FastAPI(
    title="Agent Orchestrator Microservice",
    description="Microsoft Agent Framework Sequential Multi-Agent Pipeline for Citizen Welfare Eligibility.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe confirming orchestrator readiness."""
    return {
        "status": "healthy",
        "service": "agent-orchestrator-service",
        "framework": "Microsoft Agent Framework (SequentialBuilder)",
    }


@app.post("/orchestrate", response_model=ApplicationGuideResponse)
async def orchestrate(request: ApplicationGuideRequest) -> ApplicationGuideResponse:
    """Execute the 6-agent sequential pipeline (with GroundingGate & Redis Cache)."""
    pipeline: SequentialSchemePipeline = app.state.pipeline
    return await pipeline.run(request)


@app.post("/orchestrate/stream")
async def orchestrate_stream(request: ApplicationGuideRequest) -> StreamingResponse:
    """Stream real-time per-agent step progress and final guide payload over SSE."""
    pipeline: SequentialSchemePipeline = app.state.pipeline
    return StreamingResponse(
        pipeline.run_stream(request),
        media_type="text/event-stream",
    )


@app.post("/evaluate", response_model=EvaluationSummary)
async def run_benchmark_evaluation() -> EvaluationSummary:
    """Execute all 10 ground-truth citizen profiles and report Precision, Recall & F1."""
    evaluator: BenchmarkEvaluator = app.state.evaluator
    return await evaluator.run_evaluation(persist=True)


@app.get("/evaluation-history", response_model=list[EvaluationSummary])
async def evaluation_history(limit: int = 10) -> list[EvaluationSummary]:
    """Fetch previously stored 10-profile benchmark evaluation runs."""
    client: IProfileMemoryClient = app.state.memory_client
    return await client.list_evaluations(limit=limit)

