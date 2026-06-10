"""Provider-agnostic LLM + embedding interface.

A thin abstraction over Claude (default), OpenAI, and Ollama (local fallback)
so the rest of the codebase never imports a vendor SDK directly. Selected via
``LLM_PROVIDER`` / ``EMBEDDING_PROVIDER`` env (see app.core.config).

This is the ONE place LangChain-style provider glue is allowed; everything else
calls ``complete()`` / ``embed()``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Chat/completion provider."""

    @abstractmethod
    def complete(self, prompt: str, *, system: str | None = None, **kw) -> str:
        """Return a text completion. TODO(phase-4): streaming + tool use."""
        raise NotImplementedError


class Embedder(ABC):
    """Embedding provider."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


# --- Concrete providers (Phase-1/4 stubs) ---------------------------------


class AnthropicClient(LLMClient):
    def complete(self, prompt: str, *, system: str | None = None, **kw) -> str:
        # TODO(phase-4): call anthropic SDK with settings.llm_model.
        raise NotImplementedError("AnthropicClient.complete")


class OpenAIClient(LLMClient):
    def complete(self, prompt: str, *, system: str | None = None, **kw) -> str:
        # TODO(phase-4): call openai SDK.
        raise NotImplementedError("OpenAIClient.complete")


class OllamaClient(LLMClient):
    def complete(self, prompt: str, *, system: str | None = None, **kw) -> str:
        # TODO(phase-4): call local Ollama HTTP API (zero-cost fallback).
        raise NotImplementedError("OllamaClient.complete")


class LocalEmbedder(Embedder):
    """sentence-transformers embedder (default)."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        # TODO(phase-1): lazy-load SentenceTransformer(settings.embedding_model).
        raise NotImplementedError("LocalEmbedder.embed")


# --- Factories -------------------------------------------------------------


def get_llm() -> LLMClient:
    """Return the configured chat provider. TODO(phase-4): read settings."""
    raise NotImplementedError("get_llm")


def get_embedder() -> Embedder:
    """Return the configured embedder. TODO(phase-1): read settings."""
    raise NotImplementedError("get_embedder")
