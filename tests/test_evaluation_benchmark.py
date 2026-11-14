"""End-to-End 10-Profile Precision & Recall Benchmark Test + API Gateway Integration Tests."""

import asyncio


def test_ten_profile_benchmark_precision_and_recall(pipeline_bundle):
    """
    Execute all 10 ground-truth citizen profiles across 7 languages and verify
    high Precision, Recall, F1, Grounding Pass Rate, Language Consistency, and Scheme Name Intact Rate.
    """
    evaluator = pipeline_bundle["evaluator"]
    summary = asyncio.run(evaluator.run_evaluation(persist=True))

    assert summary.total_profiles == 10
    # Assert strict precision & recall targets across all 10 profiles
    assert summary.macro_precision >= 0.95, f"Low precision: {summary.profile_results}"
    assert summary.macro_recall >= 0.95, f"Low recall: {summary.profile_results}"
    assert summary.micro_precision >= 0.95
    assert summary.micro_recall >= 0.95
    assert summary.grounding_pass_rate == 1.0
    assert summary.language_consistency_rate == 1.0
    assert summary.scheme_name_preservation_rate == 1.0


def test_api_gateway_endpoints(api_client):
    """Verify Gateway health, schemes KB, citizen guide, cache stats, and evaluation endpoints."""
    health = api_client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    schemes = api_client.get("/api/v1/schemes")
    assert schemes.status_code == 200
    assert len(schemes.json()) == 17

    guide = api_client.post(
        "/api/v1/guide",
        json={
            "query": "I am a 20-year-old male undergraduate college student from the OBC category living in an urban city. My family annual income is 180000 INR."
        },
    )
    assert guide.status_code == 200
    body = guide.json()
    assert {s["scheme_id"] for s in body["eligible_schemes"]} == {"AB-PMJAY", "NSP-PMS", "PM-YASASVI"}
    assert body["grounding_report"]["passed"] is True
    assert body["language_review_report"]["scheme_names_intact"] is True

    # Check persisted session memory via API
    session_id = body["session_id"]
    mem = api_client.get(f"/api/v1/profiles/{session_id}")
    assert mem.status_code == 200
    assert mem.json()["session_id"] == session_id

    # Check cache stats & flush endpoint
    stats = api_client.get("/api/v1/cache/stats")
    assert stats.status_code == 200
    flush = api_client.post("/api/v1/cache/flush")
    assert flush.status_code == 200

    # Run evaluation via API
    eval_resp = api_client.post("/api/v1/evaluate")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["total_profiles"] == 10
    assert eval_data["macro_precision"] == 1.0
    assert eval_data["macro_recall"] == 1.0
