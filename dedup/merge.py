"""Merge a cluster into a canonical record.

Keeps richest fields, unions skills, takes earliest posted_at, and retains all
source URLs in merged_metadata_json. Marks one member is_canonical.
See docs/ml-design.md section 6.
"""

from __future__ import annotations


def choose_canonical(members: list[dict]) -> str:
    """Pick the representative listing id (most complete record). TODO(phase-2)."""
    raise NotImplementedError("choose_canonical")


def merge_metadata(members: list[dict]) -> dict:
    """Return merged_metadata_json for the cluster. TODO(phase-2)."""
    raise NotImplementedError("merge_metadata")
