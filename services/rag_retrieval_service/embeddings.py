"""
Embedding Provider implementations (Strategy Pattern).
HybridTextEmbedder produces deterministic dense vector representations for both
scheme documents and multilingual citizen queries without external downloads.
"""

from shared.infrastructure.redis_cache import _compute_trigram_vector
from shared.interfaces.retrieval_interface import IEmbeddingProvider


class HybridTextEmbedder(IEmbeddingProvider):
    """Zero-dependency multilingual trigram + token dense embedder."""

    def __init__(self, dims: int = 256) -> None:
        self._dims = dims

    def fit(self, corpus_texts: list[str]) -> None:
        """Deterministic hashing projection requires no stateful vocabulary training."""
        return None

    def embed(self, text: str) -> list[float]:
        """Compute normalized 256-dim dense vector for text."""
        return _compute_trigram_vector(text, dims=self._dims)

