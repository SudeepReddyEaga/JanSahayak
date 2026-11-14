"""
Sequential Multi-Agent Pipeline Coordinator built on Microsoft Agent Framework
(`agent_framework.orchestrations.SequentialBuilder`).
Coordinates:
  1. ProfileIntakeAgent
  2. SchemeRetrievalAgent (RAG)
  3. EligibilityRuleAgent (Deterministic Rules)
  4. DocumentChecklistAgent
  5. GuideManagerAgent (+ GroundingGate check)
  6. LanguageReviewerAgent (Group-of-3 Add-On: Language Consistency & Scheme Name Integrity)
Integrated with Redis Exact + Profile-Guarded Semantic Query Caching.
"""

from collections.abc import AsyncIterator
import json
import time
import uuid

from agent_framework import SupportsChatGetResponse
from agent_framework.orchestrations import SequentialBuilder

from shared.config.settings import AppSettings
from shared.domain.enums import CacheStatus, EligibilityStatus
from shared.domain.models import (
    AgentStepTrace,
    ApplicationGuideRequest,
    ApplicationGuideResponse,
    GroundingReport,
    LanguageReviewReport,
    UserProfileMemory,
)
from shared.infrastructure.logging_utils import get_logger
from shared.interfaces.cache_interface import ISemanticQueryCache
from services.agent_orchestrator_service.agents.document_checklist_agent import (
    DocumentChecklistAgent,
)
from services.agent_orchestrator_service.agents.eligibility_rule_agent import (
    EligibilityRuleAgent,
)
from services.agent_orchestrator_service.agents.guide_manager_agent import (
    GuideManagerAgent,
)
from services.agent_orchestrator_service.agents.language_reviewer_agent import (
    LanguageReviewerAgent,
)
from services.agent_orchestrator_service.agents.profile_intake_agent import (
    ProfileIntakeAgent,
)
from services.agent_orchestrator_service.agents.scheme_retrieval_agent import (
    SchemeRetrievalAgent,
)
from services.agent_orchestrator_service.clients.profile_client import IProfileMemoryClient
from services.agent_orchestrator_service.clients.rag_client import IRAGRetrievalClient
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)
from services.agent_orchestrator_service.pipeline.grounding_gate import GroundingGate

logger = get_logger("sequential-pipeline")


