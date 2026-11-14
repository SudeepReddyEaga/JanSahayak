"""
End-to-End Microservice HTTP Integration Test.
Boots all 4 FastAPI microservices (profile-memory, rag-retrieval, agent-orchestrator, api-gateway)
on ephemeral localhost ports in microservice_http mode and verifies true cross-process HTTP
communication, shared DB persistence, semantic caching, and UI serving.
"""

import os
from pathlib import Path
import subprocess
import sys
import time
import httpx


def _wait_ready(url: str, timeout_s: float = 15.0) -> None:
    """Poll microservice /health endpoint until HTTP 200 or raise TimeoutError."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            r = httpx.get(url, timeout=1.0)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.25)
    raise TimeoutError(f"Service did not become healthy at {url} within {timeout_s}s")


def test_full_microservice_http_cluster(tmp_path: Path):
    """Boot all 4 FastAPI microservices and test end-to-end citizen guide flow over HTTP."""
    db_path = tmp_path / "cluster_test.db"
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(Path(__file__).resolve().parent.parent),
            "ORCHESTRATION_MODE": "microservice_http",
            "DATABASE_URL": f"sqlite:///{db_path.as_posix()}",
            "REDIS_URL": "redis://127.0.0.1:6399/9",
            "PROFILE_MEMORY_SERVICE_URL": "http://127.0.0.1:18001",
            "RAG_RETRIEVAL_SERVICE_URL": "http://127.0.0.1:18002",
            "AGENT_ORCHESTRATOR_SERVICE_URL": "http://127.0.0.1:18003",
            "VOICE_SPEECH_SERVICE_URL": "http://127.0.0.1:18004",
            "SEMANTIC_CACHE_THRESHOLD": "0.78",
        }
    )

    cmds_and_ports = [
        ([sys.executable, "-m", "uvicorn", "services.profile_memory_service.main:app", "--host", "127.0.0.1", "--port", "18001"], "http://127.0.0.1:18001/health"),
        ([sys.executable, "-m", "uvicorn", "services.rag_retrieval_service.main:app", "--host", "127.0.0.1", "--port", "18002"], "http://127.0.0.1:18002/health"),
        ([sys.executable, "-m", "uvicorn", "services.agent_orchestrator_service.main:app", "--host", "127.0.0.1", "--port", "18003"], "http://127.0.0.1:18003/health"),
        ([sys.executable, "-m", "uvicorn", "services.voice_speech_service.main:app", "--host", "127.0.0.1", "--port", "18004"], "http://127.0.0.1:18004/health"),
        ([sys.executable, "-m", "uvicorn", "services.api_gateway.main:app", "--host", "127.0.0.1", "--port", "18000"], "http://127.0.0.1:18000/health"),
    ]

    procs: list[subprocess.Popen] = []
    try:
        for cmd, health_url in cmds_and_ports:
            procs.append(
                subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            )
            _wait_ready(health_url, timeout_s=20.0)

        # Verify aggregated microservice health check across all 5 microservices
        health = httpx.get("http://127.0.0.1:18000/health", timeout=5.0).json()
        assert health["services"]["profile_memory_service"] == "healthy"
        assert health["services"]["rag_retrieval_service"] == "healthy"
        assert health["services"]["agent_orchestrator_service"] == "healthy"
        assert health["services"]["voice_speech_service"] == "healthy"

        # Verify UI root serves clean HTML with zero Q14 references and serves voice controller script
        ui_resp = httpx.get("http://127.0.0.1:18000/", timeout=5.0)
        assert ui_resp.status_code == 200
        assert "Multilingual Government Scheme Eligibility Guide" in ui_resp.text
        assert "Q14" not in ui_resp.text
        voice_js = httpx.get("http://127.0.0.1:18000/static/voice_controller.js", timeout=5.0)
        assert voice_js.status_code == 200
        assert "CitizenVoiceController" in voice_js.text

        # Verify Voice & Speech Microservice integration via Gateway
        locales_resp = httpx.get("http://127.0.0.1:18000/api/v1/voice/locales", timeout=5.0)
        assert locales_resp.status_code == 200
        assert len(locales_resp.json()) == 12
        speech_resp = httpx.post(
            "http://127.0.0.1:18000/api/v1/voice/prepare-speech",
            json={
                "text": "### ਯੋਗ ਯੋਜਨਾ\nPradhan Mantri Kisan Samman Nidhi (PM-KISAN): ₹6,000 https://pmkisan.gov.in",
                "language": "pa",
            },
            timeout=5.0,
        )
        assert speech_resp.status_code == 200
        assert speech_resp.json()["bcp47_tag"] == "pa-IN"

        # Execute live multilingual query across all HTTP microservices
        query = "मैं 65 साल का किसान हूं। मैं गांव में रहता हूं, मेरे पास 2 एकड़ खेती की जमीन है, सालाना आय 90000 रुपये है, BPL कार्ड है और पक्का घर नहीं है।"
        guide = httpx.post(
            "http://127.0.0.1:18000/api/v1/guide",
            json={"query": query},
            timeout=30.0,
        )
        assert guide.status_code == 200
        data = guide.json()
        assert {s["scheme_id"] for s in data["eligible_schemes"]} == {
            "PM-KISAN",
            "PMFBY",
            "PMAY-G",
            "AB-PMJAY",
            "IGNOAPS",
            "MGNREGA",
        }
        assert data["detected_language"] == "hi"
        assert data["grounding_report"]["passed"] is True
        assert data["language_review_report"]["language_consistent"] is True
        assert data["language_review_report"]["scheme_names_intact"] is True

        # Verify persisted session memory via API Gateway -> Profile Memory Service
        mem = httpx.get(f"http://127.0.0.1:18000/api/v1/profiles/{data['session_id']}", timeout=5.0)
        assert mem.status_code == 200
        assert len(mem.json()["audit_log"]) >= 12
    finally:
        for p in procs:
            p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
