"""
SQLAlchemy Repository implementation for Government Welfare Schemes & RAG Chunks.
Implements ISchemeRepository following Repository and Dependency Inversion principles.
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from shared.data.seed_loader import upsert_scheme_orm
from shared.domain.models import (
    DocumentRequirement,
    EligibilityRuleGroup,
    SchemeDefinition,
)
from shared.infrastructure.database import DatabaseManager, SchemeChunkORM, SchemeORM
from shared.interfaces.repository_interface import ISchemeRepository


class SqlSchemeRepository(ISchemeRepository):
    """Database-backed repository managing schemes and their pre-embedded RAG chunks."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    @staticmethod
    def _to_domain(row: SchemeORM) -> SchemeDefinition:
        """Map SQLAlchemy SchemeORM row back to immutable domain SchemeDefinition DTO."""
        return SchemeDefinition(
            scheme_id=row.scheme_id,
            official_name=row.official_name,
            short_code=row.short_code,
            ministry=row.ministry,
            benefit_summary=row.benefit_summary,
            localized_summaries=row.localized_summaries or {},
            target_tags=row.target_tags or [],
            multilingual_keywords=row.multilingual_keywords or [],
            full_document_text=row.full_document_text,
            rules=EligibilityRuleGroup.model_validate(row.rules_json),
            documents=[DocumentRequirement.model_validate(d) for d in (row.documents_json or [])],
            application_steps=row.application_steps_json or [],
            localized_application_steps=row.localized_application_steps_json or {},
            official_portal=row.official_portal,
            helpline=row.helpline,
        )

    def list_schemes(self) -> list[SchemeDefinition]:
        """Load all government schemes ordered alphabetically by scheme_id."""
        with self._db.session_scope() as session:
            rows = session.scalars(select(SchemeORM).order_by(SchemeORM.scheme_id)).all()
            return [self._to_domain(r) for r in rows]

    def get_scheme(self, scheme_id: str) -> SchemeDefinition | None:
        """Fetch a single SchemeDefinition by ID."""
        with self._db.session_scope() as session:
            row = session.get(SchemeORM, scheme_id)
            return self._to_domain(row) if row else None

    def upsert_scheme(self, scheme: SchemeDefinition) -> SchemeDefinition:
        """Insert or update a scheme along with refreshed RAG chunks via shared mapper helper."""
        with self._db.session_scope() as session:
            upsert_scheme_orm(session, scheme)
        return scheme

    def list_chunks_with_schemes(self) -> list[tuple[SchemeChunkORM, SchemeDefinition]]:
        """Fetch all pre-embedded document chunks joined with their parent SchemeDefinition."""
        with self._db.session_scope() as session:
            stmt = select(SchemeChunkORM).options(selectinload(SchemeChunkORM.scheme))
            rows = session.scalars(stmt).all()
            return [(chunk, self._to_domain(chunk.scheme)) for chunk in rows]

