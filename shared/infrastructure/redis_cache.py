"""
Redis Distributed Cache & Profile-Guarded Semantic Query Cache.
Implements ICacheStore and ISemanticQueryCache following Liskov Substitution and
Cache-Aside LLD patterns for fast AND accurate retrieval of previously seen queries.
"""

import hashlib
import json
import math
import re
import threading
import time
from typing import Any

import redis

from shared.config.settings import get_settings
from shared.domain.enums import CacheStatus
from shared.domain.models import ApplicationGuideResponse, CitizenProfile
from shared.infrastructure.logging_utils import get_logger
from shared.interfaces.cache_interface import ICacheStore, ISemanticQueryCache

logger = get_logger("redis-cache")


def _compute_trigram_vector(text: str, dims: int = 256) -> list[float]:
    """
    Build a deterministic L2-normalized character 3-gram + word token feature vector.
    Requires zero external ML model downloads and works reliably across Latin and Indic scripts.
    """
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    if not normalized:
        return [0.0] * dims

    vec = [0.0] * dims
    # Add word unigrams with higher weight across Latin, Indic, and Urdu/Arabic scripts
    tokens = re.findall(r"[\w\u0600-\u06FF\u0900-\u0DFF]+", normalized)
    for tok in tokens:
        idx = int(hashlib.blake2b(f"w:{tok}".encode("utf-8"), digest_size=4).hexdigest(), 16) % dims
        vec[idx] += 2.0

    # Add character 3-grams for morphological / spelling / paraphrase tolerance
    padded = f" {normalized} "
    for i in range(max(0, len(padded) - 2)):
        gram = padded[i : i + 3]
        idx = int(hashlib.blake2b(f"g:{gram}".encode("utf-8"), digest_size=4).hexdigest(), 16) % dims
        vec[idx] += 1.0

    # L2-normalize so dot product equals exact cosine similarity
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0.0:
        return [v / norm for v in vec]
    return vec


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two equal-length L2-normalized vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))


class RedisCacheStore(ICacheStore):
    """Production ICacheStore implementation backed by Redis."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self._client = redis_client
        self._hits = 0
        self._misses = 0
        self._sets = 0

    def get_json(self, key: str) -> dict[str, Any] | None:
        """Fetch raw string from Redis and decode JSON payload."""
        try:
            raw = self._client.get(key)
            if raw is None:
                self._misses += 1
                return None
            self._hits += 1
            return json.loads(raw)
        except Exception as exc:
            logger.warning(f"Redis get_json failed for key={key}: {exc}")
            return None

    def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Encode payload as JSON and persist to Redis with TTL expiration."""
        try:
            payload = json.dumps(value, ensure_ascii=False)
            self._client.setex(key, ttl_seconds, payload)
            self._sets += 1
            return True
        except Exception as exc:
            logger.warning(f"Redis set_json failed for key={key}: {exc}")
            return False

    def delete(self, key: str) -> bool:
        """Remove a specific key from Redis."""
        try:
            return bool(self._client.delete(key))
        except Exception as exc:
            logger.warning(f"Redis delete failed for key={key}: {exc}")
            return False

    def flush_prefix(self, prefix: str) -> int:
        """Scan and remove all Redis keys starting with prefix."""
        try:
            keys = list(self._client.scan_iter(match=f"{prefix}*"))
            if not keys:
                return 0
            return int(self._client.delete(*keys))
        except Exception as exc:
            logger.warning(f"Redis flush_prefix failed for prefix={prefix}: {exc}")
            return 0

    def stats(self) -> dict[str, Any]:
        """Collect Redis key counts and cache hit/miss telemetry."""
        try:
            info = self._client.info(section="keyspace")
            keys_sample = [str(k) for k in list(self._client.scan_iter(match="scheme_guide:*", count=100))[:25]]
            total_keys = self._client.dbsize()
        except Exception:
            info = {}
            keys_sample = []
            total_keys = 0
        return {
            "backend": "redis",
            "connected": True,
            "total_keys": total_keys,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / max(1, self._hits + self._misses), 4),
            "sample_keys": keys_sample,
            "keyspace": info,
        }


