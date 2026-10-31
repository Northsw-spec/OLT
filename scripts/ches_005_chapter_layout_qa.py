"""CHES-005: fail-closed Genesis 2 chapter-layout QA against pinned OSHB.

This is an *additional genuine PDF layout* engineering test. It NEVER
claims that same-verse CHES spans match Hebrew original words or that the
CHES import source's book prefix is independently certified.
No third-party English source text is printed or saved.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_import import import_private_pdf


class CHESChapterLayoutError(ValueError):
    """Untrusted additional source layout or biblical verse inventory."""


def verify_genesis_two_layout(private_source: dict[str, Any],
                              root: Path = ROOT) -> dict[str, Any]:
    if (not isinstance(private_source, dict) or
        private_source.get("book") != "Gen" or
        private_source.get("chapter") != 2 or
        private_source.get("verses_extracted") != 25 or
        private_source.get("source_book_identifier_is_not_verified_oshb_book_mapping") is not True or
        private_source.get("full_source_text_in_public_git_permitted") is not False or
        private_source.get("alignment_with_oshb_words_verified") is not False or
        private_source.get("olt_english_translation_approved") is not False or
        private_source.get("publication_status") != "BLOCKED"):
        raise CHESChapterLayoutError("Unsupported Genesis 2 source identity or rights status")
    sha = private_source.get("original_source_pdf_sha256")
    if not isinstance(sha, str) or not re.fullmatch("[0-9a-f]{64}", sha):
        raise CHESChapterLayoutError("No SHA256 original PDF identity")
    page_count = private_source.get("source_pdf_page_count")
    byte_count = private_source.get("source_pdf_byte_length")
    if (type(page_count) is not int or not 1 <= page_count <= 100 or
        type(byte_count) is not int or not 1000 <= byte_count <= 30_000_000):
        raise CHESChapterLayoutError("Bad original PDF size/page evidence")
    rows = private_source.get("verses")
    if not isinstance(rows, list) or len(rows) != 25:
        raise CHESChapterLayoutError("Missing original Genesis 2 verse labels")
    authentic = load_ot_book("Gen", root, read_provenance(root))
    original = {
        v["reference"]: v for v in authentic["verses"]
        if re.fullmatch(r"Gen\.2\.(?:[1-9]|1[0-9]|2[0-5])", v["reference"])
    }
    if len(original) != 25:
        raise CHESChapterLayoutError("Authentic OSHB Genesis 2 verse count mismatch")
    total_spans = total_words = 0
    word_ids: set[str] = set()
    for number, row in enumerate(rows, 1):
        ref = f"Gen.2.{number}"
        if (not isinstance(row, dict) or
            row.get("reference") != ref or
            row.get("publication_status") != "BLOCKED" or
            not isinstance(row.get("source_ches_spans_NOT_OLT_TRANSLATION"), list) or
            not row["source_ches_spans_NOT_OLT_TRANSLATION"]):
            raise CHESChapterLayoutError("A source verse marker/span is absent or changed")
        word_rows = original[ref].get("words")
        if not isinstance(word_rows, list) or not word_rows:
            raise CHESChapterLayoutError("An authentic Hebrew verse is missing")
        for ordinal, word in enumerate(word_rows, 1):
            if (word.get("reference") != ref or word.get("ordinal") != ordinal or
                not isinstance(word.get("source_id"), str) or
                word["source_id"] in word_ids):
                raise CHESChapterLayoutError("Authentic source Hebrew word ID mismatch")
            word_ids.add(word["source_id"])
        total_words += len(word_rows)
        total_spans += len(row["source_ches_spans_NOT_OLT_TRANSLATION"])
    if (private_source.get("ches_pdf_green_spans") != total_spans or
        total_spans < 25 or total_words < 25):
        raise CHESChapterLayoutError("Green span or original word count mismatch")
    return {
        "checkpoint": "CHES-005-GENESIS-2-LAYOUT-QA",
        "original_pdf_sha256_observed": sha,
        "original_pdf_byte_length_observed": byte_count,
        "original_pdf_page_count_observed": page_count,
        "printed_verse_markers_checked": 25,
        "authentic_oshb_verse_references_checked": len(original),
        "authentic_oshb_word_tokens_observed_not_ches_aligned": total_words,
        "private_green_pdf_spans_observed_not_oshb_word_aligned": total_spans,
        "original_pdf_book_prefix_vs_oshb_mapping_independently_verified": False,
        "word_alignment_verified": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Private Genesis 2 CHES PDF layout/source audit")
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Original source private-use confirmation is required")
    source = import_private_pdf(args.pdf.read_bytes(), "Gen", 2, expected_verses=25)
    print(json.dumps(verify_genesis_two_layout(source), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
