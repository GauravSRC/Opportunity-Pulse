"""Provider-agnostic LLM + embedding interface.

A thin abstraction over embedding/chat providers so the rest of the codebase
never imports a vendor SDK directly. Selected via ``EMBEDDING_PROVIDER`` /
``LLM_PROVIDER`` env (see app.core.config).

Design notes:
- The default embedder is a deterministic, dependency-free **feature-hashing**
  embedder. It needs no model download and gives stable lexical-overlap
  similarity — enough for a reproducible demo and for tests. Setting
  ``EMBEDDING_PROVIDER=local`` upgrades to sentence-transformers (semantic, but
  pulls torch); if that import fails we log and fall back to hashing so the app
  never hard-crashes on a missing optional dependency.
- The chat layer is OPTIONAL for the MVP: outreach drafting and deadline parsing
  both have deterministic fallbacks and only *enhance* with an LLM when one is
  configured and reachable.
"""

from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod
from functools import lru_cache

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.types import DEFAULT_EMBEDDING_DIM

log = get_logger(__name__)
_TOKEN_RE = re.compile(r"[a-z0-9]+")


# --------------------------------------------------------------------------- #
# Embedding providers
# --------------------------------------------------------------------------- #
class Embedder(ABC):
    dim: int = DEFAULT_EMBEDDING_DIM
    name: str = "abstract"

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


class HashingEmbedder(Embedder):
    """Deterministic feature-hashing embedder (no external model).

    Hashes word tokens and character trigrams into a fixed-dim vector with
    signed buckets, then L2-normalizes. Similar texts (shared vocabulary) land
    close in cosine space. Stable across processes and machines.
    """

    name = "hashing-v1"

    def __init__(self, dim: int = DEFAULT_EMBEDDING_DIM) -> None:
        self.dim = dim

    @staticmethod
    def _features(text: str):
        tokens = _TOKEN_RE.findall((text or "").lower())
        for tok in tokens:
            yield tok, 1.0
        # character trigrams add some sub-word robustness (typos, morphology)
        joined = " ".join(tokens)
        for i in range(len(joined) - 2):
            yield "_" + joined[i : i + 3], 0.5

    def _bucket(self, feature: str) -> tuple[int, float]:
        h = hashlib.md5(feature.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "big") % self.dim
        sign = 1.0 if (h[4] & 1) else -1.0
        return idx, sign

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            vec = [0.0] * self.dim
            for feature, weight in self._features(text):
                idx, sign = self._bucket(feature)
                vec[idx] += sign * weight
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            out.append([v / norm for v in vec])
        return out


class SentenceTransformerEmbedder(Embedder):
    """sentence-transformers embedder (semantic; production option)."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer  # lazy, heavy

        self._model = SentenceTransformer(model_name)
        self.name = model_name
        self.dim = self._model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str]) -> list[list[float]]:
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vecs]


@lru_cache(maxsize=4)
def get_embedder() -> Embedder:
    """Return the configured embedder (cached per process)."""
    settings = get_settings()
    provider = settings.embedding_provider
    if provider == "local":
        try:
            return SentenceTransformerEmbedder(settings.embedding_model)
        except Exception as exc:  # missing torch / offline / download failure
            log.warning("embedder.fallback", reason=str(exc), provider="local->hashing")
            return HashingEmbedder()
    # "hashing" (and any unknown value) -> deterministic, dependency-free default
    return HashingEmbedder()


# --------------------------------------------------------------------------- #
# Chat providers (optional enhancement)
# --------------------------------------------------------------------------- #
class LLMUnavailable(RuntimeError):
    """Raised when no chat provider is configured/reachable. Callers fall back."""


class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 800) -> str:
        raise NotImplementedError


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, model: str) -> None:
        import anthropic  # lazy

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 800) -> str:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str) -> None:
        import openai  # lazy

        self._client = openai.OpenAI(api_key=api_key)
        self._model = model

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 800) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[
                *([{"role": "system", "content": system}] if system else []),
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""


def get_llm() -> LLMClient:
    """Return the configured chat client, or raise LLMUnavailable.

    Callers MUST catch LLMUnavailable (and provider errors) and fall back to a
    deterministic path — the product never hard-depends on an LLM.
    """
    settings = get_settings()
    try:
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            return AnthropicClient(settings.anthropic_api_key, settings.llm_model)
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return OpenAIClient(settings.openai_api_key, settings.llm_model)
    except Exception as exc:  # SDK missing, bad key, etc.
        raise LLMUnavailable(str(exc)) from exc
    raise LLMUnavailable(f"no chat provider configured for {settings.llm_provider}")