class InMemoryCacheStore(ICacheStore):
    """
    Thread-safe TTL-aware fallback cache implementing ICacheStore identically to RedisCacheStore.
    Used automatically in isolated unit tests or if Redis daemon is offline locally.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, str]] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._sets = 0

    def _evict_if_expired(self, key: str) -> None:
        """Delete key if its monotonic expiration deadline has passed."""
        entry = self._store.get(key)
        if entry is not None and entry[0] < time.monotonic():
            del self._store[key]

    def get_json(self, key: str) -> dict[str, Any] | None:
        """Thread-safe TTL-checked retrieval of a JSON object."""
        with self._lock:
            self._evict_if_expired(key)
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                return None
            self._hits += 1
            return json.loads(entry[1])

    def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Thread-safe storage of JSON payload with expiration deadline."""
        deadline = time.monotonic() + max(1, ttl_seconds)
        payload = json.dumps(value, ensure_ascii=False)
        with self._lock:
            self._store[key] = (deadline, payload)
            self._sets += 1
        return True

    def delete(self, key: str) -> bool:
        """Delete single key from in-memory map."""
        with self._lock:
            return self._store.pop(key, None) is not None

    def flush_prefix(self, prefix: str) -> int:
        """Remove all keys matching prefix and return deleted count."""
        with self._lock:
            to_delete = [k for k in self._store if k.startswith(prefix)]
            for k in to_delete:
                del self._store[k]
            return len(to_delete)

    def stats(self) -> dict[str, Any]:
        """Return cache statistics matching RedisCacheStore schema."""
        now = time.monotonic()
        with self._lock:
            active_keys = [k for k, (exp, _) in self._store.items() if exp >= now]
        return {
            "backend": "in_memory_fallback",
            "connected": True,
            "total_keys": len(active_keys),
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / max(1, self._hits + self._misses), 4),
            "sample_keys": active_keys[:25],
        }


class CacheStoreFactory:
    """Factory creating and caching ICacheStore instances per Redis URL."""

    _instances: dict[str, ICacheStore] = {}

    @classmethod
    def get_store(cls, redis_url: str | None = None, *, force_memory: bool = False) -> ICacheStore:
        """
        Attempt to connect to Redis; fall back cleanly to InMemoryCacheStore if Redis
        is unavailable so local tests and developer runs never crash.
        """
        if force_memory:
            key = "memory://default"
            if key not in cls._instances:
                cls._instances[key] = InMemoryCacheStore()
            return cls._instances[key]

        url = redis_url or get_settings().redis_url
        if url in cls._instances:
            return cls._instances[url]

        try:
            client = redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=1.5)
            client.ping()
            store: ICacheStore = RedisCacheStore(client)
            logger.info(f"Connected to Redis cache at {url}")
        except Exception as exc:
            logger.warning(f"Redis unreachable at {url} ({exc}); activating InMemoryCacheStore fallback.")
            store = InMemoryCacheStore()

        cls._instances[url] = store
        return store


