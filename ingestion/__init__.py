"""Ingestion package: source adapters + normalization + politeness utilities.

Each source is a thin adapter (sources/) registered in registry.yaml. Adapters
emit the canonical NormalizedListing so all downstream stages are
source-agnostic. See docs/sourcing.md.
"""
