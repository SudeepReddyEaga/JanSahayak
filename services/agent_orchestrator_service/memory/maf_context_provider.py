"""
Microsoft Agent Framework ContextProvider bridging every specialized agent
to the shared User-Profile Memory microservice (PostgreSQL + Redis).
Guarantees every agent reads the latest profile context before execution and
writes a traceable audit entry after execution.
"""

from typing import Any

from agent_framework import AgentSession, ContextProvider, SessionContext, SupportsAgentRun

from shared.domain.models import AgentMemoryAuditEntry, UserProfileMemory
from services.agent_orchestrator_service.clients.profile_client import IProfileMemoryClient


class SharedProfileMemoryContextProvider(ContextProvider):
    """
    Adapter implementing Microsoft Agent Framework's ContextProvider lifecycle hooks
    (`before_run` and `after_run`) backed by IProfileMemoryClient.
    """

    def __init__(
        self,
        memory_client: IProfileMemoryClient,
        *,
        shared_session_id: str,
        source_id: str = "user_profile_memory_provider",
    ) -> None:
        super().__init__(source_id=source_id)
        self._client = memory_client
        self._shared_session_id = shared_session_id
        # Ephemeral reference updated during pipeline turns to avoid extra network round-trips when unneeded
        self.latest_memory: UserProfileMemory | None = None

    async def load_memory(self) -> UserProfileMemory:
        """Fetch the authoritative UserProfileMemory from profile-memory-service."""
        self.latest_memory = await self._client.get_or_create_memory(self._shared_session_id)
        return self.latest_memory

    async def persist_memory(self, memory: UserProfileMemory) -> UserProfileMemory:
        """Write modified UserProfileMemory back to profile-memory-service."""
        self.latest_memory = await self._client.save_memory(memory)
        return self.latest_memory

    async def before_run(
        self,
        *,
        agent: SupportsAgentRun,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        MAF Hook executed prior to agent model/logic invocation:
        Reads shared UserProfileMemory, injects profile summary into SessionContext
        instructions, and appends a 'read' audit log entry.
        """
        memory = await self.load_memory()
        profile_summary = memory.profile.model_dump(exclude_none=True)
        context.extend_instructions(
            self.source_id,
            (
                f"[SharedUserProfileMemory session={self._shared_session_id}] "
                f"Language={memory.profile.language.value} | "
                f"Profile={profile_summary} | "
                f"RetrievedSchemes={memory.retrieved_scheme_ids} | "
                f"EligibleSchemes={memory.eligible_scheme_ids}"
            ),
        )
        # Store active snapshot inside provider state dict for downstream inspection
        state["session_id"] = self._shared_session_id
        state["profile"] = profile_summary

        agent_label = agent.name or agent.id
        memory.audit_log.append(
            AgentMemoryAuditEntry(
                agent=agent_label,
                action="read",
                fields_accessed=list(profile_summary.keys()) or ["profile"],
                summary=f"{agent_label} read shared UserProfileMemory prior to step execution.",
            )
        )
        await self.persist_memory(memory)

    async def after_run(
        self,
        *,
        agent: SupportsAgentRun,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        MAF Hook executed immediately after agent completes:
        Logs completion context back to shared memory state.
        """
        if self.latest_memory is None:
            return
        agent_label = agent.name or agent.id
        state["last_completed_agent"] = agent_label

