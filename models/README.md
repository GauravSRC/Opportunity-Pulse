# Models

Model cards, configs, and (later) training scripts. Model **ids** are selected
via environment variables (see `.env.example`) so every choice is swappable
without code changes.

## Defaults

| Role | Default model | Env var | Notes |
|---|---|---|---|
| Embeddings (bi-encoder) | `BAAI/bge-small-en-v1.5` (384-d) | `EMBEDDING_MODEL` | fast, strong; local sentence-transformers |
| Embeddings (alt) | `sentence-transformers/all-mpnet-base-v2` (768-d) | `EMBEDDING_MODEL` | higher quality, heavier; update `DEFAULT_EMBEDDING_DIM` |
| Reranker (cross-encoder) | `cross-encoder/ms-marco-MiniLM-L-6-v2` | `RERANKER_MODEL` | latency-gated second stage |
| Chat / drafting | `claude-opus-4-8` | `LLM_MODEL` (`LLM_PROVIDER=anthropic`) | outreach, query expansion, deadline LLM |
| Chat (local fallback) | `llama3.1` via Ollama | `OLLAMA_MODEL` | zero-cost offline path |
| NER (deadlines) | spaCy `en_core_web_sm` | — | install separately: `python -m spacy download en_core_web_sm` |

## Notes

- Changing the embedding model changes vector dimensionality — update
  `DEFAULT_EMBEDDING_DIM` in `backend/app/models/embedding.py` and re-embed (a
  migration/backfill is required).
- `models/cache/` (gitignored) holds downloaded weights.
- Decay/urgency and feedback-ranking models are trained from harvested labels;
  training scripts land in Phase 3/6 under this directory.
