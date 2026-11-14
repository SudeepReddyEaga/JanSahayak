"""
FastAPI Microservice Entrypoint for RAG Retrieval Service (Port 8002).
Seeds the Scheme Knowledge Base on startup, exposes scheme CRUD/browsing endpoints,
and executes cached Hybrid BM25 + Vector RAG retrieval for SchemeRetrievalAgent.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from shared.config.settings import get_settings
from shared.data.seed_loader import seed_database_if_empty
from shared.domain.models import RAGQueryRequest, RAGQueryResponse, SchemeDefinition
from shared.infrastructure.database import get_db_manager
from shared.infrastructure.logging_utils import get_logger
from shared.infrastructure.redis_cache import CacheStoreFactory
from services.rag_retrieval_service.embeddings import HybridTextEmbedder
from services.rag_retrieval_service.repository import SqlSchemeRepository
from services.rag_retrieval_service.retriever import HybridSchemeRetriever

logger = get_logger("rag-retrieval-service")


def create_rag_components() -> tuple[SqlSchemeRepository, HybridSchemeRetriever]:
    """Construct repository, embedder, Redis cache, and hybrid retriever via DI."""
    settings = get_settings()
    db_manager = get_db_manager(settings.database_url)
    # Seed 17 canonical government schemes & vector chunks idempotently
    seed_database_if_empty(db_manager)
    repo = SqlSchemeRepository(db_manager)
    embedder = HybridTextEmbedder()
    cache_store = CacheStoreFactory.get_store(settings.redis_url)
    retriever = HybridSchemeRetriever(
        scheme_repo=repo,
        embedder=embedder,
        cache_store=cache_store,
        rag_ttl_seconds=settings.redis_rag_ttl_seconds,
    )
    return repo, retriever


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scheme knowledge base and hybrid RAG vector index on startup."""
    repo, retriever = create_rag_components()
    app.state.scheme_repo = repo
    app.state.retriever = retriever
    logger.info("RAG Retrieval Service initialized and scheme vector index built.")
    yield


app = FastAPI(
    title="RAG Retrieval Microservice",
    description="Scheme Knowledge Base & Hybrid BM25 + Vector Retrieval Service backed by PostgreSQL & Redis.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str | int]:
    """Liveness probe returning indexed scheme count."""
    repo: SqlSchemeRepository = app.state.scheme_repo
    return {
        "status": "healthy",
        "service": "rag-retrieval-service",
        "schemes_indexed": len(repo.list_schemes()),
    }


@app.get("/schemes", response_model=list[SchemeDefinition])
def list_schemes() -> list[SchemeDefinition]:
    """Return all government welfare schemes stored in the knowledge base."""
    repo: SqlSchemeRepository = app.state.scheme_repo
    return repo.list_schemes()


@app.get("/schemes/{scheme_id}", response_model=SchemeDefinition)
def get_scheme(scheme_id: str) -> SchemeDefinition:
    """Return complete specification for a single scheme by ID."""
    repo: SqlSchemeRepository = app.state.scheme_repo
    scheme = repo.get_scheme(scheme_id)
    if scheme is None:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")
    return scheme


@app.post("/retrieve", response_model=RAGQueryResponse)
def retrieve_schemes(request: RAGQueryRequest) -> RAGQueryResponse:
    """Execute hybrid BM25 + dense vector RAG retrieval over indexed scheme documents."""
    retriever: HybridSchemeRetriever = app.state.retriever
    return retriever.retrieve_with_cache(
        query_text=request.query_text,
        language=request.language,
        profile=request.profile,
        top_k=request.top_k,
        bypass_cache=request.bypass_cache,
    )


@app.post("/ingest", response_model=SchemeDefinition)
def ingest_scheme(scheme: SchemeDefinition) -> SchemeDefinition:
    """Upsert a new or updated scheme document and refresh the RAG index."""
    repo: SqlSchemeRepository = app.state.scheme_repo
    retriever: HybridSchemeRetriever = app.state.retriever
    saved = repo.upsert_scheme(scheme)
    retriever.refresh_index()
    return saved

