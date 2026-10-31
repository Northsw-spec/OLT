"""CHES-009 discovery: inspect two additional REAL OT source PDF layouts, counts only.

One-time discovery is NOT a source pin. Nothing returned contains the
private original English interlinear, Hebrew verses, or licensed excerpts.
Do not use these observations to authorize a translation or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_import import (
    explicit_verse_markers, import_private_pdf, is_ches_green, page_spans,
)

DISCOVERY = {("Gen", 4): 26, ("Exod", 2): 25}


class CHES009SourceError(ValueError):
    """Original chapter source or verse evidence does not match the target."""


def discover_source(pdf: bytes, book: str, chapter: int,
                    root: Path = ROOT, *,
                    approved_targets: Mapping[tuple[str, int], int] = DISCOVERY) -> dict[str, Any]:
    if type(book) is not str or type(chapter) is not int or (book, chapter) not in approved_targets:
        raise CHES009SourceError("Unsupported unpinned original chapter")
    expected = approved_targets[(book, chapter)]
    original = load_ot_book(book, root, read_provenance(root))
    verses = [
        v for v in original["verses"]
        if v["reference"].startswith(f"{book}.{chapter}.")
    ]
    if len(verses) != expected:
        raise CHES009SourceError("Authentic original-language verse inventory differs")
    source_ids: set[str] = set()
    words = 0
    for n, v in enumerate(verses, 1):
        if v["reference"] != f"{book}.{chapter}.{n}" or not v["words"]:
            raise CHES009SourceError("Authentic original verse sequence differs")
        for ordinal, w in enumerate(v["words"], 1):
            if (w["reference"] != v["reference"] or w["ordinal"] != ordinal or
                not isinstance(w["source_id"], str) or w["source_id"] in source_ids):
                raise CHES009SourceError("Duplicate or malformed original source token")
            source_ids.add(w["source_id"])
            words += 1
    observed = import_private_pdf(pdf, book, chapter, expected_verses=expected)
    import fitz
    with fitz.open(stream=pdf, filetype="pdf") as document:
        spans = [
            s for page, p in enumerate(document, 1)
            for s in page_spans(p, page)
        ]
    raw_green = [s for s in spans if is_ches_green(s["color"])]
    marks = explicit_verse_markers(spans, chapter)
    if [m["verse"] for m in marks] != list(range(1, expected+1)):
        raise CHES009SourceError("Original PDF missing required printed verse markers")
    source_verses = observed["verses"]
    if len(source_verses) != expected:
        raise CHES009SourceError("Original PDF verse assignment differs")
    assigned = 0
    mismatches = 0
    crosses = 0
    min_spans = 1_000_000
    max_spans = 0
    for n, row in enumerate(source_verses, 1):
        if row["reference"] != f"{book}.{chapter}.{n}":
            raise CHES009SourceError("Assigned original source verse changed")
        greens = row["source_ches_spans_NOT_OLT_TRANSLATION"]
        size = len(greens)
        if size < 1:
            raise CHES009SourceError("An original verse contains no English green spans")
        assigned += size
        mismatches += int(size != len(verses[n - 1]["words"]))
        crosses += int(len({s["page"] for s in greens}) > 1)
        min_spans = min(min_spans, size)
        max_spans = max(max_spans, size)
    if assigned != observed["ches_pdf_green_spans"]:
        raise CHES009SourceError("Imported verse fragment count changed")
    unassigned = len(raw_green) - assigned
    before_first = sum(
        (s["page"], s["y"]) < (marks[0]["page"], marks[0]["y"])
        for s in raw_green
    )
    if unassigned < 0 or unassigned != before_first:
        raise CHES009SourceError("Unexpected green-source text loss after verse marker")
    return {
        "checkpoint": "CHES-009-SOURCE-DISCOVERY",
        "scope": f"{book}.{chapter}",
        "original_pdf_sha256": hashlib.sha256(pdf).hexdigest(),
        "original_pdf_byte_length": len(pdf),
        "original_pdf_page_count": observed["source_pdf_page_count"],
        "printed_pdf_verses_confirmed_by_engineering": expected,
        "authentic_oshb_original_word_tokens_observed": words,
        "private_green_ches_pdf_spans_extracted": assigned,
        "raw_original_pdf_green_spans": len(raw_green),
        "unassigned_original_green_spans": unassigned,
        "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS":
            mismatches,
        "verses_with_green_fragments_on_multiple_pdf_pages": crosses,
        "min_green_spans_in_one_verse": min_spans,
        "max_green_spans_in_one_verse": max_spans,
        "source_pin_status": "DISCOVERY_ONLY_NOT_ENGINE_APPROVED",
        "original_pdf_book_prefix_to_oshb_mapping_independently_verified": False,
        "word_and_morpheme_alignment_verified": False,
        "english_translation_owner_approved": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Original OT PDF source-only numeric layout discovery")
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--book", choices=["Gen", "Exod"], required=True)
    p.add_argument("--chapter", type=int, required=True)
    p.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    a = p.parse_args()
    if not a.confirm_machine_readable_use_permission:
        p.error("Explicit machine-readable source-use permission is required")
    result = discover_source(a.pdf.read_bytes(), a.book, a.chapter)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
