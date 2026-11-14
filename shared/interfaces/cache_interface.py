"""
Cache Interface Contracts (Interface Segregation Principle).
Decouples services from concrete Redis or In-Memory backends, allowing
seamless switching between distributed Redis and unit-test in-memory stores.
"""

from abc import ABC, abstractmethod
from typing import Any

from shared.domain.models import ApplicationGuideResponse, CitizenProfile


class ICacheStore(ABC):
    """Abstract low-level key-value cache interface supporting TTL and namespace statistics."""

    @abstractmethod
    def get_json(self, key: str) -> dict[str, Any] | None:
        """Retrieve and deserialize a JSON object by key, or return None on miss."""

    @abstractmethod
    def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Serialize and store a JSON object under key with expiration TTL."""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a single cached key."""

    @abstractmethod
    def flush_prefix(self, prefix: str) -> int:
        """Invalidate all cached keys matching the given prefix and return deleted count."""

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Return diagnostic cache metrics (backend type, key counts, hit/miss counters)."""


class ISemanticQueryCache(ABC):
    """
    Abstract high-level cache contract supporting both exact normalized lookups
    and profile-guarded semantic similarity lookups for previously seen citizen queries.
    """

    @abstractmethod
    def lookup_guide(
        self,
        *,
        query: str,
        profile: CitizenProfile,
    ) -> tuple[ApplicationGuideResponse | None, str, float | None]:
        """
        Attempt exact match first, then semantic vector similarity match within the
        same language and canonical profile signature.
        Returns (cached_response_or_none, cache_status_value, similarity_score_or_none).
        """

    @abstractmethod
    def store_guide(
        self,
        *,
        query: str,
        profile: CitizenProfile,
        response: ApplicationGuideResponse,
    ) -> None:
        """Persist response in both exact and semantic Redis index buckets."""

