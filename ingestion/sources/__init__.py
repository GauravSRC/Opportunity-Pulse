"""Source adapters. Register new adapters in ADAPTERS and ../registry.yaml."""

from __future__ import annotations

from ingestion.sources.base import SourceAdapter

# Source key -> adapter class import path "module:ClassName".
ADAPTERS: dict[str, str] = {
    "demo_fixture": "ingestion.sources.demo_fixture:DemoFixtureAdapter",
    "greenhouse": "ingestion.sources.greenhouse:GreenhouseAdapter",
    "lever": "ingestion.sources.lever:LeverAdapter",
    "remotive": "ingestion.sources.remotive:RemotiveAdapter",
    "github": "ingestion.sources.github:GitHubAdapter",
    "kaggle": "ingestion.sources.kaggle:KaggleAdapter",
    "arxiv": "ingestion.sources.arxiv:ArxivAdapter",
    "rss_generic": "ingestion.sources.rss_generic:RssGenericAdapter",
    "search_tavily": "ingestion.sources.search_tavily:TavilySearchAdapter",
}


def load_adapter(adapter_key: str, config: dict | None = None) -> SourceAdapter:
    """Instantiate an adapter by its registry key."""
    if adapter_key not in ADAPTERS:
        raise KeyError(f"unknown adapter '{adapter_key}'")
    module_path, class_name = ADAPTERS[adapter_key].split(":")
    import importlib

    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(config or {})
