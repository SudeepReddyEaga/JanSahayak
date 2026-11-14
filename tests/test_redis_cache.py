"""Tests for Redis Exact Cache, Semantic Paraphrase Cache Hit, and Profile-Safety Isolation."""

import asyncio

from shared.domain.enums import CacheStatus
from shared.domain.models import ApplicationGuideRequest


def test_redis_exact_and_semantic_cache_accuracy(pipeline_bundle):
    """
    Verify:
      1. First query -> CacheStatus.MISS
      2. Identical query -> CacheStatus.EXACT_HIT
      3. Paraphrased query with matching citizen profile -> CacheStatus.SEMANTIC_HIT
      4. Different citizen income/occupation -> CacheStatus.MISS (prevents stale/wrong hits!)
    """
    pipeline = pipeline_bundle["pipeline"]

    async def _run():
        q1 = "I am a 35-year-old urban small business owner with an annual income of 550000 INR and I have a 6-year-old girl child."
        r1 = await pipeline.run(ApplicationGuideRequest(query=q1))
        assert r1.cache_status == CacheStatus.MISS
        assert {s.scheme_id for s in r1.eligible_schemes} == {"PMMY", "SSY"}

        # Exact repeat
        r2 = await pipeline.run(ApplicationGuideRequest(query=q1))
        assert r2.cache_status == CacheStatus.EXACT_HIT
        assert r2.cache_similarity == 1.0
        assert {s.scheme_id for s in r2.eligible_schemes} == {"PMMY", "SSY"}

        # Close paraphrase with same extracted profile attributes
        q_para = "I am a 35-year-old urban small business owner with annual income 550000 INR and a 6-year-old girl child, which schemes fit?"
        r3 = await pipeline.run(ApplicationGuideRequest(query=q_para))
        assert r3.cache_status == CacheStatus.SEMANTIC_HIT
        assert r3.cache_similarity is not None and r3.cache_similarity >= 0.78
        assert {s.scheme_id for s in r3.eligible_schemes} == {"PMMY", "SSY"}

        # Different profile attribute (income=180000 instead of 550000 -> now qualifies for AB-PMJAY too!)
        q_diff = "I am a 35-year-old urban small business owner with an annual income of 180000 INR and I have a 6-year-old girl child."
        r4 = await pipeline.run(ApplicationGuideRequest(query=q_diff))
        assert r4.cache_status == CacheStatus.MISS
        assert {s.scheme_id for s in r4.eligible_schemes} == {"AB-PMJAY", "PMMY", "SSY"}

    asyncio.run(_run())
