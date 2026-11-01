"""DANMEK-036: CHES English fragment-aware finite/subject/object parser.

English-only, local/private. No CHES text is embedded in public Git.
Original CHES, older HTML snapshots and private approved manifests stay
unchanged. A capitalized name alone is NEVER an established subject.
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
from scripts.danmek_030_reviewed_english_subject_order import _read_source_text
from scripts.danmek_034_owner_cross_clause_subjects import (
    DanMek034Error, apply_owner_cross_clause_subjects,
)
from scripts.danmek_035_structural_english_order import (
    DanMek035Error, reorder_structurally_supported_subjects,
)

REVISION = "DANMEK-036-SOURCE-FRAGMENT-ROLE-GRAMMAR-v1"
MAX_CHAPTERS = 1100
MAX_FRAGMENTS = 10000
MAX_CANDIDATES = 100
COMPACT = "FINITE_NOMINAL_MARKED_OBJECT_COMPACT"
SPLIT_ONE = "FINITE_NOMINAL_MARKED_OBJECT_ONE_VERB_CONTINUATION"
SPLIT_TWO = "FINITE_NOMINAL_MARKED_OBJECT_TWO_VERB_CONTINUATIONS"
_FINITE = re.compile(
    r"(?:(?:and|And)·)?(?:he|she|they|we|you|ye|thou)-"
    r"(?:[a-z]+-)*[a-z]+-?\Z"
)
# Explicitly exclude capitalized verb tokens like I-saw. This is NOT
# a lexicon of scriptural names. The role cue is the full ordered frame:
# finite predicate + bounded noun + standalone » + object.
_NAME = re.compile(
    r"(?!And\Z|Then\Z|When\Z|That\Z|The\Z|But\Z|For\Z|If\Z|"
    r"He\Z|She\Z|They\Z|His\Z|Her\Z|It\Z)"
    r"(?!I-|You-|We-|They-|He-|She-|Thou-|Ye-)"
    r"[A-Z][A-Za-z'’-]{1,49}(?:-[A-Za-z'’-]+)*\Z"
)
_LEXICAL = re.compile(r"[a-z]+(?:-[a-z]+)*\Z")
_VERB_STEM = re.compile(r"[a-z]{2,8}\Z")
_VERB_ING_TAIL = re.compile(r"ing(?:-[a-z]+)*\Z")


class DanMek036Error(ValueError):
    """Stable error code: do not expose private English or source paths."""


def detect_source_nominal_roles(fragments: list[str]) -> list[dict]:
    """Parse the ORIGINAL ordered source spans, never just the flat verse.

    A candidate is structurally strong only when the name comes directly
    after a complete finite verb or its 1–2 lexical continuations and the
    next source fragment is a *standalone* English object marker ».
    Other nominal structures, intervening clauses, speech and ambiguous
    objects are deliberately left for review.
    """
    if (type(fragments) is not list or len(fragments) > MAX_FRAGMENTS
            or any(type(part) is not str for part in fragments)
            or len(" ".join(fragments)) > MAX_VERSE_CHARS):
        raise DanMek036Error("INVALID_PRIVATE_CHES_FRAGMENT_SEQUENCE")
    if len(fragments) < 3:
        return []
    matches = []
    for start, finite in enumerate(fragments):
        if _FINITE.fullmatch(finite) is None:
            continue
        choices = []
        if finite.endswith("-"):
            if (start + 2 < len(fragments)
                    and _LEXICAL.fullmatch(fragments[start + 1])):
                choices.append((start + 2, SPLIT_ONE))
            if (start + 3 < len(fragments)
                    and _VERB_STEM.fullmatch(fragments[start + 1])
                    and _VERB_ING_TAIL.fullmatch(fragments[start + 2])):
                choices.append((start + 3, SPLIT_TWO))
        else:
            choices.append((start + 1, COMPACT))
        for nominal, rule in choices:
            if (nominal + 1 < len(fragments)
                    and _NAME.fullmatch(fragments[nominal])
                    and fragments[nominal + 1] == "»"):
                if matches and start <= matches[-1]["marker"]:
                    raise DanMek036Error("SOURCE_ROLE_SPANS_OVERLAP")
                matches.append({
                    "verb": start,
                    "nominal": nominal,
                    "marker": nominal + 1,
                    "class": rule,
                })
                break
        if len(matches) > MAX_CANDIDATES:
            raise DanMek036Error("TOO_MANY_NOMINAL_CANDIDATES")
    return matches


def apply_source_nominal_roles(
    source: list[str], display: str,
) -> tuple[str, list[dict], dict]:
    """Safely apply exact source-backed sequences to a new derived display.

    When a previous v2/v4/v5 reader has already changed a source sequence,
    or the sequence repeats within the verse, do not guess alignment.
    Preserve it unchanged and count the skipped source candidate.
    """
    if type(display) is not str or len(display) > MAX_VERSE_CHARS:
        raise DanMek036Error("INVALID_DERIVED_PRIVATE_DISPLAY")
    candidates = detect_source_nominal_roles(source)
    edits = []
    skipped = conflicts = 0
    for case in candidates:
        v, n, m = case["verb"], case["nominal"], case["marker"]
        expected = " ".join(source[v:m + 1])
        if display.count(expected) != 1:
            skipped += 1
            continue
        left = display.find(expected)
        right = left + len(expected)
        if any(not (right <= e[0] or left >= e[1]) for e in edits):
            conflicts += 1
            continue
        verb = " ".join(source[v:n])
        noun = source[n]
        if verb.startswith(("and·", "And·")):
            conjunction, remainder = verb.split("·", 1)
            # Preserve the user's specific space-dot format for generating.
            if remainder.startswith(("he-is- generating", "she-is- generating")):
                replacement = conjunction + " " + noun + " ·" + remainder + " »"
            else:
                replacement = conjunction + " " + noun + " -·" + remainder + " »"
        else:
            replacement = noun + " - " + verb + " »"
        if replacement == expected:
            skipped += 1
            continue
        edits.append((left, right, replacement, case["class"]))
    derived = display
    for left, right, replacement, _ in sorted(edits, reverse=True):
        derived = derived[:left] + replacement + derived[right:]
    evidence = [
        {
            "reason_code": rule, "original_display_start": left,
            "original_display_end": right,
            "finite_nominal_and_standalone_object_mark_confirmed": True,
            "independent_complete_grammar_certification": False,
        }
        for left, right, _, rule in sorted(edits)
    ]
    return derived, evidence, {
        "source_structural_candidates": len(candidates),
        "new_v6_fragment_moves": len(edits),
        "source_matches_already_changed_or_not_unique": skipped,
        "source_alignment_conflicts": conflicts,
    }


def _html_page(name: str, verses: list[tuple[str, str]]) -> bytes:
    rows = "".join(
        "<section><b>" + html.escape(ref, quote=True) + "</b> <span>" +
        html.escape(english, quote=True) + "</span></section>"
        for ref, english in verses
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        '<title>Private English fragment-role reading</title>'
        '<style>body{font:17px/1.55 Georgia,serif;max-width:960px;'
        'margin:2rem auto;padding:1rem;background:#faf9f7;color:#232323}'
        'section{padding:.5rem 0;border-bottom:1px solid #ccc}'
        'b{font:13px system-ui}span{white-space:pre-wrap;overflow-wrap:anywhere}'
        '</style></head><body><h1>Private English v6: ' +
        html.escape(name, quote=True) + '</h1>'
        '<p>Only source-anchored finite/nominal/marked-object relations. '
        'Other English syntax remains unresolved; publication BLOCKED. '
        'Original CHES and earlier readers unchanged.</p>' +
        rows + "</body></html>\n"
    ).encode("utf-8")


def build_private_fragment_role_reader(
    private_root: Path, *, render: bool = False, require_311: bool = False,
) -> dict:
    """Whole local corpus, source-anchored English grammar audit or v6 HTML."""
    if type(render) is not bool or type(require_311) is not bool:
        raise DanMek036Error("INVALID_PRIVATE_FRAGMENT_ROLE_OPTIONS")
    try:
        root = _private_archive_root(private_root)
        baseline = build_private_reader(
            root, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        digest = hashlib.sha256(
            (REVISION + ":" + baseline["snapshot_id"]).encode("ascii")
        )
        pages = []
        counts = Counter()
        by_rule = Counter()
        checked_verses = historical = touched = 0
        for filename in sorted(root.iterdir(), key=lambda p: p.name):
            if filename.is_symlink() or not filename.is_file():
                raise DanMek036Error("PRIVATE_SOURCE_FILE_UNSAFE")
            m = CHES_FILE_NAME.fullmatch(filename.name)
            if m is None:
                raise DanMek036Error("PRIVATE_SOURCE_FILENAME_INVALID")
            prefix, chap = m.groups()
            chapter, sha = _load_private_source(
                root, prefix=prefix, chapter=int(chap),
            )
            digest.update((filename.name + ":" + sha + "\n").encode("ascii"))
            verses = []
            for verse in chapter["verses"]:
                checked_verses += 1
                fragments = [
                    s["original_ches_line_text"]
                    for s in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                english, old_status = _read_source_text(
                    fragments, reference=verse["reference"],
                    chapter_sha256=sha,
                )
                historical += int(old_status == "AMBIGUOUS")
                english, owner_v4 = apply_owner_cross_clause_subjects(english)
                english, owner_v5, _ = reorder_structurally_supported_subjects(
                    english,
                )
                english, new_changes, stats = apply_source_nominal_roles(
                    fragments, english,
                )
                touched += int(bool(owner_v4 or owner_v5 or new_changes))
                counts["old_v4_contexts"] += len(owner_v4)
                counts["old_v5_marked_generating_moves"] += len(owner_v5)
                for key, value in stats.items():
                    counts[key] += value
                for edit in new_changes:
                    by_rule[edit["reason_code"]] += 1
                verses.append((verse["reference"], english))
            if len(pages) >= 1100:
                raise DanMek036Error("PRIVATE_SOURCE_CHAPTER_LIMIT")
            pages.append((filename.name[:-5] + ".html",
                          _html_page(prefix + "." + chap, verses)))
        if checked_verses != baseline["observed_verse_count"]:
            raise DanMek036Error("VERSE_COUNT_CHANGED")
        if historical != baseline[
            "olt_owner_candidate_ambiguous_verses_unchanged"
        ]:
            raise DanMek036Error("HISTORICAL_AMBIGUITY_CHANGED")
        if require_311 and historical != 311:
            raise DanMek036Error("HISTORICAL_311_REQUIRED")
        if baseline != build_private_reader(
            root, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek036Error("SOURCE_CHANGED_DURING_PROCESSING")
        if counts["source_structural_candidates"] != (
            counts["new_v6_fragment_moves"]
            + counts["source_matches_already_changed_or_not_unique"]
            + counts["source_alignment_conflicts"]
        ):
            raise DanMek036Error("FRAGMENT_CANDIDATE_ACCOUNTING_FAILED")
        snapshot = "snapshot-" + digest.hexdigest()[:24]
        if render:
            parent = root.parent / "ches-english-fragment-roles"
            _safe_dir(parent)
            dest = parent / snapshot
            _safe_dir(dest)
            for name, content in pages:
                _write_once(dest, name, content)
            index = (
                '<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta http-equiv="Content-Security-Policy" content="'
                "default-src 'none'; base-uri 'none'; form-action 'none'\">"
                '<title>Private English v6</title></head><body>'
                '<h1>DANMEK-036 fragment-aware English reader</h1>'
                '<p>Original CHES and previous snapshots unchanged; '
                'publication BLOCKED.</p><ul>' +
                "".join(
                    '<li><a href="' + html.escape(name, quote=True) + '">' +
                    html.escape(name[:-5], quote=True) + '</a></li>'
                    for name, _ in pages
                ) + '</ul></body></html>\n'
            ).encode("utf-8")
            _write_once(dest, "index.html", index)
        return {
            "checkpoint": REVISION,
            "mode": (
                "SEPARATE_PRIVATE_FRAGMENT_GRAMMAR_V6" if render
                else "PRIVATE_FRAGMENT_GRAMMAR_AUDIT_NO_FILE_WRITES"
            ),
            "source_owner_reader_snapshot": baseline["snapshot_id"],
            "new_private_v6_snapshot": snapshot,
            "chapters_scanned": len(pages),
            "verses_scanned": checked_verses,
            "historical_english_ambiguous_verses": historical,
            "source_structural_candidates": counts["source_structural_candidates"],
            "new_v6_fragment_moves": counts["new_v6_fragment_moves"],
            "old_v4_contexts_retained": counts["old_v4_contexts"],
            "old_v5_marked_generating_moves_retained":
                counts["old_v5_marked_generating_moves"],
            "source_matches_already_changed_or_not_unique":
                counts["source_matches_already_changed_or_not_unique"],
            "source_alignment_conflicts": counts["source_alignment_conflicts"],
            "new_moves_by_structure": dict(sorted(by_rule.items())),
            "verses_changed_in_separate_v6": touched,
            "private_html_files_written_or_verified":
                len(pages) + 1 if render else 0,
            "english_grammar_fully_certified": False,
            "unknown_subject_object_cases_still_require_review": True,
            "source_ches_modified": False,
            "previous_readers_modified": False,
            "approval_manifest_modified": False,
            "hebrew_cross_validation_performed": False,
            "private_verse_content_on_stdout": False,
            "publication_status": "BLOCKED",
        }
    except DanMek036Error:
        raise
    except (DanMek027Error, DanMek034Error, DanMek035Error) as exc:
        raise DanMek036Error(str(exc)) from None
    except Exception:
        raise DanMek036Error("PRIVATE_FRAGMENT_GRAMMAR_FAILED") from None


def main() -> int:
    p = argparse.ArgumentParser(
        description="DANMEK-036 private English fragment and clause roles"
    )
    p.add_argument("--private-root", type=Path, required=True)
    p.add_argument("--confirm-machine-readable-use-permission",
                   action="store_true")
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--audit-only", action="store_true")
    modes.add_argument("--render-private-v6", action="store_true")
    p.add_argument("--require-311", action="store_true")
    a = p.parse_args()
    if not a.confirm_machine_readable_use_permission:
        p.error("Local private CHES use permission must be confirmed")
    try:
        result = build_private_fragment_role_reader(
            a.private_root, render=a.render_private_v6,
            require_311=a.require_311,
        )
    except DanMek036Error:
        p.exit(2, "DANMEK_036_FRAGMENT_GRAMMAR_FAILED\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
