"""
Hybrid BM25 + Vector RAG Retriever with Multilingual Profile Query Expansion
and Redis Retrieval Caching.
Guarantees high recall across all 7 citizen languages while remaining strictly
grounded to chunks stored inside PostgreSQL.
"""

import hashlib
import math
import re
import time

from shared.domain.enums import LanguageCode
from shared.domain.models import (
    CitizenProfile,
    RAGQueryResponse,
    RetrievedSchemeChunk,
    SchemeDefinition,
)
from shared.infrastructure.redis_cache import _cosine_similarity
from shared.interfaces.cache_interface import ICacheStore
from shared.interfaces.retrieval_interface import IEmbeddingProvider, IVectorRetriever
from services.rag_retrieval_service.repository import SqlSchemeRepository


def _tokenize(text: str) -> list[str]:
    """Tokenize Unicode text (Latin, Indic, and Urdu/Arabic scripts) into normalized lowercase terms."""
    return re.findall(r"[\w\u0600-\u06FF\u0900-\u0DFF]+", text.lower())


class HybridSchemeRetriever(IVectorRetriever):
    """
    Combines Okapi BM25 lexical matching, dense vector cosine similarity,
    and citizen profile metadata expansion to retrieve grounded candidate schemes.
    """

    RAG_CACHE_PREFIX = "scheme_guide:v1:rag:"

    def __init__(
        self,
        scheme_repo: SqlSchemeRepository,
        embedder: IEmbeddingProvider,
        cache_store: ICacheStore,
        *,
        rag_ttl_seconds: int = 1800,
    ) -> None:
        self._repo = scheme_repo
        self._embedder = embedder
        self._cache = cache_store
        self._ttl = rag_ttl_seconds
        self._indexed_chunks: list[dict] = []
        self._doc_freq: dict[str, int] = {}
        self._avg_doc_len: float = 1.0
        self.refresh_index()

    def refresh_index(self) -> int:
        """Load chunks from database and precompute BM25 document frequency statistics."""
        pairs = self._repo.list_chunks_with_schemes()
        self._indexed_chunks = []
        self._doc_freq = {}
        total_len = 0

        for chunk_orm, scheme in pairs:
            tokens = _tokenize(chunk_orm.chunk_text)
            total_len += len(tokens)
            # Increment document frequency once per unique term inside chunk
            for tok in set(tokens):
                self._doc_freq[tok] = self._doc_freq.get(tok, 0) + 1

            self._indexed_chunks.append(
                {
                    "chunk_id": chunk_orm.chunk_id,
                    "scheme_id": scheme.scheme_id,
                    "official_name": scheme.official_name,
                    "chunk_text": chunk_orm.chunk_text,
                    "embedding": chunk_orm.embedding_json or self._embedder.embed(chunk_orm.chunk_text),
                    "tokens": tokens,
                    "target_tags": [t.lower() for t in scheme.target_tags],
                    "keywords": [k.lower() for k in scheme.multilingual_keywords],
                }
            )

        self._avg_doc_len = total_len / max(1, len(self._indexed_chunks))
        return len(self._indexed_chunks)

    def index_schemes(self, schemes: list[SchemeDefinition]) -> int:
        """Persist scheme list via repository and rebuild in-memory BM25 + vector index."""
        for scheme in schemes:
            self._repo.upsert_scheme(scheme)
        return self.refresh_index()

    @staticmethod
    def expand_query_with_profile(query_text: str, profile: CitizenProfile | None) -> str:
        """
        Translate structured CitizenProfile traits into English semantic search terms
        so multilingual queries accurately match canonical scheme documents.
        """
        terms: list[str] = [query_text]
        if profile is None:
            return query_text

        if profile.occupation:
            terms.append(profile.occupation.replace("_", " "))
            if profile.occupation == "farmer":
                terms.extend(["farmer", "kisan", "crop", "insurance", "agriculture", "land"])
            elif profile.occupation == "student":
                terms.extend(["student", "scholarship", "college", "education"])
            elif profile.occupation == "street_vendor":
                terms.extend(["street vendor", "hawker", "svanidhi", "urban", "loan"])
            elif profile.occupation in {"artisan", "craftsperson", "potter", "tailor", "carpenter", "weaver"}:
                terms.extend(["artisan", "vishwakarma", "craftsperson", "mudra", "loan"])
            elif profile.occupation in {"small_business", "shopkeeper", "self_employed"}:
                terms.extend(["business", "mudra", "loan", "entrepreneur"])
            elif profile.occupation in {"daily_wage_laborer", "unemployed", "agricultural_worker"}:
                terms.extend(["employment", "wage", "mgnrega", "laborer"])

        if profile.residence_type == "rural":
            terms.extend(["rural", "village", "housing", "mgnrega", "awas"])
        elif profile.residence_type == "urban":
            terms.extend(["urban", "city", "vendor", "business"])

        if profile.owns_pucca_house is False:
            terms.extend(["pucca house", "kutcha", "awas", "housing"])
        if profile.has_bpl_card:
            terms.extend(["bpl", "health", "ayushman", "hospital", "pension"])
        if profile.annual_income_inr is not None and profile.annual_income_inr <= 250000:
            terms.extend(["low income", "health", "ayushman", "scholarship", "bpl"])
        if profile.gender == "female":
            terms.extend(["woman", "female"])
        if profile.marital_status == "widowed":
            terms.extend(["widow", "pension"])
        if profile.is_pregnant_or_lactating:
            terms.extend(["pregnant", "maternity", "lactating", "matru"])
        if profile.has_lpg_connection is False:
            terms.extend(["lpg", "gas", "ujjwala", "cooking"])
        if profile.age is not None and profile.age >= 60:
            terms.extend(["senior", "old age", "elderly", "pension", "ayushman"])
        if profile.has_disability:
            terms.extend(["disability", "divyang", "pension", "assistive devices", "wheelchair"])
        if profile.has_girl_child_under_10:
            terms.extend(["girl child", "daughter", "sukanya", "savings"])
        if profile.social_category:
            terms.append(profile.social_category)

        return " ".join(terms)

    def _bm25_score(self, query_tokens: list[str], doc_tokens: list[str], k1: float = 1.5, b: float = 0.75) -> float:
        """Compute Okapi BM25 lexical relevance score for a single chunk."""
        if not query_tokens or not doc_tokens:
            return 0.0
        n_docs = max(1, len(self._indexed_chunks))
        tf_map: dict[str, int] = {}
        for t in doc_tokens:
            tf_map[t] = tf_map.get(t, 0) + 1

        doc_len = len(doc_tokens)
        score = 0.0
        for q_tok in set(query_tokens):
            df = self._doc_freq.get(q_tok, 0)
            if df == 0:
                continue
            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
            tf = tf_map.get(q_tok, 0)
            denom = tf + k1 * (1.0 - b + b * (doc_len / max(1.0, self._avg_doc_len)))
            score += idf * ((tf * (k1 + 1.0)) / max(1e-6, denom))
        return score

    def retrieve(
        self,
        *,
        query_text: str,
        language: LanguageCode,
        profile: CitizenProfile | None,
        top_k: int,
    ) -> tuple[list[RetrievedSchemeChunk], str]:
        """Run hybrid BM25 + dense cosine similarity + tag boost retrieval over indexed chunks."""
        if not self._indexed_chunks:
            self.refresh_index()

        expanded_query = self.expand_query_with_profile(query_text, profile)
        query_tokens = _tokenize(expanded_query)
        query_vec = self._embedder.embed(expanded_query)
        query_token_set = set(query_tokens)

        # Compute raw scores across all chunks
        raw_bm25 = [self._bm25_score(query_tokens, c["tokens"]) for c in self._indexed_chunks]
        max_bm25 = max(raw_bm25) if raw_bm25 and max(raw_bm25) > 0 else 1.0

        scored: list[RetrievedSchemeChunk] = []
        for idx, chunk in enumerate(self._indexed_chunks):
            norm_bm25 = raw_bm25[idx] / max_bm25
            vec_score = max(0.0, _cosine_similarity(query_vec, chunk["embedding"]))

            # Compute small metadata tag overlap bonus for precision ranking
            matched_kw = [kw for kw in chunk["keywords"] if kw in expanded_query.lower()][:5]
            tag_hits = sum(1 for tag in chunk["target_tags"] if any(t in query_token_set for t in tag.split()))
            tag_bonus = min(0.25, tag_hits * 0.05)

            hybrid = round(0.50 * norm_bm25 + 0.35 * vec_score + 0.15 * (tag_bonus / 0.25), 4)
            scored.append(
                RetrievedSchemeChunk(
                    chunk_id=chunk["chunk_id"],
                    scheme_id=chunk["scheme_id"],
                    official_name=chunk["official_name"],
                    chunk_text=chunk["chunk_text"],
                    bm25_score=round(norm_bm25, 4),
                    vector_score=round(vec_score, 4),
                    hybrid_score=hybrid,
                    matched_keywords=matched_kw,
                )
            )

        # Sort chunks highest score first and keep top scoring chunk per scheme up to top_k schemes
        scored.sort(key=lambda c: c.hybrid_score, reverse=True)
        selected: list[RetrievedSchemeChunk] = []
        seen_schemes: set[str] = set()
        for chunk in scored:
            if chunk.scheme_id not in seen_schemes:
                seen_schemes.add(chunk.scheme_id)
                selected.append(chunk)
            if len(selected) >= top_k:
                break

        return selected, expanded_query

    def retrieve_with_cache(
        self,
        *,
        query_text: str,
        language: LanguageCode,
        profile: CitizenProfile | None,
        top_k: int = 10,
        bypass_cache: bool = False,
    ) -> RAGQueryResponse:
        """
        Cache-aside wrapper checking Redis before executing hybrid BM25 + vector retrieval.
        Guarantees rapid retrieval when identical profile/query expansions recur.
        """
        started = time.perf_counter()
        expanded_preview = self.expand_query_with_profile(query_text, profile)
        cache_key_raw = f"{language.value}|{top_k}|{expanded_preview.lower().strip()}"
        cache_key = f"{self.RAG_CACHE_PREFIX}{hashlib.sha256(cache_key_raw.encode('utf-8')).hexdigest()[:24]}"

        if not bypass_cache:
            cached = self._cache.get_json(cache_key)
            if cached is not None:
                resp = RAGQueryResponse.model_validate(cached)
                resp.cache_hit = True
                resp.retrieval_latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
                return resp

        chunks, expanded_query = self.retrieve(
            query_text=query_text,
            language=language,
            profile=profile,
            top_k=top_k,
        )
        unique_ids = list(dict.fromkeys(c.scheme_id for c in chunks))
        resp = RAGQueryResponse(
            query_text=query_text,
            expanded_query=expanded_query,
            chunks=chunks,
            unique_scheme_ids=unique_ids,
            cache_hit=False,
            retrieval_latency_ms=round((time.perf_counter() - started) * 1000.0, 2),
        )
        self._cache.set_json(cache_key, resp.model_dump(), ttl_seconds=self._ttl)
        return resp

