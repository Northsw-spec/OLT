"""DANMEK-035: corpus-wide structural English word-order stage (private v5).

The user reports that subject-first word-order problems are widespread.
Earlier DANMEK regexes and two named context exceptions are NOT a general
grammar engine. This module introduces named-role *structural evidence*
(independent of any particular person's name), a corpus-wide diagnostic of
split predicate forms, and one safe, user-authorized structure:

    conjunction + he-is- + generating + SUBJECT + » + OBJECT

The English "»" marker is only a local structural cue when combined with
this exact relationship predicate. It is NOT permission to treat *any*
capitalized noun after *any* transitive verb as a subject. Uncertain
structures are measured, not rewritten. All source English is private,
and only invented lexical examples belong in GitHub CI.
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
    apply_owner_cross_clause_subjects, DanMek034Error,
)

REVISION = "DANMEK-035-CORPUS-STRUCTURAL-ENGLISH-ORDER-v1"
MAX_CHAPTERS = 1100
RULE_MARKED_GENERATING = "MARKED_GENERATIVE_RELATION_SUBJECT_BEFORE_OBJECT"
SPLIT_VERB_WITH_NAME = "SPLIT_FINITE_GLOSS_POSTVERBAL_NAME_UNRESOLVED"
SPLIT_VERB_OTHER = "SPLIT_FINITE_GLOSS_OTHER"
# Surface-level proper-name pattern; capital letter alone is NEVER a
# subject proof. Exclude likely English function words and pronouns.
_NAME = (
    r"(?!(?:And|Then|When|Because|That|The|But|For|If|He|She|They|"
    r"His|Her|It|Gods)\b)[A-Z][A-Za-z'’-]{1,49}"
    r"(?:[ ](?!And\b|Then\b|The\b)[A-Z][A-Za-z'’-]{1,49}){0,2}"
)
_FINITE_SPLIT = (
    r"(?<![A-Za-z·-])(?P<and>[Aa]nd)·"
    r"(?P<pronoun>he|she|they|we|thou|ye|you)"
    r"-(?P<aux>is|are|was|were|shall|will|has|had)-"
    r"(?P<split>[ \t]+)(?P<part>[a-z]+(?:-[a-z]+){0,4})"
)
_ANY_SPLIT = re.compile(_FINITE_SPLIT)
_SPLIT_WITH_NAME = re.compile(
    _FINITE_SPLIT + r"(?P<gap>[ \t]+)(?P<subject>" + _NAME + r")"
    r"(?![A-Za-z'’-])"
)
_MARKED_GENERATION = re.compile(
    _FINITE_SPLIT + r"(?P<gap>[ \t]+)(?P<subject>" + _NAME + r")"
    r"(?P<marker>[ \t]+»[ \t]+)(?P<object>" + _NAME + r")"
    r"(?![A-Za-z'’-])"
)


class DanMek035Error(ValueError):
    """Only stable error identifiers; never the private English itself."""


def analyze_structural_english_order(english: str) -> dict:
    """Collect *shapes* without treating detected names as proven subjects."""
    if type(english) is not str or len(english) > MAX_VERSE_CHARS:
        raise DanMek035Error("INVALID_PRIVATE_STRUCTURAL_ENGLISH")
    starts = list(_ANY_SPLIT.finditer(english))
    names = list(_SPLIT_WITH_NAME.finditer(english))
    marked = list(_MARKED_GENERATION.finditer(english))
    marked_starts = {m.start() for m in marked}
    if len(marked_starts) != len(marked):
        raise DanMek035Error("DUPLICATE_MARKED_STRUCTURAL_CANDIDATE")
    safe = [m for m in marked if (
        m["pronoun"] in ("he", "she") and
        m["aux"] == "is" and
        m["part"] == "generating"
    )]
    # Any other relationship predicate, and any unmarked name even after
    # generating, still needs English clause-role review.
    return {
        "split_finite_gloss_count": len(starts),
        "split_finite_gloss_with_name_count": len(names),
        "split_finite_gloss_with_marker_count": len(marked),
        "bounded_owner_supported_generating_matches": len(safe),
        "split_finite_gloss_with_name_left_unresolved":
            len(names) - len(safe),
        "split_finite_gloss_without_adjacent_name":
            len(starts) - len(names),
    }


def reorder_structurally_supported_subjects(
    english: str,
) -> tuple[str, list[dict], dict]:
    """Generalize one owner-approved *syntax*, never a particular name.

    Only a finite split "he-is- generating" or "she-is- generating"
    with two *different grammatical positions* separated by » qualifies.
    A possible object-only reading outside this exact slot structure stays
    unchanged. A matched sequence is rendered with the same number of name
    mentions and the author's required dot/hyphen typography.
    """
    stats = analyze_structural_english_order(english)
    edits: list[tuple[int, int, str]] = []
    for m in _MARKED_GENERATION.finditer(english):
        if not (
            m["pronoun"] in ("he", "she") and
            m["aux"] == "is" and
            m["part"] == "generating"
        ):
            continue
        # Keep the source predicate's internal whitespace exactly. The
        # original conjunction-middle-dot is re-positioned to the finite
        # predicate, as specifically requested by the owner.
        replacement = (
            m["and"] + " " + m["subject"] + " ·" +
            m["pronoun"] + "-" + m["aux"] + "-" + m["split"] +
            m["part"] + m["marker"] + m["object"]
        )
        if replacement == m.group(0):
            continue
        left, right = m.span()
        if any(not (right <= l or left >= r) for l, r, _ in edits):
            raise DanMek035Error("OVERLAPPING_STRUCTURAL_SUBJECT_MATCHES")
        edits.append((left, right, replacement))
    result = english
    for left, right, replacement in reversed(edits):
        result = result[:left] + replacement + result[right:]
    evidence = [
        {
            "rule_code": RULE_MARKED_GENERATING,
            "position_start": left,
            "position_end": right,
            "subject_identification": "OWNER_APPROVED_BOUNDED_ENGLISH_STRUCTURE",
            "explicit_english_object_marker_required": True,
            "global_subject_grammar_certified": False,
            "original_private_ches_modified": False,
        }
        for left, right, _ in edits
    ]
    if len(edits) != stats["bounded_owner_supported_generating_matches"]:
        raise DanMek035Error("STRUCTURAL_SUBJECT_MATCH_COUNT_MISMATCH")
    return result, evidence, stats


def _page(chapter: str, rows: list[tuple[str, str]]) -> bytes:
    verse_html = "".join(
        '<section><b>' + html.escape(ref, quote=True) + '</b> <span>' +
        html.escape(display, quote=True) + '</span></section>'
        for ref, display in rows
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        '<title>Private structural English reader</title>'
        '<style>body{font:17px/1.55 Georgia,serif;max-width:980px;'
        'margin:2rem auto;padding:1rem;background:#faf9f7;color:#222}'
        'section{padding:.6rem 0;border-bottom:1px solid #ccc}'
        'b{font:13px system-ui}span{white-space:pre-wrap;overflow-wrap:anywhere}'
        '</style></head><body>'
        '<h1>Private structural English v5: ' +
        html.escape(chapter, quote=True) + '</h1>'
        '<p>Bounded English structural rules only. Other potentially '
        'post-verbal subjects are not certified. CHES and all earlier '
        'private readers are unchanged. Publication BLOCKED.</p>' +
        verse_html + '</body></html>\n'
    ).encode("utf-8")


def build_private_structural_english_reader(
    private_root: Path, *, render: bool = False,
    require_311: bool = False,
) -> dict:
    """Whole available English corpus; private immutable v5 or pure audit."""
    if type(render) is not bool or type(require_311) is not bool:
        raise DanMek035Error("INVALID_STRUCTURAL_READER_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        baseline = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        digest = hashlib.sha256(
            (REVISION + ":" + baseline["snapshot_id"]).encode("ascii")
        )
        chapters: list[tuple[str, bytes]] = []
        counts: Counter[str] = Counter()
        cross_clause: Counter[str] = Counter()
        total_verses = historical = edited_verses = 0
        for file in sorted(folder.iterdir(), key=lambda p: p.name):
            if file.is_symlink() or not file.is_file():
                raise DanMek035Error("STRUCTURAL_SOURCE_ENTRY_UNSAFE")
            match = CHES_FILE_NAME.fullmatch(file.name)
            if match is None:
                raise DanMek035Error("STRUCTURAL_SOURCE_ENTRY_NAME_INVALID")
            prefix, chapter = match.groups()
            data, sha = _load_private_source(
                folder, prefix=prefix, chapter=int(chapter),
            )
            digest.update((file.name + ":" + sha + "\n").encode("ascii"))
            rows = []
            for verse in data["verses"]:
                total_verses += 1
                parts = [
                    span["original_ches_line_text"]
                    for span in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                english, status = _read_source_text(
                    parts, reference=verse["reference"],
                    chapter_sha256=sha,
                )
                historical += int(status == "AMBIGUOUS")
                prior, owner_evidence = apply_owner_cross_clause_subjects(english)
                for change in owner_evidence:
                    cross_clause[change["rule_code"]] += 1
                after, evidence, stats = reorder_structurally_supported_subjects(prior)
                for key, value in stats.items():
                    counts[key] += value
                counts["new_bounded_structural_moves"] += len(evidence)
                edited_verses += int(bool(owner_evidence or evidence))
                rows.append((verse["reference"], after))
            chapters.append((file.name[:-5] + ".html",
                             _page(prefix + "." + chapter, rows)))
            if len(chapters) > MAX_CHAPTERS:
                raise DanMek035Error("STRUCTURAL_READER_CHAPTER_LIMIT")
        if total_verses != baseline["observed_verse_count"]:
            raise DanMek035Error("STRUCTURAL_SOURCE_VERSE_COUNT_MISMATCH")
        if historical != baseline[
            "olt_owner_candidate_ambiguous_verses_unchanged"
        ]:
            raise DanMek035Error("STRUCTURAL_SOURCE_HISTORICAL_COUNT_MISMATCH")
        if require_311 and historical != 311:
            raise DanMek035Error("STRUCTURAL_REQUIRED_311_MISMATCH")
        if baseline != build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek035Error("STRUCTURAL_SOURCE_CHANGED_DURING_SCAN")
        snapshot = "snapshot-" + digest.hexdigest()[:24]
        if render:
            root = folder.parent / "ches-structural-english-reading"
            _safe_dir(root)
            target = root / snapshot
            _safe_dir(target)
            for name, page in chapters:
                _write_once(target, name, page)
            links = "".join(
                '<li><a href="' + html.escape(name, quote=True) + '">' +
                html.escape(name[:-5], quote=True) + '</a></li>'
                for name, _ in chapters
            )
            index = (
                '<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta http-equiv="Content-Security-Policy" content="'
                "default-src 'none'; base-uri 'none'; form-action 'none'\">"
                '<title>Private English v5</title></head><body>'
                '<h1>Corpus-wide structural English word-order stage</h1>'
                '<p>Not a complete grammatical certification. CHES and '
                'all earlier private reader versions remain untouched. '
                'Publication BLOCKED.</p><ul>' + links + '</ul></body></html>\n'
            ).encode("utf-8")
            _write_once(target, "index.html", index)
        return {
            "checkpoint": REVISION,
            "mode": (
                "SEPARATELY_VERSIONED_PRIVATE_STRUCTURAL_ENGLISH_V5"
                if render else "CORPUS_WIDE_STRUCTURAL_AUDIT_NO_FILES"
            ),
            "source_owner_reader_snapshot": baseline["snapshot_id"],
            "new_private_structural_snapshot_id": snapshot,
            "source_chapters_scanned": len(chapters),
            "source_verses_scanned": total_verses,
            "historical_ambiguous_english_verses": historical,
            "new_private_html_pages": len(chapters) + 1 if render else 0,
            "owner_explicit_prior_context_instances":
                sum(cross_clause.values()),
            "owner_explicit_prior_context_rule_counts":
                dict(sorted(cross_clause.items())),
            "structural_split_verb_diagnostics":
                dict(sorted(counts.items())),
            "verses_with_v4_or_v5_changes": edited_verses,
            "grammar_error_count_established": False,
            "remaining_english_grammar_review_required": True,
            "generic_postverb_name_movement_performed": False,
            "source_ches_modified": False,
            "old_readers_modified": False,
            "owner_approval_manifest_modified": False,
            "private_english_on_stdout": False,
            "hebrew_cross_validation_performed": False,
            "publication_status": "BLOCKED",
        }
    except DanMek035Error:
        raise
    except (DanMek027Error, DanMek034Error) as exc:
        raise DanMek035Error(str(exc)) from None
    except Exception:
        raise DanMek035Error("PRIVATE_STRUCTURAL_READER_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-035 full private English split-verb structure audit"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission",
                        action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--render-private-v5", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private machine-readable CHES use permission required")
    try:
        report = build_private_structural_english_reader(
            args.private_root, render=args.render_private_v5,
            require_311=args.require_311,
        )
    except DanMek035Error:
        parser.exit(2, "DANMEK_035_PRIVATE_ENGLISH_STRUCTURE_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
