"""
SQLAlchemy Repository implementations for Profile Memory & Evaluation runs.
Follows Repository Pattern & Dependency Inversion Principle by implementing
IProfileMemoryRepository and IEvaluationRepository.
"""

from sqlalchemy import desc, select

from shared.domain.models import (
    AgentMemoryAuditEntry,
    CitizenProfile,
    EvaluationSummary,
    UserProfileMemory,
)
from shared.infrastructure.database import (
    AgentAuditLogORM,
    CitizenSessionORM,
    DatabaseManager,
    EvaluationRunORM,
)
from shared.interfaces.repository_interface import (
    IEvaluationRepository,
    IProfileMemoryRepository,
)


class SqlProfileMemoryRepository(IProfileMemoryRepository):
    """Relational DB repository persisting CitizenSessionORM and AgentAuditLogORM rows."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def get_memory(self, session_id: str) -> UserProfileMemory | None:
        """Load complete UserProfileMemory snapshot for session_id from PostgreSQL/SQLite."""
        with self._db.session_scope() as session:
            row = session.get(CitizenSessionORM, session_id)
            if row is None:
                return None
            # Rehydrate Pydantic DTO from stored JSON snapshot
            return UserProfileMemory.model_validate(row.memory_snapshot_json)

    def upsert_memory(self, memory: UserProfileMemory) -> UserProfileMemory:
        """
        Insert or update citizen session profile and full shared memory snapshot,
        also synchronizing the normalized agent audit log table.
        """
        with self._db.session_scope() as session:
            row = session.get(CitizenSessionORM, memory.session_id)
            if row is None:
                row = CitizenSessionORM(session_id=memory.session_id)
                session.add(row)

            row.citizen_id = memory.citizen_id
            row.detected_language = memory.profile.language.value
            row.profile_json = memory.profile.model_dump()
            row.memory_snapshot_json = memory.model_dump()

            # Replace audit log rows with current ordered entries to guarantee exact consistency
            row.audit_logs.clear()
            for entry in memory.audit_log:
                row.audit_logs.append(
                    AgentAuditLogORM(
                        session_id=memory.session_id,
                        agent_name=entry.agent,
                        action=entry.action,
                        fields_accessed_json=entry.fields_accessed,
                        summary=entry.summary,
                        timestamp=entry.timestamp,
                    )
                )
        return memory

    def append_audit_entry(self, session_id: str, entry: AgentMemoryAuditEntry) -> UserProfileMemory:
        """Append a single agent read/write audit entry atomically to an existing or fresh session."""
        existing = self.get_memory(session_id)
        if existing is None:
            existing = UserProfileMemory(session_id=session_id, profile=CitizenProfile())
        existing.audit_log.append(entry)
        return self.upsert_memory(existing)

    def list_sessions(self, limit: int = 20) -> list[UserProfileMemory]:
        """Return recent citizen profile memory sessions sorted newest-first."""
        with self._db.session_scope() as session:
            stmt = (
                select(CitizenSessionORM)
                .order_by(desc(CitizenSessionORM.updated_at))
                .limit(limit)
            )
            rows = session.scalars(stmt).all()
            return [UserProfileMemory.model_validate(r.memory_snapshot_json) for r in rows]


class SqlEvaluationRepository(IEvaluationRepository):
    """Relational repository persisting 10-profile precision/recall evaluation summaries."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def save_evaluation(self, summary: EvaluationSummary) -> EvaluationSummary:
        """Persist benchmark evaluation summary and per-profile breakdown JSON."""
        with self._db.session_scope() as session:
            row = session.get(EvaluationRunORM, summary.run_id)
            if row is None:
                row = EvaluationRunORM(run_id=summary.run_id)
                session.add(row)

            row.timestamp = summary.timestamp
            row.total_profiles = summary.total_profiles
            row.macro_precision = summary.macro_precision
            row.macro_recall = summary.macro_recall
            row.macro_f1 = summary.macro_f1
            row.micro_precision = summary.micro_precision
            row.micro_recall = summary.micro_recall
            row.micro_f1 = summary.micro_f1
            row.exact_match_rate = summary.exact_match_rate
            row.grounding_pass_rate = summary.grounding_pass_rate
            row.language_consistency_rate = summary.language_consistency_rate
            row.scheme_name_preservation_rate = summary.scheme_name_preservation_rate
            row.avg_latency_ms = summary.avg_latency_ms
            row.summary_json = summary.model_dump()
        return summary

    def list_evaluations(self, limit: int = 10) -> list[EvaluationSummary]:
        """Fetch latest stored benchmark evaluation summaries."""
        with self._db.session_scope() as session:
            stmt = select(EvaluationRunORM).order_by(desc(EvaluationRunORM.timestamp)).limit(limit)
            rows = session.scalars(stmt).all()
            return [EvaluationSummary.model_validate(r.summary_json) for r in rows]

