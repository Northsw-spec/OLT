"""DANMEK-016: offline, metadata-only OT English reader coverage QA.

Never export CHES text, YLT text, source file paths, verse strings, or
unapproved drafts. The owner-verified DANMEK-014 HTML reader is untouched.
This audits the same exact display options, without creating any HTML.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import (
    NAME, build_private_reader,
)
from scripts.ches_local_archive_audit import (
    CHAPTERS_EXPECTED, PREFIXES_EXPECTED,
)
from scripts.danmek_008_english_display import simplify_sur_faces_for_olt_view
from scripts.danmek_011_owner_order import apply_owner_approved_candidates
from scripts.danmek_012_display import hide_isolated_c
from scripts.danmek_ylt import load_private_ylt, propose_ylt_verse_overrides


class DanMek016Error(ValueError):
    """Never report private source text or a private filesystem location."""


def _new_source_prefix_counters() -> dict:
    return {
        "chapters_observed": 0,
        "verses_observed": 0,
        "ches_english_source_fragments_observed": 0,
        "owner_order_candidates_applied": 0,
        "ambiguous_order_verses_unchanged": 0,
        "ylt_order_overlap_verses_unchanged": 0,
        "verses_without_order_candidate": 0,
        "faces_display_simplifications": 0,
        "lowercase_c_letters_hidden": 0,
        "whole_lowercase_c_fragments_hidden": 0,
        "verses_with_at_least_one_visible_edit": 0,
        "verses_without_a_visible_edit": 0,
        "ylt_noun_edits": 0,
        "ylt_tense_edits": 0,
        "ylt_unmapped_verses": 0,
        "ylt_ambiguous_verses": 0,
    }


def audit_private_english_coverage(
    private_root: Path, *, use_ylt_authority: bool = False,
    require_929: bool = False,
) -> dict:
    """Inspect all locally available OT CHES chapters, without writing files.

    A first and last invocation of the known CHES-015 validator makes the
    report reject source mutations during inspection. The detailed pass
    repeats source validation and exactly reproduces its display transforms.
    Report only aggregate counters by untrusted source filename prefix
    (never call those canonical/verified Bible book identifiers).
    """
    if type(use_ylt_authority) is not bool or type(require_929) is not bool:
        raise DanMek016Error("INVALID_PRIVATE_COVERAGE_OPTIONS")

    try:
        baseline = build_private_reader(
            private_root, render=False, use_ylt_authority=use_ylt_authority,
            olt_display_faces=True, olt_owner_approved_candidates=True,
        )
        if require_929 and not baseline["all_929_39_present_by_count_only"]:
            raise DanMek016Error("FULL_929_39_COUNT_NOT_REACHED")

        folder = _private_archive_root(private_root)
        ylt = load_private_ylt(folder)[0] if use_ylt_authority else None

        by_prefix: dict[str, dict] = {}
        present_chapters: dict[str, set[int]] = {}

        for path in sorted(folder.iterdir(), key=lambda p: p.name):
            found = NAME.fullmatch(path.name)
            if found is None:
                raise DanMek016Error("UNKNOWN_PRIVATE_SOURCE_ENTRY")
            prefix, number = found.group(1), int(found.group(2))
            source, sha256 = _load_private_source(
                folder, prefix=prefix, chapter=number,
            )
            counters = by_prefix.setdefault(prefix, _new_source_prefix_counters())
            present_chapters.setdefault(prefix, set()).add(number)
            counters["chapters_observed"] += 1

            edits = {}
            if use_ylt_authority:
                edits, stats = propose_ylt_verse_overrides(
                    source, prefix=prefix, chapter=number, ylt=ylt,
                )
                counters["ylt_noun_edits"] += stats["noun_changes"]
                counters["ylt_tense_edits"] += stats["tense_changes"]
                counters["ylt_unmapped_verses"] += stats[
                    "unmapped_verses_left_unchanged"
                ]
                counters["ylt_ambiguous_verses"] += stats[
                    "ambiguous_verses_left_unchanged"
                ]

            for verse in source["verses"]:
                ref = verse["reference"]
                original = [
                    span["original_ches_line_text"] for span in
                    verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                visible = [
                    edits.get((ref, index), text)
                    for index, text in enumerate(original, 1)
                ]
                changed_by_ylt = any(
                    (ref, index) in edits
                    for index in range(1, len(original) + 1)
                )
                moved, reason = apply_owner_approved_candidates(
                    reference=ref, chapter_sha256=sha256,
                    original=original, visible=visible,
                )
                reasons = {
                    "APPLIED": "owner_order_candidates_applied",
                    "AMBIGUOUS": "ambiguous_order_verses_unchanged",
                    "YLT_OVERLAP": "ylt_order_overlap_verses_unchanged",
                    "NO_CANDIDATE": "verses_without_order_candidate",
                }
                if reason not in reasons:
                    raise DanMek016Error("UNKNOWN_ENGLISH_ORDER_AUDIT_REASON")
                counters[reasons[reason]] += 1
                faces_view, face_count = simplify_sur_faces_for_olt_view(moved)
                cleaned, c_letters = hide_isolated_c(faces_view)
                hidden_fragments = sum(
                    before is not None and after is None
                    for before, after in zip(faces_view, cleaned)
                )
                counters["faces_display_simplifications"] += face_count
                counters["lowercase_c_letters_hidden"] += c_letters
                counters["whole_lowercase_c_fragments_hidden"] += hidden_fragments
                counters["verses_observed"] += 1
                counters["ches_english_source_fragments_observed"] += len(original)

                if changed_by_ylt or reason == "APPLIED" or face_count or c_letters:
                    counters["verses_with_at_least_one_visible_edit"] += 1
                else:
                    counters["verses_without_a_visible_edit"] += 1

        for prefix, chapters in present_chapters.items():
            # Only *internal* missing numbers up to the observed last
            # chapter; the real book's final chapter count is not attested.
            by_prefix[prefix]["internal_chapter_number_gaps_observed"] = (
                max(chapters) - len(chapters)
            )
            by_prefix[prefix]["first_chapter_number_observed"] = min(chapters)
            by_prefix[prefix]["last_chapter_number_observed"] = max(chapters)

        repeated = build_private_reader(
            private_root, render=False, use_ylt_authority=use_ylt_authority,
            olt_display_faces=True, olt_owner_approved_candidates=True,
        )
        if repeated != baseline:
            raise DanMek016Error("PRIVATE_SOURCE_CHANGED_DURING_COVERAGE_AUDIT")

        consistency = {
            "observed_chapter_count": "chapters_observed",
            "observed_verse_count": "verses_observed",
            "observed_source_fragment_count":
                "ches_english_source_fragments_observed",
            "olt_owner_approved_candidate_reorders_applied":
                "owner_order_candidates_applied",
            "olt_owner_candidate_ambiguous_verses_unchanged":
                "ambiguous_order_verses_unchanged",
            "olt_owner_candidate_ylt_conflicts_unchanged":
                "ylt_order_overlap_verses_unchanged",
            "olt_display_sur_faces_to_faces_count":
                "faces_display_simplifications",
            "olt_standalone_lowercase_c_letters_hidden":
                "lowercase_c_letters_hidden",
            "olt_isolated_lowercase_c_fragments_hidden":
                "whole_lowercase_c_fragments_hidden",
            "ylt_noun_edit_count": "ylt_noun_edits",
            "ylt_tense_edit_count": "ylt_tense_edits",
            "ylt_verses_unmapped_left_unchanged": "ylt_unmapped_verses",
            "ylt_ambiguous_verses_left_unchanged": "ylt_ambiguous_verses",
        }
        for from_reader, from_prefix in consistency.items():
            total = sum(row[from_prefix] for row in by_prefix.values())
            if total != baseline[from_reader]:
                raise DanMek016Error("PRIVATE_COVERAGE_READER_COUNTER_MISMATCH")
        if len(by_prefix) != baseline["observed_source_prefix_groups"]:
            raise DanMek016Error("PRIVATE_COVERAGE_PREFIX_COUNT_MISMATCH")

        return {
            "checkpoint": "DANMEK-016-PRIVATE-OT-ENGLISH-COVERAGE-v1",
            "mode": "OFFLINE_METADATA_ONLY_READ_ONLY",
            "reader_snapshot_id": baseline["snapshot_id"],
            "source_english_fragments_are_not_olt_translation": True,
            "observed_chapters": baseline["observed_chapter_count"],
            "expected_ot_chapters_by_count": CHAPTERS_EXPECTED,
            "observed_source_prefixes_not_verified_book_ids": len(by_prefix),
            "expected_source_prefixes_by_count": PREFIXES_EXPECTED,
            "observed_verses": baseline["observed_verse_count"],
            "observed_source_english_fragments":
                baseline["observed_source_fragment_count"],
            "all_929_39_present_by_count_only":
                baseline["all_929_39_present_by_count_only"],
            "source_index_membership_independently_verified": False,
            "source_prefixes_verified_as_canonical_book_ids": False,
            "private_english_corpus_fully_visually_reviewed": False,
            "hebrew_english_word_alignment_or_syntax_verified": False,
            "original_pdf_bytes_rehashed_in_this_audit": False,
            "ylt_authority_used": use_ylt_authority,
            "owner_approved_display_mode_evaluated": True,
            "display_is_not_independent_english_translation": True,
            "source_or_private_html_files_created": 0,
            "original_private_chapter_json_files_modified": 0,
            "private_source_words_in_output": False,
            "per_source_filename_prefix": dict(sorted(by_prefix.items())),
            "publication_status": "BLOCKED",
        }
    except DanMek016Error:
        raise
    except Exception as exc:
        # Sanitized: never leak a fragment or local path via CLI or audit.
        raise DanMek016Error("PRIVATE_COVERAGE_AUDIT_FAILED") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Private offline metadata-only English OT coverage audit"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument(
        "--confirm-machine-readable-use-permission", action="store_true",
    )
    parser.add_argument(
        "--use-ylt-authority", action="store_true",
        help="Match the reader's opt-in pinned private YLT overlay mode",
    )
    parser.add_argument(
        "--require-929", action="store_true",
        help="Require 929 CHES chapter files and 39 source prefixes by count only",
    )
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Owner-reported private machine-readable use permission required")
    try:
        result = audit_private_english_coverage(
            args.private_root, use_ylt_authority=args.use_ylt_authority,
            require_929=args.require_929,
        )
    except DanMek016Error:
        parser.exit(2, "DANMEK_016_PRIVATE_METADATA_COVERAGE_AUDIT_FAILED\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
