"""
RAG Retrieval Microservice Client Adapter (Adapter + Dependency Inversion Pattern).
Abstracts scheme document retrieval & catalog access across HTTP microservice
boundaries or local in-process testing adapters.
"""

from abc import ABC, abstractmethod

from shared.domain.exceptions import MicroserviceUnavailableError
from shared.domain.models import RAGQueryRequest, RAGQueryResponse, SchemeDefinition
from shared.infrastructure.http_client import LoopAwareAsyncHttpPool
from services.rag_retrieval_service.repository import SqlSchemeRepository
from services.rag_retrieval_service.retriever import HybridSchemeRetriever


class IRAGRetrievalClient(ABC):
    """Abstract contract used by SchemeRetrievalAgent and EligibilityRuleAgent."""

    @abstractmethod
    async def retrieve(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """Query the RAG vector + BM25 knowledge base for candidate schemes."""

    @abstractmethod
    async def get_scheme(self, scheme_id: str) -> SchemeDefinition | None:
        """Fetch canonical scheme details (including rules, documents, steps) by ID."""

    @abstractmethod
    async def list_schemes(self) -> list[SchemeDefinition]:
        """List all schemes currently registered in the knowledge base."""


class HttpRAGRetrievalClient(IRAGRetrievalClient):
    """Async HTTP client talking to the rag-retrieval-service container (Port 8002)."""

    def __init__(self, base_url: str, timeout_seconds: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._pool = LoopAwareAsyncHttpPool(timeout_seconds=timeout_seconds)

    async def retrieve(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """Invoke POST /retrieve on rag-retrieval-service."""
        try:
            client = self._pool.get_client()
            resp = await client.post(
                f"{self._base_url}/retrieve",
                json=request.model_dump(),
            )
            resp.raise_for_status()
            return RAGQueryResponse.model_validate(resp.json())
        except Exception as exc:
            raise MicroserviceUnavailableError("rag-retrieval-service", str(exc)) from exc

    async def get_scheme(self, scheme_id: str) -> SchemeDefinition | None:
        """Invoke GET /schemes/{scheme_id} on rag-retrieval-service."""
        try:
            client = self._pool.get_client()
            resp = await client.get(f"{self._base_url}/schemes/{scheme_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return SchemeDefinition.model_validate(resp.json())
        except Exception as exc:
            raise MicroserviceUnavailableError("rag-retrieval-service", str(exc)) from exc

    async def list_schemes(self) -> list[SchemeDefinition]:
        """Invoke GET /schemes on rag-retrieval-service."""
        try:
            client = self._pool.get_client()
            resp = await client.get(f"{self._base_url}/schemes")
            resp.raise_for_status()
            return [SchemeDefinition.model_validate(s) for s in resp.json()]
        except Exception as exc:
            raise MicroserviceUnavailableError("rag-retrieval-service", str(exc)) from exc


class LocalRAGRetrievalClient(IRAGRetrievalClient):
    """In-process adapter directly calling HybridSchemeRetriever and SqlSchemeRepository."""

    def __init__(self, retriever: HybridSchemeRetriever, repo: SqlSchemeRepository) -> None:
        self._retriever = retriever
        self._repo = repo

    async def retrieve(self, request: RAGQueryRequest) -> RAGQueryResponse:
        return self._retriever.retrieve_with_cache(
            query_text=request.query_text,
            language=request.language,
            profile=request.profile,
            top_k=request.top_k,
            bypass_cache=request.bypass_cache,
        )

    async def get_scheme(self, scheme_id: str) -> SchemeDefinition | None:
        return self._repo.get_scheme(scheme_id)

    async def list_schemes(self) -> list[SchemeDefinition]:
        return self._repo.list_schemes()

