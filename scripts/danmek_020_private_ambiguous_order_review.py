"""DANMEK-020: private, non-mutating exception queue for ambiguous English order.

Owner-verified DANMEK-013/014 reading is NEVER changed. Imported OSHB/WLC
verses are provisional same-reference research candidates ONLY, NOT an
independently certified CHES-to-OSHB book/verse/word crosswalk. Private
CHES English and original tokens are written only on explicit opt-in, never
to stdout, GitHub, CI logs or public artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

from olt_core.sources import load_ot_book, ot_morph_language, read_provenance
from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import (
    NAME, build_private_reader,
)
from scripts.danmek_011_owner_order import apply_owner_approved_candidates

REVISION = "DANMEK-020-PRIVATE-AMBIGUOUS-ORDER-REVIEW-v1"
MAX_AMBIGUOUS_CASES = 2500

# Explicit RESEARCH-ONLY source-code proposals, not verified crosswalks.
# The authentic CHES index validates prefix/chapter IDs, NOT these OT book IDs.
SOURCE_BOOK_CANDIDATES = {
    "1ch": "1Chr", "1kg": "1Kgs", "1sa": "1Sam",
    "2ch": "2Chr", "2kg": "2Kgs", "2sa": "2Sam",
    "amo": "Amos", "can": "Song", "dan": "Dan", "deu": "Deut",
    "est": "Esth", "exo": "Exod", "eze": "Ezek", "ezr": "Ezra",
    "gen": "Gen", "hab": "Hab", "hag": "Hag", "hos": "Hos",
    "isa": "Isa", "jdg": "Judg", "jer": "Jer", "job": "Job",
    "joe": "Joel", "jon": "Jonah", "jos": "Josh", "lam": "Lam",
    "lev": "Lev", "mal": "Mal", "mic": "Mic", "nah": "Nah",
    "neh": "Neh", "num": "Num", "oba": "Obad", "pro": "Prov",
    "psa": "Ps", "qoh": "Eccl", "rut": "Ruth", "zec": "Zech",
    "zep": "Zeph",
}


class DanMek020Error(ValueError):
    """Fixed-code error; no source words or private paths in diagnostics."""


def _private_write_once(folder: Path, filename: str, data: bytes) -> str:
    """Safely commit immutable 0600 private output without replacing a file."""
    if folder.is_symlink():
        raise DanMek020Error("PRIVATE_REVIEW_QUEUE_DIRECTORY_SYMLINK")
    if folder.exists():
        if not folder.is_dir() or stat.S_IMODE(folder.stat().st_mode) & 0o077:
            raise DanMek020Error("PRIVATE_REVIEW_QUEUE_DIRECTORY_UNSAFE")
    else:
        folder.mkdir(mode=0o700)
    target = folder / filename
    if target.is_symlink():
        raise DanMek020Error("PRIVATE_REVIEW_QUEUE_FILE_SYMLINK")
    if target.exists():
        if (not target.is_file() or stat.S_IMODE(target.stat().st_mode) & 0o077
                or target.read_bytes() != data):
            raise DanMek020Error("PRIVATE_REVIEW_QUEUE_DIFFERENT_NO_OVERWRITE")
        return "EXISTING_IDENTICAL_PRIVATE_QUEUE"
    fd, temp_name = tempfile.mkstemp(
        prefix=".danmek020-", suffix=".tmp", dir=folder
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o600)
        # Hard-link is exclusive. Never replace an existing/reviewed queue.
        try:
            os.link(temp_name, target, follow_symlinks=False)
        except FileExistsError as exc:
            raise DanMek020Error("PRIVATE_REVIEW_QUEUE_RACE_NO_OVERWRITE") from exc
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return "NEW_PRIVATE_QUEUE"


def _original_candidate(
    *, original_book: str, reference: str, by_reference: dict[str, dict],
) -> tuple[dict, bool]:
    """Return a review-only matching ORIGINAL verse, never an alignment."""
    source = by_reference.get(reference)
    if source is None:
        return {
            "status": "NO_SAME_REFERENCE_ORIGINAL_VERSE_FOUND",
            "candidate_book_mapping_verified": False,
            "original_to_ches_word_alignment_verified": False,
            "original_source_words_unaligned": [],
        }, False
    words = source.get("words")
    if not isinstance(words, list) or not words:
        raise DanMek020Error("MALFORMED_ORIGINAL_SOURCE_VERSE")
    visible_words = []
    for index, word in enumerate(words, 1):
        if (word.get("reference") != reference or word.get("ordinal") != index
                or word.get("source_status") != "IMPORTED_UNREVIEWED"
                or not isinstance(word.get("source_id"), str)
                or not isinstance(word.get("hebrew"), str)
                or not word["hebrew"]
                or not isinstance(word.get("morph_raw"), str)
                or not isinstance(word.get("lemma_raw"), str)):
            raise DanMek020Error("MALFORMED_ORIGINAL_SOURCE_TOKEN")
        visible_words.append({
            "source_token_id": word["source_id"],
            "ordinal": index,
            "original_script": word["hebrew"],
            "source_language_candidate": ot_morph_language(word["morph_raw"]),
            "raw_morphology_unreviewed": word["morph_raw"],
            "raw_lemma_annotation_unreviewed": word["lemma_raw"],
            "word_alignment_verified": False,
        })
    return {
        "status": "SAME_REFERENCE_ORIGINAL_SOURCE_CANDIDATE_UNREVIEWED",
        "candidate_original_book": original_book,
        "candidate_source_ref": reference,
        "candidate_book_mapping_verified": False,
        "original_to_ches_word_alignment_verified": False,
        "original_source_words_unaligned": visible_words,
    }, True


def build_ambiguous_order_queue(
    private_root: Path, *, write_private: bool = False,
    require_311: bool = False,
) -> dict:
    """Build original-source research candidates for all ambiguous English verses.

    Default: audit-only (no files). Optional output: private immutable JSON
    with licensed English and imported source Hebrew/Aramaic, both unaligned.
    This tool NEVER applies edits, changes the owner-verified reader, or
    marks original-language subjects as reviewed.
    """
    if type(write_private) is not bool or type(require_311) is not bool:
        raise DanMek020Error("INVALID_PRIVATE_REVIEW_QUEUE_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        baseline = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        registry = read_provenance()
        available_books = {row["book"] for row in registry["ot"]["books"]}
        if set(SOURCE_BOOK_CANDIDATES.values()) != available_books:
            raise DanMek020Error("SOURCE_BOOK_CANDIDATE_REGISTRY_CHANGED")

        records = []
        prefixes: dict[str, int] = {}
        candidate_found = 0
        original_missing = 0
        current_prefix: str | None = None
        original_by_reference: dict[str, dict] = {}
        for file in sorted(folder.iterdir(), key=lambda f: f.name):
            found = NAME.fullmatch(file.name)
            if found is None:
                raise DanMek020Error("PRIVATE_SOURCE_ARCHIVE_ENTRY_UNEXPECTED")
            prefix, chapter_text = found.groups()
            chapter = int(chapter_text)
            original_book = SOURCE_BOOK_CANDIDATES.get(prefix)
            if original_book is None:
                raise DanMek020Error("PRIVATE_SOURCE_BOOK_PREFIX_UNMAPPED")
            if prefix != current_prefix:
                original = load_ot_book(original_book, registry=registry)
                by_reference = {
                    row["reference"]: row for row in original["verses"]
                }
                if len(by_reference) != len(original["verses"]):
                    raise DanMek020Error("DUPLICATE_ORIGINAL_SOURCE_VERSE_IDS")
                original_by_reference = by_reference
                current_prefix = prefix

            source, source_hash = _load_private_source(
                folder, prefix=prefix, chapter=chapter,
            )
            for row in source["verses"]:
                reference = row["reference"]
                original_text = [
                    part["original_ches_line_text"]
                    for part in row["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                visible, reason = apply_owner_approved_candidates(
                    reference=reference, chapter_sha256=source_hash,
                    original=original_text, visible=list(original_text),
                )
                if reason != "AMBIGUOUS":
                    continue
                if visible != original_text:
                    raise DanMek020Error("AMBIGUOUS_READER_TEXT_MUTATION")
                if len(records) >= MAX_AMBIGUOUS_CASES:
                    raise DanMek020Error("TOO_MANY_AMBIGUOUS_CASES")
                # Candidate mapping from CHES prefix to original-language
                # book code is NOT source-verified; never silently certify.
                original_ref = (
                    original_book + "." + str(chapter) + "." +
                    reference.rsplit(".", 1)[-1]
                )
                evidence, available = _original_candidate(
                    original_book=original_book, reference=original_ref,
                    by_reference=original_by_reference,
                )
                candidate_found += int(available)
                original_missing += int(not available)
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                records.append({
                    "source_ches_verse_reference": reference,
                    "source_ches_chapter_json_sha256": source_hash,
                    "private_source_english_fragments_unaligned": [
                        {"fragment_ordinal": i, "private_ches_text": text}
                        for i, text in enumerate(original_text, 1)
                    ],
                    "english_order_status":
                        "AMBIGUOUS_MULTIPLE_PATTERNS_UNCHANGED",
                    "english_order_edit_proposed": False,
                    "human_original_language_subject_review": "NOT_DONE",
                    "original_source_verse_candidate": evidence,
                    "source_english_fragment_to_original_word_links": [],
                    "source_to_original_book_mapping_verified": False,
                    "original_source_subject_verified": False,
                    "word_alignment_verified": False,
                    "reorder_permitted": False,
                    "publication_status": "BLOCKED",
                })

        repeated = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        if baseline != repeated:
            raise DanMek020Error("PRIVATE_ARCHIVE_CHANGED_DURING_REVIEW")
        expected = baseline["olt_owner_candidate_ambiguous_verses_unchanged"]
        if len(records) != expected:
            raise DanMek020Error("AMBIGUOUS_COUNT_DIFFERS_FROM_LOCKED_READER")
        if require_311 and len(records) != 311:
            raise DanMek020Error("OWNER_REPORTED_311_COUNT_MISMATCH")
        if candidate_found + original_missing != len(records):
            raise DanMek020Error("ORIGINAL_CANDIDATE_COUNT_MISMATCH")

        private_status = "AUDIT_ONLY_NO_PRIVATE_QUEUE_WRITTEN"
        if write_private:
            payload = {
                "checkpoint": REVISION,
                "scope": "PRIVATE_ENGLISH_WORD_ORDER_EXCEPTION_REVIEW",
                "reader_snapshot_id": baseline["snapshot_id"],
                "source_verse_count": baseline["observed_verse_count"],
                "total_ambiguous_cases": len(records),
                "original_verse_locator_candidates_unreviewed": candidate_found,
                "original_verse_locators_missing": original_missing,
                "source_book_prefix_crosswalk_verified": False,
                "hebrew_aramaic_word_alignment_verified": False,
                "approved_english_reorders_from_queue": 0,
                "owner_approved_reader_mutated": False,
                "original_source_files_modified": False,
                "human_review_complete": False,
                "publication_status": "BLOCKED",
                "cases": records,
            }
            data = (
                json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            ).encode("utf-8")
            digest = hashlib.sha256(data).hexdigest()[:20]
            filename = REVISION.lower() + "-" + digest + ".json"
            private_status = _private_write_once(
                folder.parent / "ches-order-review", filename, data,
            )
        return {
            "checkpoint": REVISION,
            "mode": "OFFLINE_PRIVATE_ENGLISH_EXCEPTION_QUEUE",
            "reader_snapshot_id": baseline["snapshot_id"],
            "source_verses_seen": baseline["observed_verse_count"],
            "ambiguous_english_verses_queued": len(records),
            "original_source_same_reference_candidates_unreviewed": candidate_found,
            "original_source_reference_missing": original_missing,
            "by_source_prefix_ambiguous_count": dict(sorted(prefixes.items())),
            "source_book_mapping_independently_verified": False,
            "original_source_word_alignment_verified": False,
            "original_language_subject_verified": False,
            "english_reorders_applied": 0,
            "owner_verified_english_html_changed": False,
            "private_source_json_modified": False,
            "private_chapter_text_printed": False,
            "private_output_status": private_status,
            "publication_status": "BLOCKED",
        }
    except DanMek020Error:
        raise
    except Exception as exc:
        raise DanMek020Error("PRIVATE_AMBIGUITY_REVIEW_AUDIT_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline private English ambiguity triage, no reader edits"
    )
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument(
        "--confirm-machine-readable-use-permission", action="store_true",
    )
    parser.add_argument(
        "--write-private-queue", action="store_true",
        help="Create immutable 0600 queue including private source English and provisional original verses",
    )
    parser.add_argument(
        "--require-311", action="store_true",
        help="Fail unless actual current source/reader has 311 ambiguities",
    )
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private machine-readable source-use permission required")
    try:
        result = build_ambiguous_order_queue(
            args.private_root, write_private=args.write_private_queue,
            require_311=args.require_311,
        )
    except DanMek020Error:
        parser.exit(2, "DANMEK_020_PRIVATE_AMBIGUITY_REVIEW_FAILED\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
