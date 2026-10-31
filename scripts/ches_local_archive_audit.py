"""CHES-LOCAL-001: offline, read-only audit of a user's private CHES JSON archive.

Only derived counters/boolean integrity facts leave this module. Never print
licensed source lines, raw JSON, local private paths, or English draft text.
This is NOT original-source PDF re-verification or Hebrew-word alignment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import stat
from typing import Any
from urllib.parse import urlsplit

from scripts.ches_index import INDEX

CHAPTERS_EXPECTED = 929
PREFIXES_EXPECTED = 39
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
FILENAME = re.compile(r"([A-Za-z0-9_-]{1,20})\.([1-9][0-9]*)\.json\Z")
MAX_JSON_BYTES = 30_000_000
MAX_CHAPTER_VERSES = 250
MAX_CHAPTER_SPANS = 250_000


class CHESArchiveError(ValueError):
    """Fail closed without echoing private CHES source material."""


def _strict_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise CHESArchiveError("DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def _positive_int(value: Any, maximum: int) -> bool:
    return type(value) is int and 1 <= value <= maximum


def _coordinate(value: Any) -> bool:
    return (
        type(value) in (int, float) and math.isfinite(value)
        and 0 <= value < 10_000
    )


def _validate_chapter(doc: Any, *, prefix: str, chapter: int) -> tuple[int, int, str, str]:
    if not isinstance(doc, dict):
        raise CHESArchiveError("INVALID_PRIVATE_CHAPTER")
    origin = urlsplit(INDEX)
    expected_url = (
        f"{origin.scheme}://{origin.netloc}/OnlineInterlinear/OTpdf/"
        f"{prefix}{chapter}.pdf"
    )
    if (
        doc.get("book") != prefix
        or type(doc.get("chapter")) is not int
        or doc["chapter"] != chapter
        or doc.get("source_origin_url") != expected_url
        or doc.get("source_book_identifier_is_not_verified_oshb_book_mapping") is not True
        or doc.get("full_source_text_in_public_git_permitted") is not False
        or doc.get("alignment_with_oshb_words_verified") is not False
        or doc.get("independent_grammar_or_sense_approved") is not False
        or doc.get("olt_english_translation_approved") is not False
        or doc.get("owner_attested_machine_readable_permission_no_public_distribution") is not True
        or doc.get("source_chapter_verse_count_independent_oshb_qa") != "NOT_DONE"
        or doc.get("publication_status") != "BLOCKED"
    ):
        raise CHESArchiveError("SOURCE_IDENTITY_OR_PUBLICATION_GATE_MISMATCH")

    original_sha = doc.get("original_source_pdf_sha256")
    index_sha = doc.get("source_original_index_sha256")
    if (
        type(original_sha) is not str
        or DIGEST.fullmatch(original_sha) is None
        or type(index_sha) is not str
        or DIGEST.fullmatch(index_sha) is None
        or not _positive_int(doc.get("source_pdf_byte_length"), 30_000_000)
        or not _positive_int(doc.get("source_pdf_page_count"), 100)
        or not _positive_int(doc.get("verses_extracted"), MAX_CHAPTER_VERSES)
        or not _positive_int(doc.get("ches_pdf_green_spans"), MAX_CHAPTER_SPANS)
    ):
        raise CHESArchiveError("ORIGINAL_PDF_METADATA_INVALID")

    verses = doc.get("verses")
    if not isinstance(verses, list) or len(verses) != doc["verses_extracted"]:
        raise CHESArchiveError("MISSING_OR_DUPLICATE_VERSE_COUNT")

    spans_seen = 0
    for number, row in enumerate(verses, 1):
        if (
            not isinstance(row, dict)
            or row.get("reference") != f"{prefix}.{chapter}.{number}"
            or row.get("publication_status") != "BLOCKED"
            or row.get("english_draft_status") != "CHES_SOURCE_ONLY_UNALIGNED"
            or not _positive_int(
                row.get("explicit_original_pdf_verse_anchor_page"),
                doc["source_pdf_page_count"]
            )
            or not _coordinate(row.get("explicit_original_pdf_verse_anchor_y"))
        ):
            raise CHESArchiveError("VERSE_LOCATOR_OR_APPROVAL_MISMATCH")
        spans = row.get("source_ches_spans_NOT_OLT_TRANSLATION")
        if not isinstance(spans, list) or not spans:
            raise CHESArchiveError("MISSING_PRIVATE_SOURCE_SPANS")
        spans_seen += len(spans)
        if spans_seen > MAX_CHAPTER_SPANS:
            raise CHESArchiveError("SOURCE_SPAN_BOUND_EXCEEDED")
        for span in spans:
            if (
                not isinstance(span, dict)
                or not _positive_int(span.get("page"), doc["source_pdf_page_count"])
                or not _coordinate(span.get("pdf_x"))
                or not _coordinate(span.get("pdf_y"))
                or not isinstance(span.get("original_ches_line_text"), str)
                or not span["original_ches_line_text"].strip()
            ):
                raise CHESArchiveError("PRIVATE_SOURCE_SPAN_STRUCTURE_INVALID")
    if spans_seen != doc["ches_pdf_green_spans"]:
        raise CHESArchiveError("SOURCE_SPAN_TOTAL_MISMATCH")
    return len(verses), spans_seen, index_sha, original_sha


def audit_private_archive(directory: Path, *, require_929: bool = False) -> dict[str, Any]:
    """Audit existing private JSON; never fetch, modify, align or publish data."""
    path = directory.expanduser()
    if ".olt-private" not in path.parts or not path.is_dir():
        raise CHESArchiveError("PRIVATE_ARCHIVE_DIRECTORY_REQUIRED")
    if any(entry.is_symlink() for entry in (path, *path.parents)):
        raise CHESArchiveError("SYMLINKED_PRIVATE_DIRECTORY_REFUSED")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise CHESArchiveError("PRIVATE_DIRECTORY_PERMISSIONS_TOO_BROAD")

    records: dict[str, list[int]] = {}
    original_hashes: set[str] = set()
    index_hashes: set[str] = set()
    files = verses = spans = 0

    for source_path in sorted(path.iterdir()):
        if source_path.is_symlink() or not source_path.is_file():
            raise CHESArchiveError("UNEXPECTED_OR_SYMLINKED_PRIVATE_ENTRY")
        match = FILENAME.fullmatch(source_path.name)
        if match is None:
            raise CHESArchiveError("UNKNOWN_PRIVATE_ARCHIVE_FILENAME")
        if stat.S_IMODE(source_path.stat().st_mode) & 0o077:
            raise CHESArchiveError("PRIVATE_CHAPTER_PERMISSIONS_TOO_BROAD")
        if not 0 < source_path.stat().st_size <= MAX_JSON_BYTES:
            raise CHESArchiveError("INVALID_PRIVATE_CHAPTER_FILE_SIZE")

        prefix, chapter_text = match.groups()
        chapter = int(chapter_text)
        if chapter > 250:
            raise CHESArchiveError("UNEXPECTED_CHAPTER_NUMBER")
        try:
            doc = json.loads(
                source_path.read_text(encoding="utf-8"),
                object_pairs_hook=_strict_json_pairs,
                parse_constant=lambda _value: (_ for _ in ()).throw(
                    CHESArchiveError("INVALID_NONFINITE_JSON_VALUE")
                ),
            )
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise CHESArchiveError("INVALID_PRIVATE_JSON") from exc
        count_verses, count_spans, index_sha, pdf_sha = _validate_chapter(
            doc, prefix=prefix, chapter=chapter
        )
        if pdf_sha in original_hashes:
            raise CHESArchiveError("DUPLICATE_ORIGINAL_SOURCE_PDF_SHA")
        original_hashes.add(pdf_sha)
        index_hashes.add(index_sha)
        records.setdefault(prefix, []).append(chapter)
        files += 1
        verses += count_verses
        spans += count_spans
        if files > CHAPTERS_EXPECTED or len(records) > PREFIXES_EXPECTED:
            raise CHESArchiveError("IMPOSSIBLE_ORIGINAL_INDEX_COVERAGE")

    if not files:
        raise CHESArchiveError("PRIVATE_ARCHIVE_EMPTY")
    if len(index_hashes) != 1:
        raise CHESArchiveError("MIXED_ORIGINAL_SOURCE_INDEX_SNAPSHOTS")
    for chapters in records.values():
        if chapters != list(range(1, len(chapters) + 1)):
            raise CHESArchiveError("MISSING_DUPLICATE_OR_UNORDERED_SOURCE_CHAPTER")
    count_complete = (
        files == CHAPTERS_EXPECTED and len(records) == PREFIXES_EXPECTED
    )
    if require_929 and not count_complete:
        raise CHESArchiveError("FULL_929_CHAPTER_COUNT_NOT_REACHED")
    return {
        "checkpoint": "CHES-LOCAL-001",
        "read_only_private_archive_audit": True,
        "private_source_chapter_json_files_observed": files,
        "distinct_original_filename_prefixes_observed": len(records),
        "original_pdf_verse_markers_recorded": verses,
        "private_ches_green_typography_spans_recorded_not_word_aligned": spans,
        "single_source_index_hash_across_local_files": True,
        "expected_original_chapters": CHAPTERS_EXPECTED,
        "expected_original_prefixes": PREFIXES_EXPECTED,
        "full_929_39_coverage_by_count_only": count_complete,
        "full_index_membership_independently_verified": False,
        "original_pdf_bytes_rehashed_by_this_audit": False,
        "original_hebrew_verse_counts_independently_verified": False,
        "hebrew_to_english_word_alignment_verified": False,
        "english_olt_translation_owner_approved": False,
        "private_source_english_text_in_output": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline metadata-only audit of local private CHES JSON"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--require-929", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        audit_private_archive(args.private_root, require_929=args.require_929),
        sort_keys=True, indent=2
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
