"""
Module 4: Document Checklist Agent (Separate Agent Module).
Responsibilities:
  - Read eligible_scheme_ids and citizen language from shared UserProfileMemory.
  - Fetch authoritative document lists from the Scheme Knowledge Base.
  - Deduplicate overlapping papers (e.g., Aadhaar Card, Bank Passbook) across all
    eligible schemes while preserving per-scheme linkage and localized names.
  - Write consolidated document_checklist back to shared UserProfileMemory.
"""

from typing import Any

from agent_framework import SupportsChatGetResponse

from shared.domain.enums import AgentStage
from shared.domain.models import AgentStepTrace, DocumentRequirement, UserProfileMemory
from services.agent_orchestrator_service.agents.base_specialized_agent import (
    SpecializedPipelineAgent,
)
from services.agent_orchestrator_service.clients.rag_client import IRAGRetrievalClient
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)


class DocumentChecklistAgent(SpecializedPipelineAgent):
    """Compiles a deduplicated, grounded paper checklist across all eligible schemes."""

    def __init__(
        self,
        *,
        chat_client: SupportsChatGetResponse[Any],
        memory_provider: SharedProfileMemoryContextProvider,
        trace_collector: list[AgentStepTrace],
        rag_client: IRAGRetrievalClient,
    ) -> None:
        super().__init__(
            stage=AgentStage.DOCUMENT_CHECKLIST,
            agent_name="DocumentChecklistAgent",
            description="Aggregates and deduplicates verified required documents for eligible schemes.",
            instructions=(
                "You are the Document Checklist Agent. Read eligible scheme IDs from shared memory, "
                "retrieve canonical required papers, deduplicate shared documents like Aadhaar/Bank Passbook, "
                "and write the consolidated checklist back into shared UserProfileMemory."
            ),
            chat_client=chat_client,
            memory_provider=memory_provider,
            trace_collector=trace_collector,
        )
        self._rag_client = rag_client

    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Collect and deduplicate DocumentRequirement objects for every eligible scheme."""
        merged_docs: dict[str, DocumentRequirement] = {}

        for scheme_id in memory.eligible_scheme_ids:
            scheme = await self._rag_client.get_scheme(scheme_id)
            if scheme is None:
                continue

            for doc in scheme.documents:
                if doc.doc_id in merged_docs:
                    existing = merged_docs[doc.doc_id]
                    if scheme_id not in existing.required_for_schemes:
                        existing.required_for_schemes.append(scheme_id)
                else:
                    cloned = doc.model_copy(deep=True)
                    if scheme_id not in cloned.required_for_schemes:
                        cloned.required_for_schemes.append(scheme_id)
                    merged_docs[doc.doc_id] = cloned

        checklist = list(merged_docs.values())
        memory.document_checklist = checklist

        trace = AgentStepTrace(
            stage=self.stage,
            agent_name=self.agent_name,
            status="completed",
            memory_reads=["eligible_scheme_ids", "profile.language"],
            memory_writes=["document_checklist"],
            output_summary=(
                f"Compiled {len(checklist)} unique required documents covering "
                f"{len(memory.eligible_scheme_ids)} eligible schemes."
            ),
        )
        return memory, trace

