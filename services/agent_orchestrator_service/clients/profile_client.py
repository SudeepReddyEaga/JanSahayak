"""
Profile Memory Microservice Client Adapter (Adapter + Dependency Inversion Pattern).
Defines an abstract IProfileMemoryClient contract with two concrete adapters:
  - HttpProfileMemoryClient: communicates over HTTP with profile-memory-service (Port 8001)
  - LocalProfileMemoryClient: invokes ProfileMemoryService directly for zero-network unit tests
"""

from abc import ABC, abstractmethod

from shared.domain.exceptions import MicroserviceUnavailableError
from shared.domain.models import (
    AgentMemoryAuditEntry,
    EvaluationSummary,
    UserProfileMemory,
)
from shared.infrastructure.http_client import LoopAwareAsyncHttpPool
from services.profile_memory_service.service import ProfileMemoryService


class IProfileMemoryClient(ABC):
    """Abstract gateway used by all agents to read & write shared UserProfileMemory."""

    @abstractmethod
    async def get_or_create_memory(self, session_id: str) -> UserProfileMemory:
        """Fetch existing session memory or create a blank one."""

    @abstractmethod
    async def save_memory(self, memory: UserProfileMemory) -> UserProfileMemory:
        """Persist updated shared UserProfileMemory back to the profile memory service."""

    @abstractmethod
    async def append_audit(self, session_id: str, entry: AgentMemoryAuditEntry) -> UserProfileMemory:
        """Append an agent read/write audit event."""

    @abstractmethod
    async def save_evaluation(self, summary: EvaluationSummary) -> EvaluationSummary:
        """Persist 10-profile evaluation run metrics."""

    @abstractmethod
    async def list_evaluations(self, limit: int = 10) -> list[EvaluationSummary]:
        """List stored evaluation runs."""


class HttpProfileMemoryClient(IProfileMemoryClient):
    """Asynchronous HTTP client talking to the standalone profile-memory-service container."""

    def __init__(self, base_url: str, timeout_seconds: float = 15.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._pool = LoopAwareAsyncHttpPool(timeout_seconds=timeout_seconds)

    async def get_or_create_memory(self, session_id: str) -> UserProfileMemory:
        """Send GET /profiles/{session_id} to profile-memory-service."""
        try:
            client = self._pool.get_client()
            resp = await client.get(f"{self._base_url}/profiles/{session_id}")
            resp.raise_for_status()
            return UserProfileMemory.model_validate(resp.json())
        except Exception as exc:
            raise MicroserviceUnavailableError("profile-memory-service", str(exc)) from exc

    async def save_memory(self, memory: UserProfileMemory) -> UserProfileMemory:
        """Send PUT /profiles/{session_id} to persist agent memory updates."""
        try:
            client = self._pool.get_client()
            resp = await client.put(
                f"{self._base_url}/profiles/{memory.session_id}",
                json=memory.model_dump(),
            )
            resp.raise_for_status()
            return UserProfileMemory.model_validate(resp.json())
        except Exception as exc:
            raise MicroserviceUnavailableError("profile-memory-service", str(exc)) from exc

    async def append_audit(self, session_id: str, entry: AgentMemoryAuditEntry) -> UserProfileMemory:
        """Send POST /profiles/{session_id}/audit to record memory access."""
        try:
            client = self._pool.get_client()
            resp = await client.post(
                f"{self._base_url}/profiles/{session_id}/audit",
                json=entry.model_dump(),
            )
            resp.raise_for_status()
            return UserProfileMemory.model_validate(resp.json())
        except Exception as exc:
            raise MicroserviceUnavailableError("profile-memory-service", str(exc)) from exc

    async def save_evaluation(self, summary: EvaluationSummary) -> EvaluationSummary:
        """Send POST /evaluations to persist benchmark summary."""
        try:
            client = self._pool.get_client()
            resp = await client.post(
                f"{self._base_url}/evaluations",
                json=summary.model_dump(),
            )
            resp.raise_for_status()
            return EvaluationSummary.model_validate(resp.json())
        except Exception as exc:
            raise MicroserviceUnavailableError("profile-memory-service", str(exc)) from exc

    async def list_evaluations(self, limit: int = 10) -> list[EvaluationSummary]:
        """Send GET /evaluations to retrieve benchmark history."""
        try:
            client = self._pool.get_client()
            resp = await client.get(f"{self._base_url}/evaluations", params={"limit": limit})
            resp.raise_for_status()
            return [EvaluationSummary.model_validate(item) for item in resp.json()]
        except Exception as exc:
            raise MicroserviceUnavailableError("profile-memory-service", str(exc)) from exc


class LocalProfileMemoryClient(IProfileMemoryClient):
    """In-process adapter wrapping ProfileMemoryService directly for standalone/test runs."""

    def __init__(self, service: ProfileMemoryService) -> None:
        self._service = service

    async def get_or_create_memory(self, session_id: str) -> UserProfileMemory:
        return self._service.get_or_create_memory(session_id)

    async def save_memory(self, memory: UserProfileMemory) -> UserProfileMemory:
        return self._service.save_memory(memory)

    async def append_audit(self, session_id: str, entry: AgentMemoryAuditEntry) -> UserProfileMemory:
        return self._service.record_agent_access(session_id, entry)

    async def save_evaluation(self, summary: EvaluationSummary) -> EvaluationSummary:
        return self._service.save_evaluation_run(summary)

    async def list_evaluations(self, limit: int = 10) -> list[EvaluationSummary]:
        return self._service.list_evaluation_runs(limit=limit)

