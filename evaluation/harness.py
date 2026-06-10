"""Evaluation harness entrypoint.

Run: ``python -m evaluation.harness --all`` (or a specific component flag).
Writes a JSON report + markdown summary to evaluation/reports/ (gitignored).
See docs/evaluation.md for metric definitions and acceptance gates.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="OpportunityPulse evaluation harness")
    parser.add_argument("--all", action="store_true", help="run every eval")
    parser.add_argument("--retrieval", action="store_true")
    parser.add_argument("--dedup", action="store_true")
    parser.add_argument("--deadline", action="store_true")
    parser.add_argument("--email", action="store_true")
    args = parser.parse_args()
    # TODO(phase-6): dispatch to the *_eval modules and aggregate a report.
    raise SystemExit(
        "TODO(phase-6): evaluation harness not yet implemented "
        f"(args={vars(args)})"
    )


if __name__ == "__main__":
    main()
