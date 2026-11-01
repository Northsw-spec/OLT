"""DANMEK-034: owner-identified nonadjacent English subjects, private v4.

Two owner-provided ENGLISH context patterns are now authorized, independently
of the old automatic adjacent-noun heuristic. A general postverbal name is
NOT sufficient to prove a subject: "he-chose NAME" can mean NAME is an
object. Therefore the new movement requires *all* contextual anchors
specified by the owner and the correct named subject.

No Hebrew crosscheck, no CHES source edits, no modification of DANMEK-013/014
or DANMEK-027/028/030 reader snapshots or review/approval manifests. This is
a separately versioned opt-in English-only derived reading.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re

from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import (
    NAME as CHES_FILE_NAME, build_private_reader,
)
from scripts.danmek_027_multiclause_subject_first import (
    DanMek027Error, MAX_VERSE_CHARS, _safe_dir, _write_once,
)
from scripts.danmek_030_reviewed_english_subject_order import (
    _read_source_text,
)

REVISION = "DANMEK-034-OWNER-CROSS-CLAUSE-SUBJECT-ENGLISH-v1"
MAX_CHAPTERS = 1100
RULE_DAVID = "OWNER_DAVID_TWO_CLAUSE_SUBJECT_THREAD"
RULE_YAHWEH = "OWNER_YAHWEH_CHOOSER_WITH_LEVITES_CONTEXT"

# Narrow English-only context anchors are intentionally NOT a generic
# parser. The owner's exact editorial examples authorize the named David
# and Yahweh constructions, not arbitrary nouns after a transitive verb.
# Source clauses may be embedded in longer private verses.
_DAVID_CORE = re.compile(
    r"(?<![A-Za-z·-])(?P<first>and·he-is-becoming)"
    r"(?P<prefix>[ \t]+as·which[ \t]+)"
    r"(?P<embedded_subject>David)[ \t]*-[ \t]*"
    r"(?P<embedded_verb>he-sits)"
    r"(?P<between>[ \t]+in·house-of·him[ \t]+)"
    r"(?P<second>and·he-is-saying)[ \t]+"
    r"(?P<repeated_subject>David)"
    r"(?=[ \t]+to[ \t]+[A-Z][A-Za-z'’-]{1,49}"
    r"[ \t]+the·prophet(?:\b|[ \t]))"
)
_YAHWEH_CHOOSER = re.compile(
    r"(?<![A-Za-z·-])(?P<preamble>that[ \t]+in·them[ \t]+)"
    r"(?P<verb>he-chose)[ \t]+(?P<subject>Yahweh)"
    r"(?=[ \t]+to·to-carry-of(?:[ \t]|$))"
)

# One partial match is not enough. A Yahweh-object interpretation outside
# the specified agent context remains untouched, as does a different name.
_RULES = ((RULE_DAVID, _DAVID_CORE), (RULE_YAHWEH, _YAHWEH_CHOOSER))


class DanMek034Error(ValueError):
    """Fixed, private-data-safe error code only."""


def apply_owner_cross_clause_subjects(
    english: str,
) -> tuple[str, list[dict]]:
    """Return an English-only derived reading and precise move evidence.

    The complete owner-identified context (including the repeated David
    subject and the prophet recipient) must match. No adjacent heuristics
    or inferred personhood, gender, morphology or object roles.
    """
    if type(english) is not str or len(english) > MAX_VERSE_CHARS:
        raise DanMek034Error("INVALID_PRIVATE_OWNER_CROSS_CLAUSE_ENGLISH")
    edits: list[tuple[int, int, str, str, int]] = []
    for code, pattern in _RULES:
        for match in pattern.finditer(english):
            if code == RULE_DAVID:
                # Move the same *two* explicitly identified David mentions:
                # a distant subject belonging to "he-is-becoming", and
                # the repeated subject for "he-is-saying".
                replacement = (
                    "and David - ·he-is-becoming" +
                    match["prefix"].rstrip(" \t") +
                    " - " + match["embedded_verb"] +
                    match["between"] +
                    "and David -·he-is-saying"
                )
                count = 2
                if (match["embedded_subject"] != "David"
                        or match["repeated_subject"] != "David"):
                    raise DanMek034Error("CROSS_CLAUSE_SUBJECT_THREAD_MISMATCH")
            else:
                # The owner's second example: "Yahweh" is the agent of
                # he-chose in this constrained relative-clause context.
                replacement = (
                    match["preamble"] + match["subject"] + " - " + match["verb"]
                )
                count = 1
            left, right = match.span()
            if any(not (right <= l or left >= r) for l, r, _, _, _ in edits):
                raise DanMek034Error("OVERLAPPING_OWNER_CROSS_CLAUSE_RULES")
            if english[left:right] == replacement:
                continue
            edits.append((left, right, replacement, code, count))
    edits.sort()
    derived = english
    for left, right, replacement, _, _ in reversed(edits):
        derived = derived[:left] + replacement + derived[right:]
    evidence = [
        {
            "rule_code": code,
            "owner_status": "OWNER_IDENTIFIED_ENGLISH_CONTEXT",
            "original_english_start": left,
            "original_english_end": right,
            "owner_authorized_subject_moves": count,
            "hebrew_source_verified_again": False,
            "original_private_ches_modified": False,
        }
        for left, right, _, code, count in edits
    ]
    return derived, evidence


def _html_page(name: str, rows: list[tuple[str, str]]) -> bytes:
    sections = "".join(
        '<section><b>' + html.escape(ref, quote=True) + '</b> <span>' +
        html.escape(english, quote=True) + '</span></section>'
        for ref, english in rows
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        '<title>Private OLT English cross-clause reading</title>'
        '<style>body{font:17px/1.55 Georgia,serif;max-width:960px;'
        'margin:2rem auto;padding:1rem;background:#faf9f7;color:#222}'
        'section{padding:.6rem 0;border-bottom:1px solid #ccc}'
        'b{font:13px system-ui}span{white-space:pre-wrap;overflow-wrap:anywhere}'
        '</style></head><body>'
        '<h1>Private subject-first English v4 — ' +
        html.escape(name, quote=True) + '</h1>'
        '<p>Only two owner-identified English contexts are corrected beyond '
        'the guarded v2 reading. Other roles are not certified. '
        'CHES source and prior readers remain unchanged; '
        'publication BLOCKED.</p>' + sections + '</body></html>\n'
    ).encode("utf-8")


def build_private_owner_cross_clause_reader(
    private_root: Path, *, render: bool = False,
    require_311: bool = False,
) -> dict:
    """Build fresh independent private v4; never alter any previous version."""
    if type(render) is not bool or type(require_311) is not bool:
        raise DanMek034Error("INVALID_CROSS_CLAUSE_READER_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        baseline = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        digest = hashlib.sha256(
            (REVISION + ":" + baseline["snapshot_id"]).encode("ascii")
        )
        chapter_pages: list[tuple[str, bytes]] = []
        scanned_verses = historical = changed_verses = 0
        by_reason: Counter[str] = Counter()
        owner_subject_moves = 0
        for source_file in sorted(folder.iterdir(), key=lambda p: p.name):
            if source_file.is_symlink() or not source_file.is_file():
                raise DanMek034Error("OWNER_CROSS_CLAUSE_SOURCE_ENTRY_UNSAFE")
            m = CHES_FILE_NAME.fullmatch(source_file.name)
            if m is None:
                raise DanMek034Error("OWNER_CROSS_CLAUSE_SOURCE_NAME_INVALID")
            prefix, chapter_number = m.groups()
            data, sha = _load_private_source(
                folder, prefix=prefix, chapter=int(chapter_number),
            )
            digest.update((source_file.name + ":" + sha + "\n").encode("ascii"))
            if len(chapter_pages) >= MAX_CHAPTERS:
                raise DanMek034Error("OWNER_CROSS_CLAUSE_TOO_MANY_CHAPTERS")
            rows = []
            for verse in data["verses"]:
                scanned_verses += 1
                original = [
                    span["original_ches_line_text"]
                    for span in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                guarded_english, old_status = _read_source_text(
                    original, reference=verse["reference"],
                    chapter_sha256=sha,
                )
                historical += int(old_status == "AMBIGUOUS")
                new_english, changes = apply_owner_cross_clause_subjects(
                    guarded_english,
                )
                changed_verses += int(bool(changes))
                owner_subject_moves += sum(
                    change["owner_authorized_subject_moves"]
                    for change in changes
                )
                for change in changes:
                    by_reason[change["rule_code"]] += 1
                rows.append((verse["reference"], new_english))
            chapter_pages.append((
                source_file.name[:-5] + ".html",
                _html_page(prefix + "." + chapter_number, rows),
            ))
        if scanned_verses != baseline["observed_verse_count"]:
            raise DanMek034Error("OWNER_CROSS_CLAUSE_VERSE_COUNT_CHANGED")
        if historical != baseline[
            "olt_owner_candidate_ambiguous_verses_unchanged"
        ]:
            raise DanMek034Error("OWNER_CROSS_CLAUSE_HISTORICAL_COUNT_CHANGED")
        if require_311 and historical != 311:
            raise DanMek034Error("OWNER_CROSS_CLAUSE_EXPECTED_311_CHANGED")
        if baseline != build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek034Error("OWNER_CROSS_CLAUSE_SOURCE_CHANGED_DURING_SCAN")
        snapshot = "snapshot-" + digest.hexdigest()[:24]
        if render:
            root = folder.parent / "ches-cross-clause-reading"
            _safe_dir(root)
            target = root / snapshot
            _safe_dir(target)
            for filename, content in chapter_pages:
                _write_once(target, filename, content)
            links = "".join(
                '<li><a href="' + html.escape(filename, quote=True) +
                '">' + html.escape(filename[:-5], quote=True) + '</a></li>'
                for filename, _ in chapter_pages
            )
            index = (
                '<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta http-equiv="Content-Security-Policy" content="'
                "default-src 'none'; base-uri 'none'; form-action 'none'\">"
                '<title>Private English v4</title></head><body>'
                '<h1>Owner-identified nonadjacent English subjects</h1>'
                '<p>Previous readers and CHES unchanged. Publication BLOCKED.</p>'
                '<ul>' + links + '</ul></body></html>\n'
            ).encode("utf-8")
            _write_once(target, "index.html", index)
        return {
            "checkpoint": REVISION,
            "mode": (
                "SEPARATELY_VERSIONED_PRIVATE_ENGLISH_V4" if render
                else "PRIVATE_CROSS_CLAUSE_AUDIT_ONLY_NO_FILES"
            ),
            "source_owner_reader_snapshot": baseline["snapshot_id"],
            "new_private_v4_snapshot_id": snapshot,
            "source_chapters_scanned": len(chapter_pages),
            "source_verses_scanned": scanned_verses,
            "historical_ambiguous_english_verses": historical,
            "verses_with_new_owner_cross_clause_changes": changed_verses,
            "owner_approved_exact_context_instances": sum(by_reason.values()),
            "owner_authorized_individual_subject_moves": owner_subject_moves,
            "owner_cross_clause_rule_counts": dict(sorted(by_reason.items())),
            "private_html_files_written_or_verified":
                len(chapter_pages) + 1 if render else 0,
            "automatic_unbounded_subject_inference_performed": False,
            "original_ches_modified": False,
            "prior_locked_readers_modified": False,
            "review_queue_or_approved_manifest_modified": False,
            "hebrew_cross_validation_performed": False,
            "private_english_in_cli_output": False,
            "publication_status": "BLOCKED",
        }
    except DanMek034Error:
        raise
    except DanMek027Error as exc:
        raise DanMek034Error(str(exc)) from None
    except Exception:
        raise DanMek034Error("PRIVATE_CROSS_CLAUSE_READER_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-034 private owner-identified cross-clause English"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument(
        "--confirm-machine-readable-use-permission", action="store_true",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--render-private-v4", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private CHES use permission must be confirmed")
    try:
        result = build_private_owner_cross_clause_reader(
            args.private_root, render=args.render_private_v4,
            require_311=args.require_311,
        )
    except DanMek034Error:
        parser.exit(2, "DANMEK_034_PRIVATE_CROSS_CLAUSE_FAILED\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
