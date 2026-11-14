"""
Centralized configuration settings loaded from environment variables.
Follows the Single Responsibility Principle (SRP) by isolating runtime
configuration from business logic and infrastructure wiring.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Typed application settings shared across all microservices."""

    # --- Service identity & execution mode ---
    service_name: str = "scheme-guide-service"
    # "microservice_http" routes inter-service calls via HTTP; "local_inproc" uses in-process adapters for tests
    orchestration_mode: str = "microservice_http"
    log_level: str = "INFO"

    # --- Relational + JSONB Database (PostgreSQL in Docker; SQLite default for local zero-infra runs) ---
    database_url: str = "sqlite:///./scheme_guide_local.db"

    # --- Redis Cache & Shared Working Memory ---
    redis_url: str = "redis://localhost:6379/0"
    redis_exact_ttl_seconds: int = 3600
    redis_semantic_ttl_seconds: int = 3600
    redis_rag_ttl_seconds: int = 1800
    redis_profile_ttl_seconds: int = 86400
    # Cosine similarity threshold above which a paraphrased query triggers a Redis semantic hit
    semantic_cache_threshold: float = 0.85

    # --- Downstream Microservice Base URLs ---
    profile_memory_service_url: str = "http://localhost:8001"
    rag_retrieval_service_url: str = "http://localhost:8002"
    agent_orchestrator_service_url: str = "http://localhost:8003"
    voice_speech_service_url: str = "http://localhost:8004"
    api_gateway_url: str = "http://localhost:8000"

    # --- LLM Backend Strategy Configuration ---
    # Supports: "deterministic", "openai", "gemini", "ollama"
    llm_provider: str = "deterministic"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # --- RAG Retrieval Hyperparameters ---
    rag_top_k: int = 10
    rag_min_score: float = 0.05

    # Allow reading overrides from .env file while ignoring unrelated env vars
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Cached singleton accessor for AppSettings.
    Returns the validated settings instance so every microservice reads consistent config.
    """
    return AppSettings()

