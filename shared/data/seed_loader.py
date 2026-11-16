"""
Idempotent Database Seeder & Canonical Scheme ORM Mapper.
Provides a single shared helper (`upsert_scheme_orm`) used by both initial startup
seeding and runtime RAG ingestion to avoid duplicating ORM mapping and chunk generation logic.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.data.schemes_catalog import SCHEMES_CATALOG
from shared.domain.models import SchemeDefinition
from shared.infrastructure.database import DatabaseManager, SchemeChunkORM, SchemeORM
from shared.infrastructure.logging_utils import get_logger
from shared.infrastructure.redis_cache import _compute_trigram_vector

logger = get_logger("seed-loader")


def build_scheme_chunks(scheme: SchemeDefinition) -> list[tuple[str, int, str]]:
    """
    Split a SchemeDefinition into deterministic, semantically dense RAG chunks:
      - Chunk 0: Official identity, policy summary, eligibility prose, and multilingual keywords.
      - Chunk 1: Official application steps and citizen portal workflow guidance.
    """
    keywords_csv = ", ".join(scheme.multilingual_keywords)
    chunk_0 = f"{scheme.official_name} [{scheme.scheme_id}]. {scheme.full_document_text} Keywords: {keywords_csv}."
    chunk_1 = f"{scheme.official_name} [{scheme.scheme_id}] Application Steps: " + " ".join(scheme.application_steps)
    return [
        (f"{scheme.scheme_id}::chunk_0", 0, chunk_0),
        (f"{scheme.scheme_id}::chunk_1", 1, chunk_1),
    ]


def upsert_scheme_orm(session: Session, scheme: SchemeDefinition) -> SchemeORM:
    """
    Insert or update a SchemeORM row and rebuild its pre-embedded SchemeChunkORM rows.
    Reused by both seed_database_if_empty() and SqlSchemeRepository.upsert_scheme() (DRY).
    """
    orm_obj = session.get(SchemeORM, scheme.scheme_id)
    if orm_obj is None:
        orm_obj = SchemeORM(scheme_id=scheme.scheme_id)
        session.add(orm_obj)

    # Copy canonical policy attributes into relational columns
    orm_obj.official_name = scheme.official_name
    orm_obj.short_code = scheme.short_code
    orm_obj.ministry = scheme.ministry
    orm_obj.benefit_summary = scheme.benefit_summary
    orm_obj.localized_summaries = scheme.localized_summaries
    orm_obj.target_tags = scheme.target_tags
    orm_obj.multilingual_keywords = scheme.multilingual_keywords
    orm_obj.full_document_text = scheme.full_document_text
    orm_obj.rules_json = scheme.rules.model_dump()
    orm_obj.documents_json = [doc.model_dump() for doc in scheme.documents]
    orm_obj.application_steps_json = scheme.application_steps
    orm_obj.localized_application_steps_json = scheme.localized_application_steps
    orm_obj.official_portal = scheme.official_portal
    orm_obj.helpline = scheme.helpline

    # Refresh child RAG chunks and precompute 256-dim trigram+token embeddings
    orm_obj.chunks.clear()
    for chunk_id, chunk_idx, chunk_text in build_scheme_chunks(scheme):
        orm_obj.chunks.append(
            SchemeChunkORM(
                chunk_id=chunk_id,
                scheme_id=scheme.scheme_id,
                chunk_index=chunk_idx,
                chunk_text=chunk_text,
                embedding_json=_compute_trigram_vector(chunk_text),
            )
        )
    return orm_obj


def seed_database_if_empty(db_manager: DatabaseManager, *, force_refresh: bool = False) -> int:
    """
    Idempotently seed all 17 Government Welfare Schemes and RAG chunks into the database.
    Skips unnecessary rewrites only when all catalog schemes AND all current language
    localizations are already present unless force_refresh=True.
    """
    db_manager.create_tables()
    expected_langs = set(SCHEMES_CATALOG[0].localized_summaries.keys()) if SCHEMES_CATALOG else set()
    with db_manager.session_scope() as session:
        existing_rows = session.scalars(select(SchemeORM)).all()
        existing_ids = {r.scheme_id for r in existing_rows}
        has_all_langs = bool(existing_rows) and all(
            expected_langs.issubset(set((r.localized_summaries or {}).keys()))
            for r in existing_rows
        )
        if existing_ids and not force_refresh and len(existing_ids) >= len(SCHEMES_CATALOG) and has_all_langs:
            return len(existing_ids)

        for scheme in SCHEMES_CATALOG:
            upsert_scheme_orm(session, scheme)

        logger.info(f"Seeded {len(SCHEMES_CATALOG)} government welfare schemes & RAG chunks into database.")
        return len(SCHEMES_CATALOG)
