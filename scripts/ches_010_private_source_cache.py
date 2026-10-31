"""CHES-010: source-index-driven and SHA-pinned PRIVATE original-PDF cache.

No source text may appear on stdout or in GitHub artifacts. A chapter is
fetched only when explicitly named by the four-chapter source-index plan and
already independently hash-pinned in the technical source manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable

from olt_core.sources import ROOT
from scripts.ches_010_indexed_discovery import (
    TARGETS, TARGET_MAP, _source_urls_from_index, _download_original_pdf,
)
from scripts.ches_010_pin_registry import pinned_record, read_indexed_source_pins
from scripts.ches_009_source_discovery import discover_source
from scripts.ches_private_alignment_review import private_file


class CHES010CacheError(ValueError):
    """Untrusted private source file / source identity / original PDF metadata."""


def _assert_source_evidence(pin: dict[str, Any], found: dict[str, Any], data: bytes, url: str) -> None:
    if (not isinstance(data, bytes) or
        len(data) != pin["source_pdf_bytes"] or
        hashlib.sha256(data).hexdigest() != pin["source_pdf_sha256"] or
        not data.startswith(b"%PDF-") or
        pin["original_pdf_url"] != url or
        found.get("source_pin_status") != "DISCOVERY_ONLY_NOT_ENGINE_APPROVED" or
        found.get("original_pdf_sha256") != pin["source_pdf_sha256"] or
        found.get("original_pdf_byte_length") != pin["source_pdf_bytes"] or
        found.get("original_pdf_page_count") != pin["source_pdf_pages"] or
        found.get("printed_pdf_verses_confirmed_by_engineering") !=
            pin["printed_pdf_verses_confirmed_by_engineering"] or
        found.get("authentic_oshb_original_word_tokens_observed") !=
            pin["oshb_original_word_tokens_observed"] or
        found.get("private_green_ches_pdf_spans_extracted") !=
            pin["green_ches_pdf_spans_extracted"] or
        found.get("unassigned_original_green_spans") != 0 or
        found.get("verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS") !=
            pin["verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"] or
        found.get("verses_with_green_fragments_on_multiple_pdf_pages") !=
            pin["verses_with_green_fragments_on_multiple_pdf_pages"] or
        found.get("min_green_spans_in_one_verse") != pin["min_green_spans_in_one_verse"] or
        found.get("max_green_spans_in_one_verse") != pin["max_green_spans_in_one_verse"] or
        found.get("word_and_morpheme_alignment_verified") is not False or
        found.get("english_translation_owner_approved") is not False or
        found.get("publication_status") != "BLOCKED"):
        raise CHES010CacheError("Original PDF changed or authentic source QA metadata mismatched")


def _write_safe_private_pdf(path: Path, data: bytes) -> str:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file():
            raise CHES010CacheError("PRIVATE_ORIGINAL_SOURCE_PATH_UNSAFE")
        if path.read_bytes() != data:
            raise CHES010CacheError("PRIVATE_ORIGINAL_SOURCE_CHANGED_NO_OVERWRITE")
        return "SKIPPED_IDENTICAL"
    fd, temp = tempfile.mkstemp(prefix=".ches10-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(temp, 0o600)
        # No other process should write to this private output directory.
        # Race protection: never replace a newly created unrecognized source.
        if path.exists() or path.is_symlink():
            raise CHES010CacheError("PRIVATE_ORIGINAL_SOURCE_RACE_NO_OVERWRITE")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return "CREATED_PRIVATE"


def cache_indexed_originals(
    index_html: bytes, private_directory: Path, *,
    fetch_pdf: Callable[[str], bytes] = _download_original_pdf,
    root: Path = ROOT,
) -> dict[str, Any]:
    urls, index = _source_urls_from_index(index_html)
    pins = read_indexed_source_pins(root)
    keys = {(row["original_book"],row["original_chapter"]) for row in pins}
    if keys != set(TARGET_MAP):
        raise CHES010CacheError("Selected index discovery set differs from exact pinned source set")
    # Validate *all four* original source PDFs and their genuine verse/word
    # geometry BEFORE saving even one candidate.
    validated: list[tuple[dict[str, Any], bytes]] = []
    for book, chapter, _, _ in TARGETS:
        pin = pinned_record(book, chapter, root)
        url = urls[book,chapter]
        pdf = fetch_pdf(url)
        try:
            source = discover_source(pdf, book, chapter, root=root,
                                     approved_targets=TARGET_MAP)
        except Exception as exc:
            raise CHES010CacheError("Authentic original PDF verse inspection failed") from exc
        _assert_source_evidence(pin, source, pdf, url)
        validated.append((pin,pdf))
    directory = private_file(private_directory / "source-cache-sentinel").parent
    directory.mkdir(mode=0o700,parents=True,exist_ok=True)
    results: list[dict[str, Any]] = []
    for pin,data in validated:
        saved = directory / pin["private_pdf_filename"]
        action = _write_safe_private_pdf(saved, data)
        results.append({
            "scope": f'{pin["original_book"]}.{pin["original_chapter"]}',
            "source_pdf_sha256": pin["source_pdf_sha256"],
            "source_pdf_bytes": pin["source_pdf_bytes"],
            "private_cache_result": action,
        })
    return {
        "checkpoint":"CHES-010-PINNED-PRIVATE-SOURCE-CACHE",
        "source_index_html_sha256":index["source_index_html_sha256"],
        "checked_original_source_pdfs":len(results),
        "new_private_source_files_created":sum(x["private_cache_result"]=="CREATED_PRIVATE" for x in results),
        "exact_private_source_files_skipped":sum(x["private_cache_result"]=="SKIPPED_IDENTICAL" for x in results),
        "source_pins_verified":True,
        "original_source_to_ches_word_alignment_verified":False,
        "english_translation_owner_approved":False,
        "publication_status":"BLOCKED",
        "private_files":results,
    }


def main() -> int:
    parser=argparse.ArgumentParser(
        description="Fetch only exact SHA-pinned original source PDFs into a private directory"
    )
    parser.add_argument("--source-index",required=True,type=Path)
    parser.add_argument("--output-private-directory",required=True,type=Path)
    parser.add_argument("--confirm-machine-readable-use-permission",action="store_true")
    a=parser.parse_args()
    if not a.confirm_machine_readable_use_permission:
        parser.error("Original source private machine-readable use permission confirmation required")
    try:
        result=cache_indexed_originals(
            a.source_index.read_bytes(),a.output_private_directory
        )
    except Exception:
        parser.error("CHES-010_PINNED_PRIVATE_SOURCE_CACHE_FAILED")
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
