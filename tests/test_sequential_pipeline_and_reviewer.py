"""Tests for Microsoft Agent Framework SequentialPipeline & Language-Consistency Reviewer."""

import asyncio

from shared.domain.enums import AgentStage, LanguageCode
from shared.domain.models import ApplicationGuideRequest, UserProfileMemory
from services.agent_orchestrator_service.agents.language_reviewer_agent import (
    LanguageReviewerAgent,
)


def test_sequential_pipeline_executes_all_stages_and_streams(pipeline_bundle):
    """Verify SequentialBuilder executes all 6 agents in exact order and streams SSE events."""
    pipeline = pipeline_bundle["pipeline"]
    req = ApplicationGuideRequest(
        query="I am a 35-year-old urban small business owner with annual income 550000 INR and a 6-year-old girl child.",
        bypass_cache=True,
    )

    async def _run():
        resp = await pipeline.run(req)
        events: list[str] = []
        async for chunk in pipeline.run_stream(req):
            events.append(chunk)
        return resp, events

    resp, events = asyncio.run(_run())

    stages = [t.stage for t in resp.pipeline_traces]
    assert stages == [
        AgentStage.PROFILE_INTAKE,
        AgentStage.SCHEME_RETRIEVAL,
        AgentStage.ELIGIBILITY_RULE,
        AgentStage.DOCUMENT_CHECKLIST,
        AgentStage.GUIDE_MANAGER,
        AgentStage.LANGUAGE_REVIEWER,
    ]
    assert {s.scheme_id for s in resp.eligible_schemes} == {"PMMY", "SSY"}
    assert resp.grounding_report.passed is True
    assert resp.language_review_report.language_consistent is True
    assert resp.language_review_report.scheme_names_intact is True
    assert any("event: agent_step" in ev for ev in events)
    assert any("event: complete" in ev for ev in events)


def test_language_reviewer_repairs_corrupted_scheme_names(pipeline_bundle):
    """Verify Group-of-3 LanguageReviewerAgent detects & restores altered official scheme names."""
    from services.agent_orchestrator_service.clients.maf_chat_client import (
        DeterministicMultilingualChatClient,
    )
    from services.agent_orchestrator_service.memory.maf_context_provider import (
        SharedProfileMemoryContextProvider,
    )

    provider = SharedProfileMemoryContextProvider(
        pipeline_bundle["memory_client"], shared_session_id="rev-test"
    )
    reviewer = LanguageReviewerAgent(
        chat_client=DeterministicMultilingualChatClient(),
        memory_provider=provider,
        trace_collector=[],
    )

    # Simulate a translated reply where official scheme name was accidentally translated/omitted
    draft = "नमस्ते! आपकी प्रोफ़ाइल के आधार पर आप किसान सम्मान योजना के पात्र हैं।"
    expected = ["Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"]

    repaired, report = reviewer.review_and_repair(
        reply_text=draft,
        target_language=LanguageCode.HINDI,
        expected_scheme_names=expected,
        memory=UserProfileMemory(session_id="rev-test"),
    )

    assert "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)" in repaired
    assert report.scheme_names_intact is True
    assert len(report.repairs_applied) >= 1
