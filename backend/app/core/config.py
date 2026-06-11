"""Application settings, loaded from environment (.env).

Single source of truth for configuration across the backend. Other services
(worker, agents) import the relevant subset. See ``.env.example`` for the full
list of variables.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Core
    app_env: Literal["development", "staging", "production"] = "development"
    app_secret: str = "change-me"
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Data services
    database_url: str = "postgresql+psycopg://opp:opp@localhost:5432/opportunitypulse"
    redis_url: str = "redis://localhost:6379/0"

    # LLM provider (see agents/llm.py)
    llm_provider: Literal["anthropic", "openai", "ollama"] = "anthropic"
    llm_model: str = "claude-opus-4-8"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Embeddings / rerank
    embedding_provider: Literal["hashing", "local", "openai", "hosted"] = "hashing"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_enabled: bool = True
    rerank_latency_budget_ms: int = 300

    # Discovery / search
    search_provider: Literal["tavily", "serpapi"] = "tavily"
    tavily_api_key: str | None = None
    serpapi_api_key: str | None = None

    # Source credentials
    github_token: str | None = None
    kaggle_username: str | None = None
    kaggle_key: str | None = None

    # Crawler politeness
    crawler_user_agent: str = "OpportunityPulseBot/0.1 (+https://example.com/bot-info)"
    http_rate_limit_per_host: float = 1.0
    http_timeout_seconds: int = 20

    # Observability
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "opportunitypulse"
    prometheus_enabled: bool = True

    # Frontend origin(s) for CORS. Accepts a single origin or a comma-separated
    # list (e.g. a Vercel production URL plus preview URLs).
    web_origin: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """Parse ``web_origin`` into a normalized list of allowed CORS origins.

        Browsers send the ``Origin`` header with no trailing slash and
        Starlette's CORSMiddleware matches it by exact string, so a value like
        ``https://app.vercel.app/`` (trailing slash) or a comma-separated list
        would otherwise never match and the OPTIONS preflight would 400. This
        splits on commas, trims whitespace, and strips trailing slashes.
        """
        return [origin.strip().rstrip("/") for origin in self.web_origin.split(",") if origin.strip()]

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, v: str) -> str:
        """Coerce managed-Postgres URLs to the psycopg3 driver.

        Neon, Render, Supabase, Railway, etc. all hand out ``postgres://`` or
        ``postgresql://`` URLs. The app's SQLAlchemy engine uses the psycopg3
        driver, which requires the ``postgresql+psycopg://`` scheme. This rewrite
        is a no-op when the scheme is already correct (or for SQLite in tests).
        """
        if v.startswith("postgres://"):
            return "postgresql+psycopg://" + v[len("postgres://") :]
        if v.startswith("postgresql://"):
            return "postgresql+psycopg://" + v[len("postgresql://") :]
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (one instance per process)."""
    return Settings()
