"""DANMEK-017: compare private CHES chapter inventory to a supplied OT PDF index.

Offline, read-only and metadata-only. The supplied index is locally sourced,
not independently authenticated; matching its SHA is not proof of Biblical
book mapping, Hebrew word alignment, original PDF contents or publication rights.
No original index HTML or third-party words may enter public Git/CI logs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat

from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import NAME, build_private_reader
from scripts.ches_index import parse_index
from scripts.ches_local_archive_audit import CHAPTERS_EXPECTED, PREFIXES_EXPECTED

MAX_INDEX_HTML_BYTES = 3_000_000


class DanMek017Error(ValueError):
    """Fixed public diagnostics; never expose private files or source lines."""


def _read_private_index(index_path: Path, source_folder: Path) -> bytes:
    if not isinstance(index_path, Path):
        raise DanMek017Error("PRIVATE_SOURCE_INDEX_PATH_REQUIRED")
    path = index_path.expanduser()
    if (not path.is_absolute() or ".olt-private" not in path.parts
            or path.parent == source_folder or source_folder in path.parents
            or not path.is_file() or path.is_symlink()):
        raise DanMek017Error("PRIVATE_SOURCE_INDEX_PATH_UNSAFE")
    for parent in path.parents:
        if parent.is_symlink():
            raise DanMek017Error("PRIVATE_SOURCE_INDEX_PARENT_SYMLINK")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise DanMek017Error("PRIVATE_SOURCE_INDEX_PERMISSIONS_TOO_BROAD")
    size = path.stat().st_size
    if not 0 < size <= MAX_INDEX_HTML_BYTES:
        raise DanMek017Error("PRIVATE_SOURCE_INDEX_INVALID_SIZE")
    raw = path.read_bytes()
    if len(raw) != size:
        raise DanMek017Error("PRIVATE_SOURCE_INDEX_CHANGED_ON_READ")
    return raw


def audit_private_index_membership(
    private_root: Path, index_path: Path, *, require_complete: bool = False,
) -> dict:
    """Compare present private chapter IDs against a same-SHA local PDF index.

    The index HTML is provided by the user and NOT independently downloaded
    or authenticated here. A 929/39 inventory can still omit/forge sources;
    membership in the supplied index is all that this tool can attest.
    """
    if type(require_complete) is not bool:
        raise DanMek017Error("INVALID_SOURCE_MEMBERSHIP_AUDIT_OPTION")
    try:
        folder = _private_archive_root(private_root)
        raw = _read_private_index(index_path, folder)
        source_index = parse_index(raw)
        if (source_index["discovered_chapter_pdf_count"] != CHAPTERS_EXPECTED
                or source_index[
                    "discovered_original_source_filename_prefix_count"
                ] != PREFIXES_EXPECTED
                or source_index[
                    "book_prefixes_are_not_approved_oshb_book_mappings"
                ] is not True
                or source_index[
                    "rights_for_public_CHES_data_export_confirmed"
                ] is not False):
            raise DanMek017Error("UNEXPECTED_LOCAL_SOURCE_INDEX_INVENTORY")
        index_sha = hashlib.sha256(raw).hexdigest()

        expected_by_prefix: dict[str, set[int]] = {}
        for item in source_index["chapter_links"]:
            prefix = item["source_book_filename_prefix_NOT_OLT_BOOK_ID"]
            number = item["source_chapter_filename_number"]
            expected_by_prefix.setdefault(prefix, set()).add(number)
        expected = {
            (prefix, number) for prefix, numbers in expected_by_prefix.items()
            for number in numbers
        }
        if len(expected) != CHAPTERS_EXPECTED:
            raise DanMek017Error("DUPLICATE_OR_MISSING_SOURCE_INDEX_IDS")

        baseline = build_private_reader(folder, render=False)
        present: set[tuple[str, int]] = set()
        present_by_prefix: dict[str, set[int]] = {}
        for file in sorted(folder.iterdir(), key=lambda p: p.name):
            found = NAME.fullmatch(file.name)
            if found is None:
                raise DanMek017Error("UNEXPECTED_PRIVATE_CHAPTER_FILE")
            prefix, chapter = found.group(1), int(found.group(2))
            if (prefix, chapter) not in expected:
                raise DanMek017Error("LOCAL_SOURCE_CHAPTER_NOT_IN_SUPPLIED_INDEX")
            document, _ = _load_private_source(
                folder, prefix=prefix, chapter=chapter,
            )
            if document["source_original_index_sha256"] != index_sha:
                raise DanMek017Error("LOCAL_SOURCE_INDEX_SHA_MISMATCH")
            present.add((prefix, chapter))
            present_by_prefix.setdefault(prefix, set()).add(chapter)

        if len(present) != baseline["observed_chapter_count"]:
            raise DanMek017Error("PRIVATE_READER_CHAPTER_TOTAL_MISMATCH")
        missing = expected - present
        if require_complete and missing:
            raise DanMek017Error("LOCAL_SOURCE_INDEX_NOT_FULLY_IMPORTED")

        repeated = build_private_reader(folder, render=False)
        if baseline != repeated or index_path.expanduser().read_bytes() != raw:
            raise DanMek017Error("PRIVATE_INDEX_OR_SOURCE_CHANGED_DURING_AUDIT")

        result_by_prefix = {}
        for prefix, numbers in sorted(expected_by_prefix.items()):
            local = present_by_prefix.get(prefix, set())
            result_by_prefix[prefix] = {
                "chapter_links_in_supplied_index": len(numbers),
                "private_chapter_json_files_present": len(local),
                "index_chapters_missing_locally": len(numbers - local),
                "all_index_chapters_present_locally": local == numbers,
            }

        return {
            "checkpoint": "DANMEK-017-LOCAL-SOURCE-INDEX-MEMBERSHIP-v1",
            "mode": "OFFLINE_METADATA_ONLY_READ_ONLY",
            "validated_local_reader_snapshot_id": baseline["snapshot_id"],
            "supplied_index_sha256": index_sha,
            "locally_supplied_index_count": len(expected),
            "locally_supplied_index_filename_prefix_count":
                len(expected_by_prefix),
            "private_chapter_json_files_observed": len(present),
            "present_chapter_ids_found_in_supplied_index": len(present),
            "supplied_index_chapter_ids_missing_locally": len(missing),
            "all_supplied_index_chapter_ids_present_locally": not missing,
            "all_local_chapter_index_sha_values_match_supplied_index": True,
            "supplied_index_originality_independently_authenticated": False,
            "pdf_source_bytes_independently_rehashed": False,
            "english_to_original_hebrew_alignment_verified": False,
            "source_filename_prefix_is_verified_biblical_book_id": False,
            "complete_english_bible_translation_owner_approved": False,
            "private_files_read_only": True,
            "private_text_exported": False,
            "private_files_written": 0,
            "per_source_filename_prefix": result_by_prefix,
            "publication_status": "BLOCKED",
        }
    except DanMek017Error:
        raise
    except Exception as exc:
        raise DanMek017Error("PRIVATE_SOURCE_INDEX_MEMBERSHIP_AUDIT_FAILED") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only private CHES inventory versus supplied OT index HTML"
    )
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument("--source-index", required=True, type=Path)
    parser.add_argument(
        "--confirm-machine-readable-use-permission", action="store_true",
    )
    parser.add_argument(
        "--require-index-complete", action="store_true",
        help="Fail if any source chapter listed in the supplied local index is missing",
    )
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Owner-reported private machine-readable use permission required")
    try:
        result = audit_private_index_membership(
            args.private_root, args.source_index,
            require_complete=args.require_index_complete,
        )
    except DanMek017Error:
        parser.exit(2, "DANMEK_017_PRIVATE_INDEX_AUDIT_FAILED\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