class SemanticQueryCacheService(ISemanticQueryCache):
    """
    Two-tier Cache-Aside query resolver backed by ICacheStore (Redis):
      1. Exact Canonical Key Lookup (normalized query + language + profile signature)
      2. Profile-Guarded Semantic Similarity Lookup (catches paraphrased "same kind of query"
         ONLY when language and canonical citizen profile signature match accurately!)
    """

    KEY_PREFIX = "scheme_guide:v1"

    def __init__(
        self,
        cache_store: ICacheStore,
        *,
        similarity_threshold: float = 0.85,
        exact_ttl_seconds: int = 3600,
        semantic_ttl_seconds: int = 3600,
    ) -> None:
        self._store = cache_store
        self._threshold = similarity_threshold
        self._exact_ttl = exact_ttl_seconds
        self._semantic_ttl = semantic_ttl_seconds

    @staticmethod
    def _normalize_query(query: str) -> str:
        """Lowercase, normalize whitespace, and strip trailing punctuation across Latin/Indic/Urdu scripts."""
        cleaned = re.sub(r"[^\w\s\u0600-\u06FF\u0900-\u0DFF]", " ", query.lower())
        return re.sub(r"\s+", " ", cleaned).strip()

    @staticmethod
    def _profile_hash(profile: CitizenProfile) -> str:
        """Compute deterministic SHA-256 digest of citizen demographic attributes and language."""
        sig_json = json.dumps(profile.canonical_signature(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(sig_json.encode("utf-8")).hexdigest()[:24]

    def _exact_key(self, normalized_query: str, profile_hash: str) -> str:
        """Construct namespaced exact cache key incorporating both query and profile digest."""
        q_hash = hashlib.sha256(normalized_query.encode("utf-8")).hexdigest()[:24]
        return f"{self.KEY_PREFIX}:exact:{profile_hash}:{q_hash}"

    def _semantic_bucket_key(self, profile_hash: str) -> str:
        """Construct semantic index bucket key scoped strictly to identical citizen profile hash."""
        return f"{self.KEY_PREFIX}:sem_bucket:{profile_hash}"

    def lookup_guide(
        self,
        *,
        query: str,
        profile: CitizenProfile,
    ) -> tuple[ApplicationGuideResponse | None, str, float | None]:
        """
        Check exact canonical Redis key first, then compare query vectors inside the
        profile-scoped semantic bucket to return accurate hits for similar/paraphrased queries.
        """
        norm_query = self._normalize_query(query)
        p_hash = self._profile_hash(profile)
        exact_key = self._exact_key(norm_query, p_hash)

        # Tier 1: O(1) exact canonical cache check
        exact_payload = self._store.get_json(exact_key)
        if exact_payload is not None:
            response = ApplicationGuideResponse.model_validate(exact_payload)
            response.cache_status = CacheStatus.EXACT_HIT
            response.cache_similarity = 1.0
            return response, CacheStatus.EXACT_HIT.value, 1.0

        # Tier 2: Semantic similarity match across previously cached queries sharing this profile signature
        bucket_key = self._semantic_bucket_key(p_hash)
        bucket = self._store.get_json(bucket_key)
        if not bucket or not bucket.get("entries"):
            return None, CacheStatus.MISS.value, None

        incoming_vec = _compute_trigram_vector(norm_query)
        best_sim = 0.0
        best_target_key: str | None = None

        for entry in bucket["entries"]:
            sim = _cosine_similarity(incoming_vec, entry.get("vector", []))
            if sim > best_sim:
                best_sim = sim
                best_target_key = entry.get("exact_key")

        # Only trigger semantic hit when cosine similarity crosses strict threshold
        if best_target_key and best_sim >= self._threshold:
            cached_payload = self._store.get_json(best_target_key)
            if cached_payload is not None:
                response = ApplicationGuideResponse.model_validate(cached_payload)
                response.cache_status = CacheStatus.SEMANTIC_HIT
                response.cache_similarity = round(best_sim, 4)
                return response, CacheStatus.SEMANTIC_HIT.value, round(best_sim, 4)

        return None, CacheStatus.MISS.value, None

    def store_guide(
        self,
        *,
        query: str,
        profile: CitizenProfile,
        response: ApplicationGuideResponse,
    ) -> None:
        """Persist guide response to exact cache key and append query vector to semantic bucket."""
        norm_query = self._normalize_query(query)
        p_hash = self._profile_hash(profile)
        exact_key = self._exact_key(norm_query, p_hash)

        # Store full serialized response in Redis with exact TTL
        self._store.set_json(exact_key, response.model_dump(), ttl_seconds=self._exact_ttl)

        # Update semantic bucket list (keep bounded to latest 25 entries per profile hash)
        bucket_key = self._semantic_bucket_key(p_hash)
        bucket = self._store.get_json(bucket_key) or {"entries": []}
        entries: list[dict[str, Any]] = [
            e for e in bucket.get("entries", []) if e.get("exact_key") != exact_key
        ]
        entries.append(
            {
                "exact_key": exact_key,
                "query_preview": norm_query[:120],
                "vector": _compute_trigram_vector(norm_query),
            }
        )
        bucket["entries"] = entries[-25:]
        self._store.set_json(bucket_key, bucket, ttl_seconds=self._semantic_ttl)

    def prewarm_cache_from_db(self, db_manager: Any) -> int:
        """
        Pre-warm Redis cache at startup / session initiation from PostgreSQL/SQLite:
        1. Preloads all 17 government schemes and policy chunks into Redis RAM.
        2. Preloads historical citizen sessions and queries into the two-tier exact and semantic
           cache buckets so subsequent matching queries return in sub-5ms with 0 tokens.
        """
        if db_manager is None:
            return 0

        from shared.infrastructure.database import (
            CitizenSessionORM,
            SchemeORM,
            SchemeChunkORM,
        )
        from shared.domain.models import UserProfileMemory, GroundingReport, LanguageReviewReport
        from shared.domain.enums import EligibilityStatus

        warmed_count = 0
        try:
            with db_manager.session_scope() as session:
                # 1. Preload schemes into Redis cache
                schemes = session.query(SchemeORM).all()
                for sch in schemes:
                    sch_key = f"{self.KEY_PREFIX}:scheme:{sch.scheme_id}"
                    self._store.set_json(
                        sch_key,
                        {
                            "scheme_id": sch.scheme_id,
                            "official_name": sch.official_name,
                            "ministry": sch.ministry,
                            "official_portal": sch.official_portal,
                            "helpline": sch.helpline,
                            "benefit_summary": sch.benefit_summary,
                        },
                        ttl_seconds=86400,
                    )
                    warmed_count += 1

                # 2. Preload chunks into Redis cache
                chunks = session.query(SchemeChunkORM).all()
                for chk in chunks:
                    chk_key = f"{self.KEY_PREFIX}:chunk:{chk.chunk_id}"
                    self._store.set_json(
                        chk_key,
                        {
                            "chunk_id": chk.chunk_id,
                            "scheme_id": chk.scheme_id,
                            "text": chk.chunk_text,
                        },
                        ttl_seconds=86400,
                    )
                    warmed_count += 1

                # 3. Preload past citizen queries from citizen_sessions into Redis exact/semantic buckets
                sessions = (
                    session.query(CitizenSessionORM)
                    .order_by(CitizenSessionORM.updated_at.desc())
                    .limit(100)
                    .all()
                )
                for sess in sessions:
                    try:
                        mem_data = sess.memory_snapshot_json
                        if not mem_data or not isinstance(mem_data, dict):
                            continue
                        memory = UserProfileMemory.model_validate(mem_data)
                        if not memory.profile or not memory.profile.raw_query:
                            continue

                        eligible = [
                            r for r in memory.eligibility_results if r.status == EligibilityStatus.ELIGIBLE
                        ]
                        potential = [
                            r for r in memory.eligibility_results if r.status == EligibilityStatus.POTENTIAL
                        ]
                        ineligible = [
                            r for r in memory.eligibility_results if r.status == EligibilityStatus.INELIGIBLE
                        ]

                        resp = ApplicationGuideResponse(
                            session_id=memory.session_id,
                            detected_language=memory.profile.language,
                            citizen_profile=memory.profile,
                            missing_profile_fields=memory.missing_profile_fields,
                            eligible_schemes=eligible,
                            potential_schemes=potential,
                            ineligible_schemes=ineligible,
                            document_checklist=memory.document_checklist,
                            final_reply=memory.final_reply_text or memory.draft_guide_text,
                            grounding_report=memory.grounding_report or GroundingReport(passed=True),
                            language_review_report=memory.language_review_report
                            or LanguageReviewReport(
                                target_language=memory.profile.language,
                                detected_reply_language=memory.profile.language.value,
                                language_consistent=True,
                            ),
                            pipeline_traces=memory.audit_log,
                            memory_audit_log=memory.audit_log,
                            cache_status=CacheStatus.EXACT_HIT,
                            cache_similarity=1.0,
                            total_latency_ms=1.5,
                        )
                        self.store_guide(
                            query=memory.profile.raw_query,
                            profile=memory.profile,
                            response=resp,
                        )
                        warmed_count += 1
                    except Exception as inner_exc:
                        logger.debug(f"Skipping pre-warming session {sess.session_id}: {inner_exc}")
                        continue

            logger.info(f"Redis cache pre-warming completed: {warmed_count} entities loaded into RAM.")
        except Exception as exc:
            logger.warning(f"Cache pre-warming encountered non-fatal error: {exc}")
        return warmed_count

    def flush_all(self) -> int:
        """Clear all cached query entries under the guide namespace."""
        return self._store.flush_prefix(f"{self.KEY_PREFIX}:")

