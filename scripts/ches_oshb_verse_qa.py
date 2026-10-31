"""CHES-002 private Genesis 1 source PDF ↔ original Hebrew VERSE locator QA.

We validate verse identity/count and PDF provenance, NOT a word, morpheme,
lexeme or sense alignment. No licensed CHES glyph text is printed or saved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from olt_core.sources import ROOT, load_ot_book, read_provenance


class CHESVerseQAError(ValueError):
    """Mismatch in a chapter source, edition or original verse reference."""


def verify_genesis_1_verse_locators(private_source: dict[str, Any],
                                   root: Path = ROOT) -> dict[str, Any]:
    """Strictly scoped one-chapter correspondence; other books require mapping review."""
    manifest = json.loads((root / "data/engine/olt_ches_source_manifest.json").read_text(
        encoding="utf-8"))
    pinned = manifest["source_reference"]
    if private_source.get("book") not in ("gen", "Gen") or private_source.get("chapter") != 1:
        raise CHESVerseQAError("Only the reviewed original Genesis chapter-1 filename is supported")
    for observed, expected in (
        ("original_source_pdf_sha256", pinned["source_pdf_sha256"]),
        ("source_pdf_byte_length", pinned["source_pdf_bytes"]),
        ("source_pdf_page_count", pinned["source_pdf_pages"]),
        ("verses_extracted", pinned["printed_pdf_verses_confirmed_by_engineering"]),
        ("ches_pdf_green_spans", pinned["green_ches_pdf_spans_extracted"]),
    ):
        if private_source.get(observed) != expected:
            raise CHESVerseQAError("Genesis source PDF provenance/structure changed: " + observed)
    if (private_source.get("source_book_identifier_is_not_verified_oshb_book_mapping") is not True or
        private_source.get("full_source_text_in_public_git_permitted") is not False or
        private_source.get("alignment_with_oshb_words_verified") is not False or
        private_source.get("olt_english_translation_approved") is not False or
        private_source.get("publication_status") != "BLOCKED"):
        raise CHESVerseQAError("Original-source permission or alignment boundary was modified")
    if ("source_origin_url" in private_source and
        private_source["source_origin_url"] != pinned["original_pdf_url"]):
        raise CHESVerseQAError("Incorrect original source URL")

    source_book = load_ot_book("Gen", root, read_provenance(root))
    original = {v["reference"]: v for v in source_book["verses"]
                if v["reference"].startswith("Gen.1.")}
    if len(original) != 31:
        raise CHESVerseQAError("Authentic Hebrew source Genesis 1 verse count differs")
    rows = private_source.get("verses")
    if not isinstance(rows, list) or len(rows) != 31:
        raise CHESVerseQAError("PDF does not contain all 31 distinct printed verses")
    span_count = 0
    total_words = 0
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or row.get("reference") != (
            f"{private_source['book']}.1.{number}"):
            raise CHESVerseQAError("Missing, reordered or duplicate PDF verse marker")
        if row.get("publication_status") != "BLOCKED":
            raise CHESVerseQAError("Imported source verse wrongly marked public")
        source_ref = f"Gen.1.{number}"
        verse = original.get(source_ref)
        if verse is None or not isinstance(verse.get("words"), list) or not verse["words"]:
            raise CHESVerseQAError("No verified OSHB original Hebrew verse")
        green_spans = row.get("source_ches_spans_NOT_OLT_TRANSLATION")
        if not isinstance(green_spans, list) or not green_spans:
            raise CHESVerseQAError("Missing source CHES spans for an original PDF verse")
        span_count += len(green_spans)
        total_words += len(verse["words"])
    if span_count != pinned["green_ches_pdf_spans_extracted"] or total_words != 434:
        raise CHESVerseQAError("Original PDF span or OSHB word count mismatch")

    return {
        "checkpoint": "CHES-002",
        "source_pdf_sha256_verified": True,
        "chapter_verse_locators_match_original_oshb": True,
        "source_original_book_scope": "Gen.1 ONLY; NO GENERAL OT CROSSWALK",
        "original_oshb_verses_checked": 31,
        "original_oshb_word_tokens_observed_not_ches_aligned": total_words,
        "private_pdf_green_spans_observed_not_oshb_word_aligned": span_count,
        "ches_to_oshb_word_level_alignment_verified": False,
        "ches_to_oshb_morpheme_alignment_verified": False,
        "sense_selection_or_english_translation_verified": False,
        "whole_ot_verified": False,
        "public_ches_payload_exported": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Source-bound private Genesis 1 PDF verse locator QA")
    parser.add_argument("--pdf", type=Path, required=True)
    args = parser.parse_args()
    from scripts.ches_import import import_private_pdf
    private_data = import_private_pdf(args.pdf.read_bytes(), "Gen", 1, expected_verses=31)
    summary = verify_genesis_1_verse_locators(private_data)
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
