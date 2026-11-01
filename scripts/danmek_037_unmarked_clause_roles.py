"""DANMEK-037: privately parse English subject roles without object marker.

Based on direct inspection of the owner's 929 CHES JSON chapters, rather than
hardcoding biblical personal names. Two bounded, source-fragment-aware
English structures are added on top of the immutable v6 derived reading:

(1) a speech/report predicate + one proper-name-shaped speaker + an explicit
    TO-recipient phrase (excluding TO-TO infinitival expressions);
(2) a typically intransitive predicate + one proper-name-shaped subject +
    an explicit prepositional or independent next-clause boundary.

A capitalized word or a following TO on its own is NOT grammatical proof.
No direct object-bearing, quoted-name or complex/compound noun is moved
without another validated structural frame. CHES English lexical decisions
are accepted, not rechecked against Hebrew.
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
from scripts.danmek_036_fragment_role_grammar import (
    DanMek036Error, apply_source_nominal_roles,
    _FINITE, _NAME, _LEXICAL, _VERB_STEM, _VERB_ING_TAIL,
)

REVISION = "DANMEK-037-PRIVATE-ENGLISH-UNMARKED-CLAUSE-ROLES-v1"
MAX_CHAPTERS = 1100
MAX_FRAGMENTS = 10000
MAX_CANDIDATES = 100
SPEAKER_TO_RECIPIENT = "SPEECH_VERB_NOMINAL_TO_RECIPIENT"
INTRANSITIVE_SUBJECT = "INTRANSITIVE_VERB_NOMINAL_CLAUSE_BOUNDARY"
SPEECH_VERBS = frozenset({
    "said", "says", "say", "saying", "spoke", "speaks", "speaking",
})
INTRANSITIVE_VERBS = frozenset({
    "came", "come", "comes", "coming", "went", "go", "goes", "going",
    "arose", "rose", "rises", "rising", "rested", "rests", "resting",
    "lived", "lives", "living", "died", "dies", "dying",
    "slept", "sleeps", "sleeping", "sat", "sits", "sitting",
    "stood", "stands", "standing", "reigned", "reigns", "reigning",
    "dwelt", "dwells", "dwelling", "remained", "remains", "remaining",
})
INTRANSITIVE_BOUNDARIES = (
    "in·", "to·", "from·", "with·", "at·", "on·", "over·", "upon·",
)


class DanMek037Error(ValueError):
    """Public error identifier; never quote private English source."""


def identify_unmarked_english_roles(fragments: list[str]) -> list[dict]:
    if (type(fragments) is not list or len(fragments) > MAX_FRAGMENTS
            or any(type(t) is not str for t in fragments)
            or len(" ".join(fragments)) > MAX_VERSE_CHARS):
        raise DanMek037Error("INVALID_PRIVATE_UNMARKED_SOURCE_FRAGMENTS")
    if len(fragments) < 2:
        return []
    candidates = []
    for i, predicate in enumerate(fragments):
        if _FINITE.fullmatch(predicate) is None:
            continue
        positions = []
        if predicate.endswith("-"):
            if (i+2 < len(fragments)
                    and _LEXICAL.fullmatch(fragments[i+1])):
                positions.append(i+2)
            if (i+3 < len(fragments)
                    and _VERB_STEM.fullmatch(fragments[i+1])
                    and _VERB_ING_TAIL.fullmatch(fragments[i+2])):
                positions.append(i+3)
        else:
            positions.append(i+1)
        for nominal in positions:
            if (nominal >= len(fragments)
                    or _NAME.fullmatch(fragments[nominal]) is None):
                continue
            following = (
                fragments[nominal+1] if nominal+1 < len(fragments) else None
            )
            if following == "»":
                continue  # Handled separately by DANMEK-036.
            verb_ending = fragments[nominal - 1].rsplit("-", 1)[-1]
            # A progressive English auxiliary must not be followed by a
            # contradictory finite form (e.g., synthetic he-is-says).
            if (re.search(r"-(?:is|are|was|were)-", predicate)
                    and not verb_ending.endswith("ing")):
                continue
            reason = None
            if verb_ending in SPEECH_VERBS and (
                following == "to"
                or (
                    following is not None and following.startswith("to·")
                    and not following.startswith("to·to-")
                )
            ):
                reason = SPEAKER_TO_RECIPIENT
            elif verb_ending in INTRANSITIVE_VERBS and (
                following is None
                or following.startswith(INTRANSITIVE_BOUNDARIES)
                or _FINITE.fullmatch(following) is not None
            ):
                reason = INTRANSITIVE_SUBJECT
            if reason is None:
                continue
            if candidates and i <= candidates[-1]["last"]:
                raise DanMek037Error("OVERLAPPING_UNMARKED_CLAUSE_CANDIDATES")
            candidates.append({
                "first": i,
                "nominal": nominal,
                "last": nominal,
                "reason": reason,
            })
            break
        if len(candidates) > MAX_CANDIDATES:
            raise DanMek037Error("EXCESSIVE_UNMARKED_ENGLISH_CANDIDATES")
    return candidates


def apply_unmarked_english_roles(
    fragments: list[str], current_display: str,
) -> tuple[str, list[dict], dict]:
    if (type(current_display) is not str
            or len(current_display) > MAX_VERSE_CHARS):
        raise DanMek037Error("INVALID_UNMARKED_DERIVED_ENGLISH")
    candidates = identify_unmarked_english_roles(fragments)
    edits = []
    skipped = conflicts = 0
    for case in candidates:
        first, nominal, last = case["first"], case["nominal"], case["last"]
        original = " ".join(fragments[first:last+1])
        boundary = (
            " " + fragments[nominal+1]
            if nominal+1 < len(fragments) else ""
        )
        # Check the next source token as a clause cue, but do NOT consume
        # it in the edit. That token may itself begin the next finite
        # clause, whose subject can be independently moved.
        anchored = original + boundary
        if current_display.count(anchored) != 1:
            skipped += 1
            continue
        left = current_display.find(anchored)
        right = left + len(original)
        if any(not (right <= a or left >= b) for a,b,_,_ in edits):
            conflicts += 1
            continue
        predicate = " ".join(fragments[first:nominal])
        name = fragments[nominal]
        if predicate.startswith(("and·", "And·")):
            conjunction, after_dot = predicate.split("·", 1)
            replacement = conjunction + " " + name + " -·" + after_dot
        else:
            replacement = name + " - " + predicate
        edits.append((left, right, replacement, case["reason"]))
    derived = current_display
    for left, right, replacement, _ in sorted(edits, reverse=True):
        derived = derived[:left] + replacement + derived[right:]
    evidence = [
        {"rule_code": rule,
         "source_anchored_english_clause": True,
         "whole_verse_grammar_certified": False,
         "original_display_offset": left}
        for left, _, _, rule in sorted(edits)
    ]
    return derived, evidence, {
        "new_unmarked_grammar_candidates": len(candidates),
        "new_unmarked_grammar_moves": len(edits),
        "unmarked_candidates_not_exact_or_previously_changed": skipped,
        "unmarked_clause_overlap_conflicts": conflicts,
    }


def _html(name: str, rows: list[tuple[str,str]]) -> bytes:
    body = "".join(
        "<section><b>" + html.escape(ref, quote=True) + "</b> <span>" +
        html.escape(text, quote=True) + "</span></section>"
        for ref,text in rows
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        '<title>Private DANMEK v7 English</title>'
        '<style>body{font:17px/1.55 Georgia,serif;max-width:960px;'
        'margin:2rem auto;padding:1rem;background:#faf9f7;color:#222}'
        'section{padding:.5rem 0;border-bottom:1px solid #ddd}'
        'b{font:13px system-ui}span{white-space:pre-wrap;overflow-wrap:anywhere}'
        '</style></head><body><h1>Private v7 English — ' +
        html.escape(name, quote=True) + '</h1>'
        '<p>Finite, nominal, recipient, object-marker and clause-boundary '
        'roles from source English fragments only. Not complete grammar '
        'certification. Publication BLOCKED.</p>' + body +
        '</body></html>\n'
    ).encode("utf-8")


def build_private_unmarked_clause_reader(
    private_root: Path, *, render: bool = False, require_311: bool = False,
) -> dict:
    if type(render) is not bool or type(require_311) is not bool:
        raise DanMek037Error("INVALID_PRIVATE_UNMARKED_READER_OPTIONS")
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
        counts: Counter[str] = Counter()
        by_new_rule: Counter[str] = Counter()
        verses_scanned = historical = verses_changed = 0
        for file in sorted(root.iterdir(), key=lambda x: x.name):
            if file.is_symlink() or not file.is_file():
                raise DanMek037Error("PRIVATE_SOURCE_FILE_UNSAFE")
            match = CHES_FILE_NAME.fullmatch(file.name)
            if not match:
                raise DanMek037Error("PRIVATE_SOURCE_NAME_INVALID")
            prefix, number = match.groups()
            chapter, sha = _load_private_source(
                root, prefix=prefix, chapter=int(number),
            )
            digest.update((file.name + ":" + sha + "\n").encode("ascii"))
            verses = []
            for verse in chapter["verses"]:
                verses_scanned += 1
                source = [
                    x["original_ches_line_text"]
                    for x in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                text, status = _read_source_text(
                    source, reference=verse["reference"], chapter_sha256=sha,
                )
                historical += int(status == "AMBIGUOUS")
                text, v4 = apply_owner_cross_clause_subjects(text)
                text, v5, _ = reorder_structurally_supported_subjects(text)
                text, v6, _ = apply_source_nominal_roles(source, text)
                text, v7, result = apply_unmarked_english_roles(source, text)
                counts["older_v4_contexts_retained"] += len(v4)
                counts["older_v5_structures_retained"] += len(v5)
                counts["older_v6_structures_retained"] += len(v6)
                for key, value in result.items():
                    counts[key] += value
                for edit in v7:
                    by_new_rule[edit["rule_code"]] += 1
                verses_changed += int(bool(v4 or v5 or v6 or v7))
                verses.append((verse["reference"], text))
            if len(pages) >= MAX_CHAPTERS:
                raise DanMek037Error("PRIVATE_SOURCE_CHAPTER_LIMIT")
            pages.append((file.name[:-5] + ".html",
                          _html(prefix+"."+number, verses)))
        if verses_scanned != baseline["observed_verse_count"]:
            raise DanMek037Error("SOURCE_VERSE_COUNT_DRIFT")
        if historical != baseline[
            "olt_owner_candidate_ambiguous_verses_unchanged"
        ]:
            raise DanMek037Error("HISTORICAL_ENGLISH_CASE_COUNT_DRIFT")
        if require_311 and historical != 311:
            raise DanMek037Error("REQUIRE_HISTORICAL_311")
        if baseline != build_private_reader(
            root, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek037Error("SOURCE_CHANGED_DURING_AUDIT")
        if counts["new_unmarked_grammar_candidates"] != (
            counts["new_unmarked_grammar_moves"]
            + counts["unmarked_candidates_not_exact_or_previously_changed"]
            + counts["unmarked_clause_overlap_conflicts"]
        ):
            raise DanMek037Error("UNMARKED_CANDIDATE_ACCOUNTING")
        snapshot = "snapshot-" + digest.hexdigest()[:24]
        if render:
            parent = root.parent / "ches-english-clause-roles"
            _safe_dir(parent)
            folder = parent / snapshot
            _safe_dir(folder)
            for name, data in pages:
                _write_once(folder, name, data)
            links = "".join(
                '<li><a href="' + html.escape(name, quote=True) + '">' +
                html.escape(name[:-5], quote=True) + '</a></li>'
                for name,_ in pages
            )
            index = (
                '<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta http-equiv="Content-Security-Policy" content="'
                "default-src 'none'; base-uri 'none'; form-action 'none'\">"
                '<title>Private English v7</title></head><body>'
                '<h1>English clause roles v7</h1>'
                '<p>CHES and previous snapshots unchanged, publication BLOCKED.'
                '</p><ul>' + links + '</ul></body></html>\n'
            ).encode("utf-8")
            _write_once(folder, "index.html", index)
        return {
            "checkpoint": REVISION,
            "mode": (
                "SEPARATE_PRIVATE_ENGLISH_CLAUSE_READING_V7" if render
                else "PRIVATE_CLAUSE_AUDIT_METADATA_ONLY"
            ),
            "source_owner_reader_snapshot": baseline["snapshot_id"],
            "private_v7_snapshot": snapshot,
            "chapters_scanned": len(pages),
            "verses_scanned": verses_scanned,
            "historical_ambiguous_english_verses": historical,
            "new_unmarked_grammar_candidates":
                counts["new_unmarked_grammar_candidates"],
            "new_unmarked_grammar_moves": counts["new_unmarked_grammar_moves"],
            "new_unmarked_moves_by_structure": dict(sorted(by_new_rule.items())),
            "unmarked_candidates_not_exact_or_previously_changed":
                counts["unmarked_candidates_not_exact_or_previously_changed"],
            "unmarked_clause_overlap_conflicts":
                counts["unmarked_clause_overlap_conflicts"],
            "retained_v4_contexts": counts["older_v4_contexts_retained"],
            "retained_v5_structures": counts["older_v5_structures_retained"],
            "retained_v6_structures": counts["older_v6_structures_retained"],
            "verses_with_any_v4_to_v7_reorder": verses_changed,
            "private_html_files_written_or_verified":
                len(pages)+1 if render else 0,
            "all_english_syntax_certified": False,
            "other_unmarked_nominal_roles_still_unresolved": True,
            "source_ches_modified": False,
            "prior_readers_modified": False,
            "approval_manifest_modified": False,
            "hebrew_cross_validation_performed": False,
            "private_english_on_stdout": False,
            "publication_status": "BLOCKED",
        }
    except DanMek037Error:
        raise
    except (DanMek027Error, DanMek034Error, DanMek035Error, DanMek036Error) as exc:
        raise DanMek037Error(str(exc)) from None
    except Exception:
        raise DanMek037Error("PRIVATE_UNMARKED_ENGLISH_GRAMMAR_FAILED") from None


def main() -> int:
    p = argparse.ArgumentParser(
        description="DANMEK-037 private source-aware English clause roles"
    )
    p.add_argument("--private-root", type=Path, required=True)
    p.add_argument("--confirm-machine-readable-use-permission",
                   action="store_true")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--render-private-v7", action="store_true")
    p.add_argument("--require-311", action="store_true")
    a = p.parse_args()
    if not a.confirm_machine_readable_use_permission:
        p.error("Private machine-readable CHES permission must be confirmed")
    try:
        report = build_private_unmarked_clause_reader(
            a.private_root, render=a.render_private_v7,
            require_311=a.require_311,
        )
    except DanMek037Error:
        p.exit(2, "DANMEK_037_PRIVATE_CLAUSE_GRAMMAR_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
