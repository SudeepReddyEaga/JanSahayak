"""
Module 2: Scheme Retrieval Agent (Separate Agent Module).
Responsibilities:
  - Read structured CitizenProfile and raw query from shared UserProfileMemory.
  - Invoke the rag-retrieval-service via IRAGRetrievalClient to perform hybrid
    BM25 + Dense Vector RAG retrieval over government scheme documents.
  - Write ranked RetrievedSchemeChunk citations and unique candidate scheme IDs
    back into shared UserProfileMemory for deterministic evaluation.
"""

from typing import Any

from agent_framework import SupportsChatGetResponse

from shared.domain.enums import AgentStage
from shared.domain.models import AgentStepTrace, RAGQueryRequest, UserProfileMemory
from services.agent_orchestrator_service.agents.base_specialized_agent import (
    SpecializedPipelineAgent,
)
from services.agent_orchestrator_service.clients.rag_client import IRAGRetrievalClient
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)


class SchemeRetrievalAgent(SpecializedPipelineAgent):
    """Executes grounded hybrid RAG retrieval over scheme documents."""

    def __init__(
        self,
        *,
        chat_client: SupportsChatGetResponse[Any],
        memory_provider: SharedProfileMemoryContextProvider,
        trace_collector: list[AgentStepTrace],
        rag_client: IRAGRetrievalClient,
        top_k: int = 10,
        bypass_rag_cache: bool = False,
    ) -> None:
        super().__init__(
            stage=AgentStage.SCHEME_RETRIEVAL,
            agent_name="SchemeRetrievalAgent",
            description="Retrieves grounded government scheme documents using hybrid BM25 + vector RAG.",
            instructions=(
                "You are the Scheme Retrieval Agent. Read the citizen's profile from shared memory, "
                "query the Scheme RAG Knowledge Base, and persist top matching scheme chunks and IDs."
            ),
            chat_client=chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
        )
        self._rag_client = rag_client
        self._top_k = top_k
        self._bypass_rag_cache = bypass_rag_cache

    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Query rag-retrieval-service using citizen query + structured profile expansion."""
        request = RAGQueryRequest(
            query_text=memory.profile.raw_query or "government welfare scheme eligibility",
            language=memory.profile.language,
            profile=memory.profile,
            top_k=self._top_k,
            bypass_cache=self._bypass_rag_cache,
        )
        rag_response = await self._rag_client.retrieve(request)

        # Persist retrieved chunks and unique candidate scheme IDs into shared UserProfileMemory
        memory.retrieved_chunks = rag_response.chunks
        memory.retrieved_scheme_ids = rag_response.unique_scheme_ids

        top_preview = ", ".join(
            f"{c.scheme_id}({c.hybrid_score:.2f})" for c in rag_response.chunks[:5]
        )
        trace = AgentStepTrace(
            stage=self.stage,
            agent_name=self.agent_name,
            status="completed",
            memory_reads=["profile", "profile.raw_query", "profile.language"],
            memory_writes=["retrieved_chunks", "retrieved_scheme_ids"],
            output_summary=(
                f"Retrieved {len(rag_response.chunks)} grounded scheme candidates "
                f"(rag_cache_hit={rag_response.cache_hit}): {top_preview}."
            ),
        )
        return memory, trace

