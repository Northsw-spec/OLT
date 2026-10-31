"""CHES-010: bounded, source-index-driven REAL PDF discovery (metadata only).

Four additional original OT chapter files are selected using links parsed from
the genuine 929-chapter index.  NO unpinned PDF is eligible for English drafts.
Downloaded original CHES text/PDFs remain only in process memory. Output never
includes copyrighted words, English passages, original Hebrew content or
private user notes. No arbitrary URL is accepted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from scripts.ches_index import parse_index
from scripts.ches_009_source_discovery import discover_source

# Separate from the six already SHA-pinned and accepted chapters. Each
# filename-prefix-to-OSHB-book relation is an explicit engineering candidate,
# NOT independently certified linguistic original-word correspondence.
TARGETS: tuple[tuple[str, int, str, int], ...] = (
    ("Gen", 5, "gen", 32),
    ("Gen", 6, "gen", 22),
    ("Exod", 3, "exo", 22),
    ("Exod", 4, "exo", 31),
)
TARGET_MAP = {(book, chapter): verses for book, chapter, _, verses in TARGETS}
PDF_MAX_BYTES = 30_000_000
ALLOWED_HOST = "www.scripture4all.org"
SOURCE_PDF_FOLDER = "/OnlineInterlinear/OTpdf/"


class CHES010Error(ValueError):
    """Source index or original PDF failed a conservative discovery constraint."""


def _source_urls_from_index(index_html: bytes) -> tuple[dict[tuple[str, int], str], dict[str, Any]]:
    try:
        index = parse_index(index_html)
    except ValueError as exc:
        raise CHES010Error("Original OT chapter index rejected by strict parser") from exc
    if (index.get("discovered_chapter_pdf_count") != 929 or
        index.get("discovered_original_source_filename_prefix_count") != 39 or
        index.get("rights_for_public_CHES_data_export_confirmed") is not False or
        index.get("book_prefixes_are_not_approved_oshb_book_mappings") is not True):
        raise CHES010Error("Original source index inventory or rights status differs")
    by_key = {
        (row["source_book_filename_prefix_NOT_OLT_BOOK_ID"],
         row["source_chapter_filename_number"]): row["original_pdf_url"]
        for row in index["chapter_links"]
    }
    if len(by_key) != 929:
        raise CHES010Error("Duplicated original book prefix/chapter index identity")
    urls: dict[tuple[str, int], str] = {}
    for book, chapter, source_prefix, _ in TARGETS:
        url = by_key.get((source_prefix, chapter))
        expected = f"https://{ALLOWED_HOST}{SOURCE_PDF_FOLDER}{source_prefix}{chapter}.pdf"
        if type(url) is not str or url != expected:
            raise CHES010Error("Authentic source index omits an expected chapter PDF")
        urls[book, chapter] = url
    return urls, index


def _download_original_pdf(url: str) -> bytes:
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST or
        parsed.port is not None or parsed.username is not None or
        parsed.password is not None or parsed.query or parsed.fragment or
        not parsed.path.startswith(SOURCE_PDF_FOLDER) or
        not parsed.path.endswith(".pdf")):
        raise CHES010Error("Noncanonical original PDF address")
    request = Request(url, headers={"User-Agent": "OLT-private-source-geometry-audit/1.0"})
    with urlopen(request, timeout=40) as response:
        final = response.geturl()
        if final != url:
            raise CHES010Error("Source redirect was not identical to the pinned index URL")
        data = response.read(PDF_MAX_BYTES + 1)
    if not 1000 <= len(data) <= PDF_MAX_BYTES or not data.startswith(b"%PDF-"):
        raise CHES010Error("Original chapter response is not an acceptable PDF file")
    return data


def examine_indexed_sources(
    index_html: bytes,
    *, fetch_pdf: Callable[[str], bytes] = _download_original_pdf,
) -> dict[str, Any]:
    urls, index = _source_urls_from_index(index_html)
    records: list[dict[str, Any]] = []
    for book, chapter, _, _ in TARGETS:
        original = fetch_pdf(urls[book, chapter])
        if (type(original) is not bytes or
            not 1000 <= len(original) <= PDF_MAX_BYTES or
            not original.startswith(b"%PDF-")):
            raise CHES010Error("Invalid candidate original PDF bytes")
        source = discover_source(
            original, book, chapter, approved_targets=TARGET_MAP
        )
        if (source.get("scope") != f"{book}.{chapter}" or
            source.get("source_pin_status") != "DISCOVERY_ONLY_NOT_ENGINE_APPROVED" or
            source.get("word_and_morpheme_alignment_verified") is not False or
            source.get("english_translation_owner_approved") is not False or
            source.get("publication_status") != "BLOCKED" or
            source.get("unassigned_original_green_spans") != 0):
            raise CHES010Error("Source discovery requires further review: unsafe metadata")
        records.append({
            "original_book": book, "original_chapter": chapter,
            "source_pdf_url": urls[book, chapter], **source
        })
    return {
        "checkpoint": "CHES-010-SOURCE-INDEX-DISCOVERY",
        "source_index_html_sha256": index["source_index_html_sha256"],
        "original_chapter_index_links_confirmed": index["discovered_chapter_pdf_count"],
        "original_source_book_filename_prefixes_confirmed":
            index["discovered_original_source_filename_prefix_count"],
        "selected_new_original_chapter_PDFs": len(records),
        "total_printed_original_verse_markers": sum(
            r["printed_pdf_verses_confirmed_by_engineering"] for r in records
        ),
        "total_authentic_oshb_word_tokens_not_ches_aligned": sum(
            r["authentic_oshb_original_word_tokens_observed"] for r in records
        ),
        "total_private_original_ches_green_typography_spans": sum(
            r["private_green_ches_pdf_spans_extracted"] for r in records
        ),
        "all_original_source_greens_assigned_to_verses":
            all(r["unassigned_original_green_spans"] == 0 for r in records),
        "source_pin_status": "DISCOVERY_ONLY_NOT_ENGINE_APPROVED",
        "english_translation_owner_approved": False,
        "word_and_morpheme_alignment_verified": False,
        "publication_status": "BLOCKED",
        "selected_source_metadata": records,
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="CHES-010: index-select 4 genuine OT PDFs; inspect only nontext metadata"
    )
    p.add_argument("--source-index", required=True, type=Path)
    p.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    args = p.parse_args()
    if not args.confirm_machine_readable_use_permission:
        p.error("Explicit permission for private machine-readable source use required")
    try:
        result = examine_indexed_sources(args.source_index.read_bytes())
    except Exception:
        # Avoid leaking source URLs with query params, or raw copyrighted text,
        # from future third-party network/parser exception implementations.
        p.error("CHES-010_SOURCE_DISCOVERY_FAILED")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
