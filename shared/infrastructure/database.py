"""
Database Schema & Connection Manager (SQLAlchemy 2.0).
Supports PostgreSQL in multi-container Docker deployments and SQLite for lightweight
local execution or automated unit testing, preserving identical ORM semantics.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import time
from typing import Iterator

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from shared.config.settings import get_settings


def _utc_now() -> datetime:
    """Return timezone-aware UTC timestamp for ORM default values."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 Declarative Base shared by all relational ORM entities."""


class SchemeORM(Base):
    """
    Canonical Government Welfare Scheme table storing policy metadata,
    structured deterministic eligibility rules (JSON), documents, and steps.
    """

    __tablename__ = "schemes"

    # Primary scheme code (e.g., "PM-KISAN")
    scheme_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    official_name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_code: Mapped[str] = mapped_column(String(64), nullable=False)
    ministry: Mapped[str] = mapped_column(String(255), nullable=False)
    benefit_summary: Mapped[str] = mapped_column(Text, nullable=False)
    # Map of language code -> localized summary text
    localized_summaries: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    target_tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    multilingual_keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    full_document_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Declarative EligibilityRuleGroup JSON consumed by EligibilityRuleAgent
    rules_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    documents_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    application_steps_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    localized_application_steps_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    official_portal: Mapped[str] = mapped_column(String(255), nullable=False)
    helpline: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now)

    # One-to-Many relationship with RAG document chunks (cascade deletes orphan chunks)
    chunks: Mapped[list["SchemeChunkORM"]] = relationship(
        back_populates="scheme",
        cascade="all, delete-orphan",
    )


class SchemeChunkORM(Base):
    """Chunked scheme knowledge segments with precomputed vector embeddings for RAG retrieval."""

    __tablename__ = "scheme_chunks"

    chunk_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    scheme_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("schemes.scheme_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Dense float embedding vector serialized as JSON array for portability across Postgres/SQLite
    embedding_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    scheme: Mapped[SchemeORM] = relationship(back_populates="chunks")


class CitizenSessionORM(Base):
    """
    Shared User-Profile Memory persistence table.
    Every specialized agent reads from and writes to the session's memory snapshot.
    """

    __tablename__ = "citizen_sessions"

    session_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    citizen_id: Mapped[str] = mapped_column(String(128), default="anonymous", index=True)
    detected_language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    profile_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    memory_snapshot_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now)

    audit_logs: Mapped[list["AgentAuditLogORM"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class AgentAuditLogORM(Base):
    """Fine-grained audit log recording every read and write operation performed by each agent."""

    __tablename__ = "agent_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("citizen_sessions.session_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    agent_name: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)  # "read" or "write"
    fields_accessed_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)

    session: Mapped[CitizenSessionORM] = relationship(back_populates="audit_logs")


class EvaluationRunORM(Base):
    """Stores historical 10-profile benchmark runs with precision, recall, and consistency metrics."""

    __tablename__ = "evaluation_runs"

    run_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    total_profiles: Mapped[int] = mapped_column(Integer, nullable=False)
    macro_precision: Mapped[float] = mapped_column(Float, nullable=False)
    macro_recall: Mapped[float] = mapped_column(Float, nullable=False)
    macro_f1: Mapped[float] = mapped_column(Float, nullable=False)
    micro_precision: Mapped[float] = mapped_column(Float, nullable=False)
    micro_recall: Mapped[float] = mapped_column(Float, nullable=False)
    micro_f1: Mapped[float] = mapped_column(Float, nullable=False)
    exact_match_rate: Mapped[float] = mapped_column(Float, nullable=False)
    grounding_pass_rate: Mapped[float] = mapped_column(Float, nullable=False)
    language_consistency_rate: Mapped[float] = mapped_column(Float, nullable=False)
    scheme_name_preservation_rate: Mapped[float] = mapped_column(Float, nullable=False)
    avg_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    summary_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class QueryCacheAuditORM(Base):
    """Tracks Redis cache hit/miss telemetry and latency improvements for observability."""

    __tablename__ = "query_cache_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    cache_status: Mapped[str] = mapped_column(String(32), nullable=False)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)


class DatabaseManager:
    """
    Factory & Unit-of-Work manager encapsulating SQLAlchemy engine creation,
    schema initialization, and transactional session context management.
    """

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        # SQLite requires check_same_thread=False and generous busy timeout for multi-service concurrency
        connect_args = (
            {"check_same_thread": False, "timeout": 30.0}
            if database_url.startswith("sqlite")
            else {}
        )
        self.engine = create_engine(
            database_url,
            connect_args=connect_args,
            pool_pre_ping=True,
            future=True,
        )
        # Enable Write-Ahead Logging (WAL) on SQLite so concurrent microservices never contend on locks
        if database_url.startswith("sqlite"):
            @event.listens_for(self.engine, "connect")
            def _configure_sqlite_pragma(dbapi_conn, _connection_record) -> None:
                cursor = dbapi_conn.cursor()
                try:
                    cursor.execute("PRAGMA busy_timeout=30000;")
                    cursor.execute("PRAGMA journal_mode=WAL;")
                except Exception:
                    pass
                finally:
                    cursor.close()

        self._session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    def create_tables(self) -> None:
        """Idempotently create all database tables with brief retry for concurrent startup."""
        for attempt in range(5):
            try:
                Base.metadata.create_all(bind=self.engine, checkfirst=True)
                return
            except OperationalError:
                if attempt == 4:
                    raise
                time.sleep(0.3 * (attempt + 1))

    def dispose(self) -> None:
        """Release all pooled database connections cleanly on shutdown."""
        self.engine.dispose()

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """
        Provide a transactional unit-of-work session that automatically commits
        on clean exit and rolls back on any raised exception.
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Module-level cache of DatabaseManagers keyed by connection URL so tests with distinct URLs stay isolated
_DB_MANAGERS: dict[str, DatabaseManager] = {}


def get_db_manager(database_url: str | None = None) -> DatabaseManager:
    """Return (and initialize tables for) a DatabaseManager bound to database_url."""
    url = database_url or get_settings().database_url
    if url not in _DB_MANAGERS:
        manager = DatabaseManager(url)
        manager.create_tables()
        _DB_MANAGERS[url] = manager
    return _DB_MANAGERS[url]
