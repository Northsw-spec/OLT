"""CHES-006: source-checked, text-free multi-chapter interlinear layout telemetry.

The source provider is explicitly licensed for private machine-readable use as
reported by the owner. Do NOT emit copyrighted green PDF text, accept inferred
word alignment, or count a typography-span mismatch as a translation error.

The only present scope is four authentic OT chapter layouts. Other 925 chapter
PDFs and the Greek NT remain OUT OF SCOPE. All real PDF access is ephemeral.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_import import (
    explicit_verse_markers, import_private_pdf, is_ches_green, page_spans,
)

PILOT = {
    ("Gen", 1): (31, "source_reference"),
    ("Gen", 2): (25, "additional_chapter_layout_source_reference"),
    ("Gen", 3): (24, "third_chapter_layout_source_reference"),
    ("Exod", 1): (22, "cross_book_layout_source_reference"),
}


class CHESLayoutMetricsError(ValueError):
    """Unverified chapter source, rights, PDF identity or geometry."""


def _source_bytes_and_geometry(pdf_bytes: bytes) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Extract actual PDF layout without letting green copyrighted text escape."""
    import fitz
    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
        original_spans = [
            span for page_number, page in enumerate(pdf, 1)
            for span in page_spans(page, page_number)
        ]
    return {"original_pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest()}, original_spans


def measure_private_chapter_layout(
    source: dict[str, Any], *,
    root: Path = ROOT,
    full_pdf_spans: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Check authentic OSHB IDs and page/verse layout; never verify word links.

    full_pdf_spans is only used for counts and coordinates. No source text is
    retained in this returned report. Unpinned discovery is explicitly unsafe
    for downstream English drafting and must NOT be used to publish.
    """
    if not isinstance(source, dict):
        raise CHESLayoutMetricsError("Missing private imported chapter")
    book, chapter = source.get("book"), source.get("chapter")
    if (type(book) is not str or type(chapter) is not int or
        (book, chapter) not in PILOT):
        raise CHESLayoutMetricsError("This QA only covers four explicitly chosen original OT chapters")
    expected_verses, source_key = PILOT[(book, chapter)]
    if (source.get("source_book_identifier_is_not_verified_oshb_book_mapping") is not True or
        source.get("full_source_text_in_public_git_permitted") is not False or
        source.get("alignment_with_oshb_words_verified") is not False or
        source.get("olt_english_translation_approved") is not False or
        source.get("independent_grammar_or_sense_approved") is not False or
        source.get("publication_status") != "BLOCKED"):
        raise CHESLayoutMetricsError("Source-language link, license or approval state is unsupported")
    if (type(source.get("verses_extracted")) is not int or
        source["verses_extracted"] != expected_verses):
        raise CHESLayoutMetricsError("Actual original PDF verse inventory does not match selected scope")
    digest = source.get("original_source_pdf_sha256")
    pages = source.get("source_pdf_page_count")
    size = source.get("source_pdf_byte_length")
    if (not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None or
        type(pages) is not int or not 1 <= pages <= 100 or
        type(size) is not int or not 1_000 <= size <= 30_000_000):
        raise CHESLayoutMetricsError("Missing original PDF identity")
    manifest = json.loads((root / "data/engine/olt_ches_source_manifest.json").read_text(
        encoding="utf-8"))
    pinned = manifest.get(source_key)
    if not isinstance(pinned, dict) or (
        pinned.get("original_book") != book or
        type(pinned.get("original_chapter")) is not int or
        pinned["original_chapter"] != chapter or
        pinned.get("source_pdf_sha256") != digest or
        type(pinned.get("source_pdf_bytes")) is not int or
        pinned["source_pdf_bytes"] != size or
        type(pinned.get("source_pdf_pages")) is not int or
        pinned["source_pdf_pages"] != pages or
        type(pinned.get("printed_pdf_verses_confirmed_by_engineering")) is not int or
        pinned["printed_pdf_verses_confirmed_by_engineering"] != expected_verses or
        pinned.get("full_source_text_in_public_git_permitted", pinned.get("source_text_in_public_repo")) is not False or
        pinned.get("word_and_morpheme_alignment_verified", False) is not False or
        pinned.get("independent_pdf_filename_to_oshb_book_mapping_verified", False) is not False
    ):
        raise CHESLayoutMetricsError("Missing or changed exact original PDF pin, rights or source identity")
    book_source = load_ot_book(book, root, read_provenance(root))
    verse_lookup = {v["reference"]: v for v in book_source["verses"]
                    if v["reference"].startswith(f"{book}.{chapter}.")}
    if len(verse_lookup) != expected_verses:
        raise CHESLayoutMetricsError("Authentic OSHB verse inventory differs")
    rows = source.get("verses")
    if not isinstance(rows, list) or len(rows) != expected_verses:
        raise CHESLayoutMetricsError("Original PDF verse records missing")
    all_original_ids: set[str] = set()
    total_words = total_spans = 0
    source_pages: set[int] = set()
    spans_per_verse: list[int] = []
    word_per_verse: list[int] = []
    same_verse_span_word_count_differs = 0
    green_over_page_breaks = 0
    outside_original_verse_y = 0
    for i, row in enumerate(rows, 1):
        ref = f"{book}.{chapter}.{i}"
        if not isinstance(row, dict) or row.get("reference") != ref or (
            row.get("publication_status") != "BLOCKED"):
            raise CHESLayoutMetricsError("Original PDF verse sequence/approval changed")
        verse_words = verse_lookup[ref].get("words")
        if not isinstance(verse_words, list) or not verse_words:
            raise CHESLayoutMetricsError("Authentic source original words missing")
        for ordinal, word in enumerate(verse_words, 1):
            if (not isinstance(word, dict) or word.get("reference") != ref or
                word.get("ordinal") != ordinal or
                not isinstance(word.get("source_id"), str) or
                word["source_id"] in all_original_ids):
                raise CHESLayoutMetricsError("Original source Hebrew token ID malformed or repeated")
            all_original_ids.add(word["source_id"])
        green = row.get("source_ches_spans_NOT_OLT_TRANSLATION")
        if not isinstance(green, list) or not green:
            raise CHESLayoutMetricsError("Original PDF verse missing green source fragments")
        verse_pages: set[int] = set()
        previous: tuple[int, float, float] | None = None
        for span in green:
            if not isinstance(span, dict):
                raise CHESLayoutMetricsError("Malformed PDF source fragment")
            page, x, y, original_text = (
                span.get("page"), span.get("pdf_x"), span.get("pdf_y"),
                span.get("original_ches_line_text")
            )
            if (type(page) is not int or not 1 <= page <= pages or
                type(x) not in (float, int) or type(y) not in (float, int) or
                not (0 <= x < 100_000 and 0 <= y < 100_000) or
                not isinstance(original_text, str) or not original_text.strip()):
                raise CHESLayoutMetricsError("Invalid source PDF text geometry or missing private text")
            locator = (page, round(y, 1), float(x))
            if previous is not None and locator < previous:
                raise CHESLayoutMetricsError("Source green fragments reordered within verse")
            previous = locator
            verse_pages.add(page)
        green_over_page_breaks += int(len(verse_pages) > 1)
        source_pages |= verse_pages
        if len(green) != len(verse_words):
            same_verse_span_word_count_differs += 1
        spans_per_verse.append(len(green))
        word_per_verse.append(len(verse_words))
        total_words += len(verse_words)
        total_spans += len(green)
    if (type(source.get("ches_pdf_green_spans")) is not int or
        source["ches_pdf_green_spans"] != total_spans):
        raise CHESLayoutMetricsError("Original source span count contradicts verse contents")
    if (pinned.get("green_ches_pdf_spans_extracted") != total_spans or
        "oshb_original_word_tokens_observed" in pinned and
        pinned["oshb_original_word_tokens_observed"] != total_words):
        raise CHESLayoutMetricsError("Pinned original source span or Hebrew word totals disagree")
    # Layout warning counts are observations, not source identity or language
    # approval. The exact SHA-256 pin guards real PDF geometry reproducibility;
    # synthetic tests can use deliberately different verse span distributions.
    raw_green_count = None
    unassigned_green_count = None
    marker_count = None
    green_before_first_printed_verse_marker = None
    if full_pdf_spans is not None:
        if not isinstance(full_pdf_spans, list):
            raise CHESLayoutMetricsError("Original PDF geometry inventory is not a list")
        raw_green = [s for s in full_pdf_spans if is_ches_green(s.get("color"))]
        raw_green_count = len(raw_green)
        markers = explicit_verse_markers(full_pdf_spans, chapter)
        if [m["verse"] for m in markers] != list(range(1, expected_verses + 1)):
            raise CHESLayoutMetricsError("Printed original verse anchors disagree with expected inventory")
        marker_count = len(markers)
        first = markers[0]
        green_before_first_printed_verse_marker = sum(
            1 for s in raw_green if (s["page"], s["y"]) < (first["page"], first["y"])
        )
        unassigned_green_count = raw_green_count - total_spans
        if unassigned_green_count < 0:
            raise CHESLayoutMetricsError("More imported green fragments than in original PDF")
        if unassigned_green_count != green_before_first_printed_verse_marker:
            raise CHESLayoutMetricsError("Original green PDF fragment assignment lost/duplicated content")
        if ("raw_original_pdf_unassigned_green_spans" in pinned and
            pinned["raw_original_pdf_unassigned_green_spans"] != unassigned_green_count):
            raise CHESLayoutMetricsError("Original PDF unassigned source ink changed")
    return {
        "checkpoint": "CHES-006",
        "scope": f"{book}.{chapter}",
        "source_pdf_sha256": digest,
        "source_pdf_byte_length": size,
        "source_pdf_page_count": pages,
        "source_pin_status": "ORIGINAL_PDF_PINNED_EXACT",
        "printed_verse_markers_checked": marker_count,
        "authentic_oshb_verse_references_checked": len(rows),
        "authentic_oshb_word_tokens_observed_not_ches_aligned": total_words,
        "private_pdf_green_spans_observed_not_oshb_word_aligned": total_spans,
        "original_pdf_pages_containing_assigned_green_fragments": len(source_pages),
        "min_green_spans_in_one_verse": min(spans_per_verse),
        "max_green_spans_in_one_verse": max(spans_per_verse),
        "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS":
            same_verse_span_word_count_differs,
        "verses_with_green_fragments_on_multiple_pdf_pages": green_over_page_breaks,
        "raw_original_pdf_green_span_count": raw_green_count,
        "unassigned_original_green_spans": unassigned_green_count,
        "raw_original_green_spans_before_first_printed_verse": 
            green_before_first_printed_verse_marker,
        "layout_requires_exception_review":
            bool(unassigned_green_count or green_over_page_breaks),
        "source_pdf_book_prefix_vs_oshb_mapping_independently_verified": False,
        "english_translation_automatically_verified": False,
        "oshb_to_pdf_word_alignment_verified": False,
        "english_grammar_rules_automatically_applied": False,
        "full_old_testament_processed": False,
        "publication_status": "BLOCKED",
    }


def audit_real_pdf(
    original_bytes: bytes, *, book: str, chapter: int, root: Path = ROOT,
) -> dict[str, Any]:
    expected, _ = PILOT.get((book, chapter), (None, None))
    if expected is None:
        raise CHESLayoutMetricsError("Unsupported source chapter")
    chapter_source = import_private_pdf(original_bytes, book, chapter, expected_verses=expected)
    _, full_spans = _source_bytes_and_geometry(original_bytes)
    return measure_private_chapter_layout(
        chapter_source, root=root, full_pdf_spans=full_spans,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="CHES private source geometry diagnostics only")
    parser.add_argument("--book", choices=["Gen", "Exod"], required=True)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Explicit original-source machine-readable permission required")
    result = audit_real_pdf(
        args.pdf.read_bytes(), book=args.book, chapter=args.chapter,
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
