"""Deadline evaluation: exact-match, +/-N-day tolerance, relative-phrase recall.

Dataset: JSONL of {text, expected_kind, expected_date?, anchor?}.
See docs/evaluation.md. TODO(phase-6): implement against deadline_parser.extract.
"""

from __future__ import annotations


def run(dataset_path: str, tolerance_days: int = 3) -> dict:
    raise NotImplementedError("deadline_eval.run")  # TODO(phase-6)