class SequentialSchemePipeline:
    """
    Facade & Coordinator assembling all 6 Microsoft Agent Framework agents into
    a SequentialBuilder workflow with GroundingGate verification and Redis caching.
    """

    def __init__(
        self,
        *,
        settings: AppSettings,
        chat_client: SupportsChatGetResponse,
        memory_client: IProfileMemoryClient,
        rag_client: IRAGRetrievalClient,
        semantic_cache: ISemanticQueryCache | None = None,
    ) -> None:
        self._settings = settings
        self._chat_client = chat_client
        self._memory_client = memory_client
        self._rag_client = rag_client
        self._semantic_cache = semantic_cache
        self._grounding_gate = GroundingGate()

    def _build_workflow_and_agents(
        self,
        *,
        session_id: str,
        request: ApplicationGuideRequest,
        trace_collector: list[AgentStepTrace],
    ):
        """
        Instantiate the shared MAF ContextProvider, all 6 specialized agents,
        and compile them into an executable Microsoft Agent Framework SequentialBuilder Workflow.
        """
        memory_provider = SharedProfileMemoryContextProvider(
            self._memory_client,
            shared_session_id=session_id,
        )

        # Construct each specialized agent module wired to the shared UserProfileMemory provider
        intake_agent = ProfileIntakeAgent(
            chat_client=self._chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
            raw_query=request.query,
            preferred_language=request.preferred_language,
            profile_overrides=request.profile_overrides,
        )
        retrieval_agent = SchemeRetrievalAgent(
            chat_client=self._chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
            rag_client=self._rag_client,
            top_k=self._settings.rag_top_k,
            bypass_rag_cache=request.bypass_cache,
        )
        rule_agent = EligibilityRuleAgent(
            chat_client=self._chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
            rag_client=self._rag_client,
        )
        checklist_agent = DocumentChecklistAgent(
            chat_client=self._chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
            rag_client=self._rag_client,
        )
        guide_manager = GuideManagerAgent(
            chat_client=self._chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
            grounding_verifier=self._grounding_gate,
        )
        language_reviewer = LanguageReviewerAgent(
            chat_client=self._chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
        )

        # Wire all 6 participants sequentially via Microsoft Agent Framework SequentialBuilder
        workflow = SequentialBuilder(
            name="MultilingualSchemeEligibilityPipeline",
            participants=[
                intake_agent,
                retrieval_agent,
                rule_agent,
                checklist_agent,
                guide_manager,
                language_reviewer,
            ],
            output_from=[language_reviewer],
            intermediate_output_from="all_other",
        ).build()

        return workflow, memory_provider

    @staticmethod
    def _assemble_response(
        *,
        memory: UserProfileMemory,
        traces: list[AgentStepTrace],
        cache_status: CacheStatus,
        cache_similarity: float | None,
        total_latency_ms: float,
    ) -> ApplicationGuideResponse:
        """Convert final shared UserProfileMemory state into API ApplicationGuideResponse DTO."""
        eligible = [
            r for r in memory.eligibility_results if r.status == EligibilityStatus.ELIGIBLE
        ]
        potential = [
            r for r in memory.eligibility_results if r.status == EligibilityStatus.POTENTIAL
        ]
        ineligible = [
            r for r in memory.eligibility_results if r.status == EligibilityStatus.INELIGIBLE
        ]

        grounding = memory.grounding_report or GroundingReport(passed=True)
        review = memory.language_review_report or LanguageReviewReport(
            target_language=memory.profile.language,
            detected_reply_language=memory.profile.language.value,
            language_consistent=True,
        )

        return ApplicationGuideResponse(
            session_id=memory.session_id,
            detected_language=memory.profile.language,
            citizen_profile=memory.profile,
            missing_profile_fields=memory.missing_profile_fields,
            eligible_schemes=eligible,
            potential_schemes=potential,
            ineligible_schemes=ineligible,
            document_checklist=memory.document_checklist,
            final_reply=memory.final_reply_text or memory.draft_guide_text,
            grounding_report=grounding,
            language_review_report=review,
            pipeline_traces=traces,
            memory_audit_log=memory.audit_log,
            cache_status=cache_status,
            cache_similarity=cache_similarity,
            total_latency_ms=round(total_latency_ms, 2),
        )

    async def run(self, request: ApplicationGuideRequest) -> ApplicationGuideResponse:
        """
        Execute the full pipeline with Cache-Aside Redis acceleration:
          1. Quick-extract canonical citizen profile for profile-safe Redis cache check.
          2. Return exact or semantic Redis hit immediately if available and not bypassed.
          3. Otherwise execute Microsoft Agent Framework SequentialBuilder across all 6 agents.
          4. Persist validated response to Redis Exact + Semantic Query Cache.
        """
        started = time.perf_counter()
        session_id = request.session_id or f"sess-{uuid.uuid4().hex[:12]}"

        # Step 1: Check Redis Exact + Profile-Guarded Semantic Cache (only for fresh queries unless matching session)
        existing_mem = await self._memory_client.get_or_create_memory(session_id)
        quick_profile = ProfileIntakeAgent.extract_quick_profile(
            raw_query=request.query,
            preferred_language=request.preferred_language,
            profile_overrides=request.profile_overrides,
            existing_profile=existing_mem.profile if existing_mem.profile.raw_query else None,
        )

        if self._semantic_cache is not None and not request.bypass_cache:
            cached_resp, status_str, sim = self._semantic_cache.lookup_guide(
                query=request.query,
                profile=quick_profile,
            )
            if cached_resp is not None:
                cached_resp.session_id = session_id
                cached_resp.total_latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
                logger.info(
                    f"Redis {status_str} (sim={sim}) in {cached_resp.total_latency_ms}ms for session={session_id}"
                )
                return cached_resp

        # Step 2: Cache miss -> Build and run Microsoft Agent Framework SequentialBuilder workflow
        traces: list[AgentStepTrace] = []
        workflow, _ = self._build_workflow_and_agents(
            session_id=session_id,
            request=request,
            trace_collector=traces,
        )
        await workflow.run(request.query)

        # Step 3: Load final enriched shared UserProfileMemory written by all 6 agents
        final_memory = await self._memory_client.get_or_create_memory(session_id)
        total_ms = (time.perf_counter() - started) * 1000.0

        response = self._assemble_response(
            memory=final_memory,
            traces=traces,
            cache_status=CacheStatus.BYPASSED if request.bypass_cache else CacheStatus.MISS,
            cache_similarity=None,
            total_latency_ms=total_ms,
        )

        # Step 4: Store clean grounded response in Redis for future exact or similar queries
        if self._semantic_cache is not None and response.grounding_report.passed:
            self._semantic_cache.store_guide(
                query=request.query,
                profile=final_memory.profile,
                response=response,
            )

        return response

    async def run_stream(self, request: ApplicationGuideRequest) -> AsyncIterator[str]:
        """
        Server-Sent Events (SSE) generator emitting live stage progress updates as each
        Microsoft Agent Framework sequential participant completes, ending with the full JSON result.
        """
        started = time.perf_counter()
        session_id = request.session_id or f"sess-{uuid.uuid4().hex[:12]}"

        existing_mem = await self._memory_client.get_or_create_memory(session_id)
        quick_profile = ProfileIntakeAgent.extract_quick_profile(
            raw_query=request.query,
            preferred_language=request.preferred_language,
            profile_overrides=request.profile_overrides,
            existing_profile=existing_mem.profile if existing_mem.profile.raw_query else None,
        )

        # Fast-path Redis cache hit streamed directly to UI
        if self._semantic_cache is not None and not request.bypass_cache:
            cached_resp, status_str, sim = self._semantic_cache.lookup_guide(
                query=request.query,
                profile=quick_profile,
            )
            if cached_resp is not None:
                cached_resp.session_id = session_id
                cached_resp.total_latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
                yield f"event: cache_hit\ndata: {json.dumps({'cache_status': status_str, 'similarity': sim})}\n\n"
                yield f"event: complete\ndata: {cached_resp.model_dump_json()}\n\n"
                return

        # Execute MAF SequentialBuilder in streaming mode
        traces: list[AgentStepTrace] = []
        workflow, _ = self._build_workflow_and_agents(
            session_id=session_id,
            request=request,
            trace_collector=traces,
        )
        stream = workflow.run(request.query, stream=True)
        emitted_trace_count = 0
        async for _event in stream:
            # Emit each newly finished AgentStepTrace immediately to the interactive UI
            while emitted_trace_count < len(traces):
                step_trace = traces[emitted_trace_count]
                emitted_trace_count += 1
                yield f"event: agent_step\ndata: {step_trace.model_dump_json()}\n\n"

        await stream.get_final_response()
        while emitted_trace_count < len(traces):
            step_trace = traces[emitted_trace_count]
            emitted_trace_count += 1
            yield f"event: agent_step\ndata: {step_trace.model_dump_json()}\n\n"

        final_memory = await self._memory_client.get_or_create_memory(session_id)
        total_ms = (time.perf_counter() - started) * 1000.0
        response = self._assemble_response(
            memory=final_memory,
            traces=traces,
            cache_status=CacheStatus.BYPASSED if request.bypass_cache else CacheStatus.MISS,
            cache_similarity=None,
            total_latency_ms=total_ms,
        )

        if self._semantic_cache is not None and response.grounding_report.passed:
            self._semantic_cache.store_guide(
                query=request.query,
                profile=final_memory.profile,
                response=response,
            )

        yield f"event: complete\ndata: {response.model_dump_json()}\n\n"

