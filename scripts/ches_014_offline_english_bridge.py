"""CHES-014: offline private chapter JSON -> Hebrew-checked English working draft.

Reuses the established CHES-004 / CHES-007 small engine. No network, no PDF
refetch, no English source text in stdout, logs, source control or artifacts.
The original PDF SHA in locally imported JSON is compared with immutable
public engineering pins, but PDF BYTES ARE NOT rehashed in this offline step.
All draft text remains an unapproved private CHES gloss stream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat
from typing import Any

from olt_core.sources import ROOT
from scripts.ches_006_layout_metrics import PILOT
from scripts.ches_007_multichapter_english import build_private_pinned_english_chapter
from scripts.ches_008_private_batch import _source_pin
from scripts.ches_import import write_private_json
from scripts.ches_lite_english import build_private_genesis_one_english_drafts
from scripts.ches_local_archive_audit import (
    _strict_json_pairs, _validate_chapter, MAX_JSON_BYTES,
)

PREFIX_TO_BOOK = {"gen": "Gen", "exo": "Exod"}
BOOK_TO_PREFIX = {value: key for key, value in PREFIX_TO_BOOK.items()}
OUTPUT_FOLDER = "olt-english-drafts"


class CHES014BridgeError(ValueError):
    """Safe fixed-code error; never print licensed source text or local paths."""


def _private_archive_root(directory: Path) -> Path:
    folder = directory.expanduser()
    if (not folder.is_absolute() or folder.name != "ches" or
        folder.parent.name != ".olt-private" or not folder.is_dir()):
        raise CHES014BridgeError("PRIVATE_CHES_ARCHIVE_PATH_INVALID")
    for ancestor in (folder, *folder.parents):
        if ancestor.is_symlink():
            raise CHES014BridgeError("SYMLINKED_PRIVATE_PATH_REFUSED")
    if (stat.S_IMODE(folder.stat().st_mode) & 0o077 or
        stat.S_IMODE(folder.parent.stat().st_mode) & 0o077):
        raise CHES014BridgeError("PRIVATE_ARCHIVE_PERMISSIONS_TOO_BROAD")
    return folder


def _load_private_source(folder: Path, *, prefix: str, chapter: int) -> tuple[dict[str, Any], str]:
    source_path = folder / f"{prefix}.{chapter}.json"
    if source_path.is_symlink() or not source_path.is_file():
        raise CHES014BridgeError("PRIVATE_SOURCE_CHAPTER_MISSING_OR_SYMLINKED")
    if stat.S_IMODE(source_path.stat().st_mode) & 0o077:
        raise CHES014BridgeError("PRIVATE_SOURCE_PERMISSIONS_TOO_BROAD")
    size = source_path.stat().st_size
    if not 0 < size <= MAX_JSON_BYTES:
        raise CHES014BridgeError("PRIVATE_SOURCE_CHAPTER_SIZE_INVALID")
    data = source_path.read_bytes()
    if len(data) != size:
        raise CHES014BridgeError("PRIVATE_SOURCE_CHAPTER_CHANGED_DURING_READ")
    try:
        document = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_strict_json_pairs,
            parse_constant=lambda _value: (_ for _ in ()).throw(
                CHES014BridgeError("NONFINITE_PRIVATE_JSON_REFUSED")
            ),
        )
        _validate_chapter(document, prefix=prefix, chapter=chapter)
    except (UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise CHES014BridgeError("PRIVATE_SOURCE_CHAPTER_SCHEMA_INVALID") from exc
    return document, hashlib.sha256(data).hexdigest()


def _canonical_english_engine_source(
    source: dict[str, Any], *, book: str, chapter: int
) -> dict[str, Any]:
    """Converts only source *identifiers* after original-private schema QA.

    Never interprets a green PDF text span as a Hebrew word, never renumbers
    non-contiguous chapter sources and never rewrites the original JSON.
    """
    if (book, chapter) == ("Gen", 1):
        return source
    return {
        **source,
        "book": book,
        "verses": [
            {**row, "reference": f"{book}.{chapter}.{ordinal}"}
            for ordinal, row in enumerate(source["verses"], 1)
        ],
    }


def _private_output_path(source_folder: Path, *, prefix: str, chapter: int) -> Path:
    destination = source_folder.parent / OUTPUT_FOLDER
    if destination.is_symlink():
        raise CHES014BridgeError("SYMLINKED_PRIVATE_OUTPUT_REFUSED")
    if not destination.exists():
        destination.mkdir(mode=0o700)
    if not destination.is_dir() or stat.S_IMODE(destination.stat().st_mode) & 0o077:
        raise CHES014BridgeError("PRIVATE_OUTPUT_FOLDER_UNSAFE")
    target = destination / f"{prefix}.{chapter}.unapproved-english.json"
    if target.is_symlink():
        raise CHES014BridgeError("SYMLINKED_PRIVATE_DRAFT_REFUSED")
    if target.exists() and (
        not target.is_file() or stat.S_IMODE(target.stat().st_mode) & 0o077
    ):
        raise CHES014BridgeError("PRIVATE_DRAFT_FILE_UNSAFE")
    return target


def bridge_private_chapter(
    private_root: Path, *, book: str, chapter: int,
    write_private: bool = False, root: Path = ROOT,
) -> dict[str, Any]:
    """Generate one source-pinned *unapproved* English draft from local JSON.

    The result contains allowlisted metadata only. Actual English stays in the
    private output file, and existing differing drafts are never overwritten.
    """
    if (type(book) is not str or type(chapter) is not int or
        book not in BOOK_TO_PREFIX or (book, chapter) not in PILOT or
        type(write_private) is not bool):
        raise CHES014BridgeError("CHAPTER_NOT_IN_FOURTEEN_SOURCE_PINS")
    source_folder = _private_archive_root(private_root)
    prefix = BOOK_TO_PREFIX[book]
    source, source_json_sha = _load_private_source(
        source_folder, prefix=prefix, chapter=chapter
    )
    _, pin_key = PILOT[(book, chapter)]
    pinned = _source_pin(root, pin_key, book, chapter)
    if (source.get("source_origin_url") != pinned["original_pdf_url"] or
        source.get("original_source_pdf_sha256") != pinned["source_pdf_sha256"] or
        type(source.get("source_pdf_byte_length")) is not int or
        source["source_pdf_byte_length"] != pinned["source_pdf_bytes"] or
        type(source.get("source_pdf_page_count")) is not int or
        source["source_pdf_page_count"] != pinned["source_pdf_pages"] or
        type(source.get("verses_extracted")) is not int or
        source["verses_extracted"] != pinned["printed_pdf_verses_confirmed_by_engineering"] or
        type(source.get("ches_pdf_green_spans")) is not int or
        source["ches_pdf_green_spans"] != pinned["green_ches_pdf_spans_extracted"]):
        raise CHES014BridgeError("LOCALLY_RECORDED_SOURCE_DOES_NOT_MATCH_PIN")

    source_for_engine = _canonical_english_engine_source(
        source, book=book, chapter=chapter
    )
    if (book, chapter) == ("Gen", 1):
        draft = build_private_genesis_one_english_drafts(
            source_for_engine, root=root
        )
        verses = draft["genesis_verse_count"]
    else:
        draft = build_private_pinned_english_chapter(
            source_for_engine, root=root
        )
        verses = draft["verse_count"]
    if (draft.get("publication_status") != "BLOCKED" or
        draft.get("english_translation_owner_approved") is not False or
        draft.get("word_alignment_verified") is not False or
        draft.get("all_english_grammar_rules_applied") is not False or
        draft.get("private_editorial_verse_edits_unapproved") != 0):
        raise CHES014BridgeError("UNSAFE_ENGLISH_DRAFT_APPROVAL_GATE")
    draft["offline_private_source_json_sha256"] = source_json_sha
    draft["offline_private_source_index_sha256"] = source["source_original_index_sha256"]
    draft["offline_private_archive_bridge_checkpoint"] = "CHES-014"
    draft["original_pdf_bytes_rehashed_by_offline_bridge"] = False
    draft["private_archive_source_used_without_network"] = True

    state = "VALIDATED_AUDIT_ONLY_NOT_SAVED"
    if write_private:
        dest = _private_output_path(
            source_folder, prefix=prefix, chapter=chapter
        )
        expected = (
            json.dumps(draft, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        if dest.exists():
            if dest.read_bytes() != expected:
                raise CHES014BridgeError("EXISTING_PRIVATE_DRAFT_DIFFERENT_REFUSING_OVERWRITE")
            state = "EXISTING_IDENTICAL_PRIVATE_DRAFT_UNCHANGED"
        else:
            write_private_json(draft, dest)
            state = "NEW_PRIVATE_UNAPPROVED_DRAFT_WRITTEN"
    return {
        "checkpoint": "CHES-014",
        "scope": f"{book}.{chapter}",
        "source_pin_pdf_metadata_checked": True,
        "original_pdf_bytes_rehashed_by_this_bridge": False,
        "private_source_archive_record_sha256_observed": True,
        "original_source_index_membership_independently_reverified": False,
        "original_oshb_verse_ids_checked": verses,
        "original_oshb_word_tokens_observed_not_ches_aligned":
            draft["original_hebrew_token_count"],
        "original_pdf_green_text_spans_not_oshb_aligned":
            draft["original_ches_pdf_green_span_count"],
        "source_tagged_wayyiqtol_simple_past_requirements":
            draft["source_wayyiqtol_simple_past_requirements"],
        "source_lemma_override_candidates_not_applied":
            draft["owner_lexical_override_candidates_not_applied"],
        "private_output_state": state,
        "ches_to_oshb_word_alignment_verified": False,
        "english_grammar_rules_applied": False,
        "english_translation_owner_approved": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline private CHES JSON to unapproved English working draft"
    )
    parser.add_argument("--private-root", type=Path,
                        default=Path.home() / ".olt-private" / "ches")
    parser.add_argument("--book", required=True, choices=("Gen", "Exod"))
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--write-private-draft", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private authorized machine-readable source use required")
    try:
        report = bridge_private_chapter(
            args.private_root, book=args.book, chapter=args.chapter,
            write_private=args.write_private_draft,
        )
    except Exception:
        # Never put untrusted CHES content, Hebrew text, local paths or
        # operator drafts into exception tracebacks or public logs.
        parser.exit(2, "CHES-014_PRIVATE_SOURCE_OR_ENGLISH_DRAFT_VALIDATION_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
