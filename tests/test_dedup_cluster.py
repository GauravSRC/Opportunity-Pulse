"""Tests for union-find clustering (deterministic dedup core)."""

from __future__ import annotations

from dedup.cluster import cluster


def test_transitive_merge():
    pairs = [("a", "b"), ("b", "c"), ("d", "e")]
    groups = [sorted(g) for g in cluster(pairs)]
    groups.sort()
    assert groups == [["a", "b", "c"], ["d", "e"]]


def test_singletons_not_created_without_pairs():
    # Only ids that appear in a pair are clustered.
    assert cluster([]) == []
