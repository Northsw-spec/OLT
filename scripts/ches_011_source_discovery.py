"""CHES-011: four additional authentic OT chapter PDF candidates, metadata only.

This is an explicit *discovery* group; no source pin or English final
translation is implied. The genuine original OT chapter index controls
the source URL. Only ephemeral private source bytes are downloaded.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.ches_010_indexed_discovery import examine_indexed_sources

# Original Hebrew verse totals are independently verified against pinned
# OSHB/WLC evidence inside CHES-009, rather than read from PDF filename.
NEW_CHAPTERS = (
    ("Gen", 7, "gen", 24),
    ("Gen", 8, "gen", 22),
    ("Exod", 5, "exo", 23),
    ("Exod", 6, "exo", 30),
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover four original OT PDFs from source index: numeric original-language QA"
    )
    parser.add_argument("--source-index", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Original source private machine-readable use permission required")
    try:
        report = examine_indexed_sources(
            args.source_index.read_bytes(), targets=NEW_CHAPTERS
        )
    except Exception:
        parser.error("CHES-011_PRIVATE_SOURCE_DISCOVERY_FAILED")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
