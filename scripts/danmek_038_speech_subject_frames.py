"""DANMEK-038: source-anchored English speech-subject compound/formula grammar.

Uses CHES's ordered PRIVATE English fragments, not biblical person-name
exceptions. Full noun phrases stay intact and "thus he-says <subject>" is a
bounded speech formula, never a universal name-after-verb grammar rule.
CHES, old readers and approval manifests remain untouched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from scripts.danmek_027_multiclause_subject_first import MAX_VERSE_CHARS
from scripts.danmek_036_fragment_role_grammar import (
    _FINITE, _NAME, _LEXICAL, _VERB_STEM, _VERB_ING_TAIL,
)
from scripts.danmek_037_unmarked_clause_roles import (
    SPEECH_VERBS, build_private_unmarked_clause_reader,
)

REVISION = "DANMEK-038-SOURCE-SPEECH-SUBJECT-FORMULA-COMPOUND-v1"
MAX_FRAGMENTS = 10000
MAX_CASES = 100
COMPOUND_RECIPIENT = "SPEECH_COMPOUND_SUBJECT_WITH_RECIPIENT"
THUS_SIMPLE = "THUS_SAYS_SIMPLE_SUBJECT"
THUS_COMPOUND = "THUS_SAYS_COMPOUND_SUBJECT"
_TITLES = frozenset({
    "the·king", "the·queen", "the·priest", "the·prophet",
    "the·seer", "the·judge", "the·chief",
})
_RELATIONS = frozenset({
    "son-of", "daughter-of", "king-of", "priest-of", "prophet-of", "servant-of",
})
_OF_COMPLEMENTS = frozenset({"hosts", "Israel", "Judah"})
_SUSPICIOUS = (
    "the·", "son-of", "daughter-of", "king-of", "priest-of",
    "prophet-of", "servant-of",
)
_AUX = re.compile(r"-(?:is|are|was|were)-")


class DanMek038Error(ValueError):
    """Stable error codes without licensed English or local paths."""


def _recipient(token: str) -> bool:
    return token == "to" or (
        token.startswith("to·") and not token.startswith("to·to-")
    )


def _nominal_end(tokens: list[str], head: int) -> int | None:
    """End-exclusive full nominal phrase; None for incomplete compound."""
    if head + 1 >= len(tokens):
        return head + 1
    nxt = tokens[head + 1]
    if nxt in _TITLES:
        return head + 2
    if nxt in _RELATIONS:
        return (head + 3 if head + 2 < len(tokens)
                and _NAME.fullmatch(tokens[head + 2]) else None)
    # CHES lexical-class fragment, not a hardcoded individual name.
    if nxt == "Elohim":
        return head + 2 if not tokens[head].endswith("-of") else None
    if nxt == "Elohim-of":
        return (head + 3 if head + 2 < len(tokens)
                and _NAME.fullmatch(tokens[head + 2]) else None)
    if tokens[head].endswith("-of"):
        return head + 2 if nxt in _OF_COMPLEMENTS else None
    if nxt.startswith(_SUSPICIOUS) or _NAME.fullmatch(nxt):
        return None
    return head + 1


def discover_speech_subject_frames(fragments: list[str]) -> list[dict]:
    """Bounded source-span grammar: speech+compound+recipient OR thus-says."""
    if (type(fragments) is not list or len(fragments) > MAX_FRAGMENTS
            or any(type(x) is not str for x in fragments)
            or len(" ".join(fragments)) > MAX_VERSE_CHARS):
        raise DanMek038Error("INVALID_PRIVATE_SPEECH_SOURCE_FRAGMENTS")
    if len(fragments) < 2:
        return []
    found = []
    for verb_at, pred in enumerate(fragments):
        if not _FINITE.fullmatch(pred):
            continue
        positions = []
        if pred.endswith("-"):
            if (verb_at + 2 < len(fragments)
                    and _LEXICAL.fullmatch(fragments[verb_at + 1])):
                positions.append(verb_at + 2)
            if (verb_at + 3 < len(fragments)
                    and _VERB_STEM.fullmatch(fragments[verb_at + 1])
                    and _VERB_ING_TAIL.fullmatch(fragments[verb_at + 2])):
                positions.append(verb_at + 3)
        else:
            positions.append(verb_at + 1)
        for head in positions:
            if head >= len(fragments) or not _NAME.fullmatch(fragments[head]):
                continue
            ending = fragments[head - 1].rsplit("-", 1)[-1]
            if ending not in SPEECH_VERBS:
                break
            if _AUX.search(pred) and not ending.endswith("ing"):
                break
            phrase_end = _nominal_end(fragments, head)
            if phrase_end is None:
                break
            following = (
                fragments[phrase_end]
                if phrase_end < len(fragments) else None
            )
            compound_recipient = (
                phrase_end > head + 1 and following is not None
                and _recipient(following)
            )
            formula = (
                verb_at > 0 and fragments[verb_at - 1] == "thus"
                and pred in ("he-says", "he-said")
            )
            if compound_recipient:
                reason = COMPOUND_RECIPIENT
                begin = verb_at
            elif formula:
                reason = (
                    THUS_COMPOUND if phrase_end > head + 1 else THUS_SIMPLE
                )
                begin = verb_at - 1
            else:
                break
            if (compound_recipient and following == "to"
                    and phrase_end + 1 >= len(fragments)):
                break
            if (following is not None and following.startswith("and·")
                    and not _FINITE.fullmatch(following)):
                break
            if found and begin <= found[-1]["nominal_end"]:
                raise DanMek038Error("OVERLAPPING_SPEECH_SOURCE_FRAMES")
            found.append({
                "anchor_start": begin,
                "predicate_start": verb_at,
                "nominal_start": head,
                "nominal_end": phrase_end,
                "reason": reason,
            })
            break
        if len(found) > MAX_CASES:
            raise DanMek038Error("PRIVATE_SPEECH_FRAME_LIMIT")
    return found


def apply_speech_subject_frames(
    source: list[str], displayed: str,
) -> tuple[str, list[dict], dict]:
    """Relocate full phrase only with exact unique prior-display alignment.

    The following recipient or next-clause cue anchors the match but is NOT
    consumed. No edit is attempted if v7 or another stage already changed
    the exact source substring.
    """
    if type(displayed) is not str or len(displayed) > MAX_VERSE_CHARS:
        raise DanMek038Error("INVALID_PRIVATE_SPEECH_DISPLAY")
    frames = discover_speech_subject_frames(source)
    edits = []
    skipped = conflicts = 0
    for f in frames:
        begin, verb, head, end = (
            f["anchor_start"], f["predicate_start"],
            f["nominal_start"], f["nominal_end"],
        )
        bound = min(end + 1, len(source))
        anchor = " ".join(source[begin:bound])
        if displayed.count(anchor) != 1:
            skipped += 1
            continue
        left = displayed.find(anchor)
        original = " ".join(source[begin:end])
        right = left + len(original)
        if any(not (right <= a or left >= b) for a, b, _, _ in edits):
            conflicts += 1
            continue
        predicate = " ".join(source[verb:head])
        nominal = " ".join(source[head:end])
        leading = "thus " if begin < verb else ""
        if predicate.startswith(("and·", "And·")):
            conj, remainder = predicate.split("·", 1)
            replacement = leading + conj + " " + nominal + " -·" + remainder
        else:
            replacement = leading + nominal + " - " + predicate
        edits.append((left, right, replacement, f["reason"]))
    output = displayed
    for left, right, replacement, _ in sorted(edits, reverse=True):
        output = output[:left] + replacement + output[right:]
    evidence = [
        {"reason_code": reason, "full_source_nominal_phrase_moved": True,
         "complete_verse_grammar_certified": False}
        for _, _, _, reason in sorted(edits)
    ]
    return output, evidence, {
        "raw_source_speech_frames": len(frames),
        "new_v8_speech_subject_moves": len(edits),
        "already_changed_or_ambiguous_source_alignment": skipped,
        "edit_overlap_conflicts": conflicts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-038 private source-fragment speech grammar"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission",
                        action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--render-private-v8", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private machine-readable CHES usage must be confirmed")
    try:
        result = build_private_unmarked_clause_reader(
            args.private_root, render=args.render_private_v8,
            require_311=args.require_311, include_speech_frames_v8=True,
        )
    except ValueError:
        parser.exit(2, "DANMEK_038_PRIVATE_SPEECH_GRAMMAR_FAILED\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
