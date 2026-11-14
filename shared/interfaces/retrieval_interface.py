"""
Retrieval & Embedding Interface Contracts (Strategy Pattern + DIP).
Allows swapping TF-IDF/Char-Ngram, SentenceTransformers, or external vector stores
without changing SchemeRetrievalAgent or rag-retrieval-service handlers.
"""

from abc import ABC, abstractmethod

from shared.domain.models import CitizenProfile, RetrievedSchemeChunk, SchemeDefinition
from shared.domain.enums import LanguageCode


class IEmbeddingProvider(ABC):
    """Abstract text-to-vector embedding strategy."""

    @abstractmethod
    def fit(self, corpus_texts: list[str]) -> None:
        """Fit or initialize embedding vocabulary/projection over scheme corpus."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Transform input text into a normalized dense float vector."""


class IVectorRetriever(ABC):
    """Abstract hybrid RAG retriever operating over scheme knowledge chunks."""

    @abstractmethod
    def index_schemes(self, schemes: list[SchemeDefinition]) -> int:
        """Chunk, embed, and index all scheme documents; returns total chunk count."""

    @abstractmethod
    def retrieve(
        self,
        *,
        query_text: str,
        language: LanguageCode,
        profile: CitizenProfile | None,
        top_k: int,
    ) -> tuple[list[RetrievedSchemeChunk], str]:
        """
        Execute hybrid retrieval over scheme chunks using expanded profile query.
        Returns (ranked_chunks, expanded_query_string).
        """

