"""
Pytest Fixtures for Isolated Multi-Agent, RAG, Redis Cache, and API Gateway Tests.
Uses temporary per-test SQLite databases and InMemoryCacheStore so tests run cleanly
with zero dependency on external daemons while exercising identical production code paths.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from shared.config.settings import AppSettings
from shared.data.seed_loader import seed_database_if_empty
from shared.infrastructure.database import DatabaseManager
from shared.infrastructure.redis_cache import (
    InMemoryCacheStore,
    SemanticQueryCacheService,
)
from services.agent_orchestrator_service.clients.maf_chat_client import ChatClientFactory
from services.agent_orchestrator_service.clients.profile_client import LocalProfileMemoryClient
from services.agent_orchestrator_service.clients.rag_client import LocalRAGRetrievalClient
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


@pytest.fixture()
def test_settings(tmp_path: Path) -> AppSettings:
    """Provide isolated AppSettings pointing to a temporary SQLite DB and local_inproc mode."""
    db_file = tmp_path / "test_scheme_guide.db"
    return AppSettings(
        orchestration_mode="local_inproc",
        database_url=f"sqlite:///{db_file.as_posix()}",
        redis_url="redis://127.0.0.1:6399/9",
        llm_provider="deterministic",
        semantic_cache_threshold=0.78,
        rag_top_k=12,
    )


@pytest.fixture()
def test_db(test_settings: AppSettings) -> DatabaseManager:
    """Create schema and seed all 17 welfare schemes into temporary DB."""
    db = DatabaseManager(test_settings.database_url)
    seed_database_if_empty(db, force_refresh=True)
    return db


@pytest.fixture()
def test_cache() -> InMemoryCacheStore:
    """Provide clean per-test cache store implementing ICacheStore."""
    return InMemoryCacheStore()


@pytest.fixture()
def pipeline_bundle(test_settings: AppSettings, test_db: DatabaseManager, test_cache: InMemoryCacheStore):
    """Build complete wired pipeline, memory service, RAG retriever, and benchmark evaluator."""
    profile_repo = SqlProfileMemoryRepository(test_db)
    eval_repo = SqlEvaluationRepository(test_db)
    profile_svc = ProfileMemoryService(profile_repo, eval_repo, test_cache)
    scheme_repo = SqlSchemeRepository(test_db)
    retriever = HybridSchemeRetriever(scheme_repo, HybridTextEmbedder(), test_cache)

    memory_client = LocalProfileMemoryClient(profile_svc)
    rag_client = LocalRAGRetrievalClient(retriever, scheme_repo)
    semantic_cache = SemanticQueryCacheService(
        test_cache,
        similarity_threshold=test_settings.semantic_cache_threshold,
    )
    chat_client = ChatClientFactory.create_client(test_settings)

    pipeline = SequentialSchemePipeline(
        settings=test_settings,
        chat_client=chat_client,
        memory_client=memory_client,
        rag_client=rag_client,
        semantic_cache=semantic_cache,
    )
    evaluator = BenchmarkEvaluator(pipeline=pipeline, memory_client=memory_client)
    return {
        "pipeline": pipeline,
        "evaluator": evaluator,
        "memory_client": memory_client,
        "profile_svc": profile_svc,
        "retriever": retriever,
        "scheme_repo": scheme_repo,
        "semantic_cache": semantic_cache,
        "cache_store": test_cache,
    }


@pytest.fixture()
def api_client(test_settings: AppSettings, monkeypatch: pytest.MonkeyPatch):
    """Provide FastAPI TestClient wired to the API Gateway in local_inproc mode."""
    from services.api_gateway import main as gw_main

    monkeypatch.setenv("ORCHESTRATION_MODE", "local_inproc")
    monkeypatch.setenv("DATABASE_URL", test_settings.database_url)
    monkeypatch.setenv("SEMANTIC_CACHE_THRESHOLD", str(test_settings.semantic_cache_threshold))
    monkeypatch.setenv("RAG_TOP_K", str(test_settings.rag_top_k))

    from shared.config.settings import get_settings

    get_settings.cache_clear()
    with TestClient(gw_main.app) as client:
        yield client
    get_settings.cache_clear()

