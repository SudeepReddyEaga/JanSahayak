"""
Template-Method Base Class bridging Microsoft Agent Framework (`BaseAgent`, `Agent`,
`SupportsAgentRun`, `ResponseStream`) with Shared User-Profile Memory and Step Telemetry.
Every specialized agent subclasses SpecializedPipelineAgent to guarantee uniform
memory read/write auditing, MAF runtime participation, and clean LLD separation.
"""

from abc import abstractmethod
from collections.abc import AsyncIterable, Mapping, Sequence
import time
from typing import Any

from agent_framework import (
    Agent,
    AgentResponse,
    AgentResponseUpdate,
    AgentSession,
    BaseAgent,
    Message,
    ResponseStream,
    SupportsChatGetResponse,
    ToolTypes,
)

from shared.domain.enums import AgentStage
from shared.domain.models import (
    AgentMemoryAuditEntry,
    AgentStepTrace,
    UserProfileMemory,
)
from shared.interfaces.agent_interface import ISpecializedAgent
from services.agent_orchestrator_service.memory.maf_context_provider import (
    SharedProfileMemoryContextProvider,
)


class SpecializedPipelineAgent(BaseAgent, ISpecializedAgent):
    """
    Base class implementing Microsoft Agent Framework's `SupportsAgentRun` protocol
    while delegating domain processing to concrete `execute_step()` subclasses.
    """

    stage: AgentStage
    agent_name: str

    def __init__(
        self,
        *,
        stage: AgentStage,
        agent_name: str,
        description: str,
        instructions: str,
        chat_client: SupportsChatGetResponse[Any],
        memory_provider: SharedProfileMemoryContextProvider,
        trace_collector: list[AgentStepTrace],
        tools: Sequence[ToolTypes | Any] | None = None,
    ) -> None:
        super().__init__(
            id=stage.value,
            name=agent_name,
            description=description,
            context_providers=[memory_provider],
        )
        self.stage = stage
        self.agent_name = agent_name
        self._memory_provider = memory_provider
        self._trace_collector = trace_collector
        self._maf_session = AgentSession(session_id=memory_provider._shared_session_id)
        # Inner MAF Agent handles ContextProvider hooks, ChatClient invocation, and @tool binding
        self._maf_agent = Agent(
            client=chat_client,
            id=f"{stage.value}-maf",
            name=agent_name,
            description=description,
            instructions=instructions,
            tools=list(tools) if tools else None,
            context_providers=[memory_provider],
        )

    @abstractmethod
    async def execute_step(self, memory: UserProfileMemory) -> tuple[UserProfileMemory, AgentStepTrace]:
        """Concrete subclass implements its single-responsibility domain logic here."""

    async def _run_pipeline_turn(self, incoming_text: str) -> AgentResponse:
        """
        Execute the full Template Method workflow for this pipeline stage:
          1. Run MAF inner Agent (triggers SharedProfileMemoryContextProvider.before_run -> 'read')
          2. Execute concrete domain logic via `execute_step(memory)`
          3. Append 'write' audit entry and persist updated UserProfileMemory
          4. Collect AgentStepTrace and emit MAF AgentResponse downstream
        """
        started = time.perf_counter()

        # Step 1: Invoke MAF Agent so ContextProvider reads shared memory & engages ChatClient
        await self._maf_agent.run(
            f"[{self.agent_name}] Stage={self.stage.value} | Input={incoming_text[:200]}",
            session=self._maf_session,
        )

        # Step 2: Load freshly audited memory snapshot and execute concrete agent logic
        memory = await self._memory_provider.load_memory()
        updated_memory, trace = await self.execute_step(memory)

        # Step 3: Record explicit write audit entry and persist back to PostgreSQL + Redis
        elapsed_ms = round((time.perf_counter() - started) * 1000.0, 2)
        trace.duration_ms = elapsed_ms
        if not trace.memory_reads:
            trace.memory_reads = ["citizen_profile"]
        updated_memory.audit_log.append(
            AgentMemoryAuditEntry(
                agent=self.agent_name,
                action="write",
                fields_accessed=trace.memory_writes,
                summary=trace.output_summary,
            )
        )
        await self._memory_provider.persist_memory(updated_memory)

        # Step 4: Append structured trace and return MAF AgentResponse to SequentialBuilder
        self._trace_collector.append(trace)
        return AgentResponse(
            messages=[
                Message(
                    role="assistant",
                    contents=[f"[{self.agent_name}] {trace.output_summary}"],
                )
            ],
            response_id=f"{self.stage.value}-{len(self._trace_collector)}",
        )

    def run(
        self,
        messages: Any = None,
        *,
        stream: bool = False,
        session: AgentSession | None = None,
        function_invocation_kwargs: Mapping[str, Any] | None = None,
        client_kwargs: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ):
        """
        Microsoft Agent Framework `SupportsAgentRun.run` entry point invoked by
        SequentialBuilder's AgentExecutor in both buffered and streaming modes.
        """
        # Extract readable text from incoming str, Message, or list[Message]
        incoming_text = ""
        if isinstance(messages, str):
            incoming_text = messages
        elif isinstance(messages, Message):
            incoming_text = messages.text
        elif isinstance(messages, Sequence) and messages:
            last = messages[-1]
            incoming_text = last.text if isinstance(last, Message) else str(last)

        if stream:
            async def _stream_updates() -> AsyncIterable[AgentResponseUpdate]:
                final_resp = await self._run_pipeline_turn(incoming_text)
                yield AgentResponseUpdate(
                    role="assistant",
                    contents=[{"type": "text", "text": final_resp.text}],
                    response_id=final_resp.response_id,
                )

            return ResponseStream(
                _stream_updates(),
                finalizer=lambda updates: AgentResponse(
                    messages=[Message(role="assistant", contents=[updates[-1].text if updates else ""])]
                ),
            )

        return self._run_pipeline_turn(incoming_text)

