"""Source adapters. Register new adapters in ../registry.yaml and ADAPTERS below."""

from __future__ import annotations

# Map of source key -> adapter import path, mirrored in registry.yaml.
# TODO(phase-1+): import and register adapters as they are implemented.
ADAPTERS: dict[str, str] = {
    "greenhouse": "ingestion.sources.greenhouse:GreenhouseAdapter",
    "lever": "ingestion.sources.lever:LeverAdapter",
    "github": "ingestion.sources.github:GitHubAdapter",
    "kaggle": "ingestion.sources.kaggle:KaggleAdapter",
    "arxiv": "ingestion.sources.arxiv:ArxivAdapter",
    "rss_generic": "ingestion.sources.rss_generic:RssGenericAdapter",
    "search_tavily": "ingestion.sources.search_tavily:TavilySearchAdapter",
}
