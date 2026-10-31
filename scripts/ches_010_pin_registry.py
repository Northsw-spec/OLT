"""CHES-010: bounded, immutable source-index PDF pin registry.

This is the single source of truth for subsequent index-driven original chapter
extensions. Never infer a word alignment, a new book mapping or redistribution
permission from a source file name. All PDF text stays private and ephemeral.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from olt_core.sources import ROOT


class CHES010PinError(ValueError):
    """Untrusted indexed source pin or original-source permission state."""


def read_indexed_source_pins(root: Path = ROOT) -> list[dict[str, Any]]:
    manifest = json.loads(
        (root / "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8")
    )
    if (manifest.get("publication_status") != "BLOCKED" or
        manifest.get("public_redistribution_rights_confirmed") is not False or
        manifest.get("original_source_to_ches_morphological_alignment_human_verified") is not False):
        raise CHES010PinError("Original source manifest cannot authorize publication or alignment")
    pins = manifest.get("indexed_original_source_pins")
    if not isinstance(pins, list) or not 1 <= len(pins) <= 16:
        raise CHES010PinError("Source index pin group must be small and explicit")
    seen: set[tuple[str, int]] = set()
    seen_names: set[str] = set()
    for record in pins:
        if not isinstance(record, dict):
            raise CHES010PinError("Original source pin must be an object")
        book = record.get("original_book")
        number = record.get("original_chapter")
        prefix = {"Gen": "gen", "Exod": "exo"}.get(book)
        if prefix is None or type(number) is not int or not 1 <= number <= 50:
            raise CHES010PinError("No authenticated source book/chapter scope")
        key = (book, number)
        filename = f"ches-{'gen' if book == 'Gen' else 'ex'}{number}.pdf"
        url = f"https://www.scripture4all.org/OnlineInterlinear/OTpdf/{prefix}{number}.pdf"
        if (key in seen or filename in seen_names or
            key in {("Gen",i) for i in (1,2,3,4)} or
            key in {("Exod",i) for i in (1,2)} or
            record.get("private_pdf_filename") != filename or
            record.get("original_source_filename_prefix_not_original_language_mapping") != prefix or
            record.get("original_pdf_url") != url or
            not isinstance(record.get("source_pdf_sha256"), str) or
            re.fullmatch("[0-9a-f]{64}",record["source_pdf_sha256"]) is None):
            raise CHES010PinError("Source pin duplicate or URL/hash/filename does not match index conventions")
        for name,minimum,maximum in (
            ("source_pdf_bytes",1000,30_000_000),
            ("source_pdf_pages",1,100),
            ("printed_pdf_verses_confirmed_by_engineering",1,200),
            ("oshb_original_word_tokens_observed",1,100_000),
            ("green_ches_pdf_spans_extracted",1,100_000),
            ("raw_original_pdf_unassigned_green_spans",0,0),
        ):
            value = record.get(name)
            if type(value) is not int or not minimum <= value <= maximum:
                raise CHES010PinError("Original source numeric or zero-loss pin invalid")
        for name in (
            "independent_pdf_filename_to_oshb_book_mapping_verified",
            "word_and_morpheme_alignment_verified",
            "full_source_text_in_public_git_permitted",
            "source_pdf_stored_in_public_repo",
        ):
            if record.get(name) is not False:
                raise CHES010PinError("Original source word-alignment/public-rights claim is unsafe")
        seen.add(key)
        seen_names.add(filename)
    return pins


INDEXED_SOURCE_PINS = read_indexed_source_pins()
INDEXED_BATCH_ITEMS = tuple(
    (row["original_book"], row["original_chapter"],
     row["private_pdf_filename"], "indexed_original_source_pins")
    for row in INDEXED_SOURCE_PINS
)


def pinned_record(book: str, chapter: int, root: Path = ROOT) -> dict[str, Any]:
    matches = [
        row for row in read_indexed_source_pins(root)
        if row["original_book"] == book and row["original_chapter"] == chapter
    ]
    if len(matches) != 1:
        raise CHES010PinError("Source chapter not present exactly once in pinned registry")
    return matches[0]
