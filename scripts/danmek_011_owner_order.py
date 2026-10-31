"""DANMEK-011: owner-approved *English editorial* subject-first candidates.

The owner expressly approves all uniquely proposed DANMEK-010 patterns.
This is not an attestation that the proposed subject agrees with Hebrew syntax.
No third-party data are embedded in this implementation or printed to stdout.
"""
from __future__ import annotations

import re

from scripts.danmek_009_english_order import (
    DanMek009Error, apply_reviewed_order,
)

REVISION = "DANMEK-012-OWNER-APPROVED-GLUED-YAHWEH-v2"

# Conservative typography patterns; NOT a linguistic parser.
VERB = (r"(?:[Aa]nd[· ])?"
        r"(?:[Hh]e|[Ss]he|[Tt]hey|[Ww]e|[Tt]hou|[Yy]ou|[Yy]e)-"
        r"(?:(?:is|are|was|were|shall|will|have|had)-)?"
        r"[a-z]+(?:-[a-z]+){0,5}")
SUBJECT = r"[A-Z][A-Za-z'’-]{1,49}"
WHOLE_VERB = re.compile(VERB + r"\Z")
WHOLE_SUBJECT = re.compile(SUBJECT + r"\Z")
INLINE = re.compile(
    r"(?<![A-Za-z-])(?P<verb>" + VERB + r")[ \t]*"
    r"(?P<subject>" + SUBJECT + r")(?![A-Za-z-])"
)
# Bounded extra case, not a blanket 'And' + 'Yahweh' search: a name
# immediately after this verb and immediately before 'from·' is the
# user-supplied English editorial shape. 'Yahweh' elsewhere could be
# the OBJECT, and must not be relocated by an ungrounded rule.
JOINED_YAHWEH = re.compile(
    r"\A(?P<verb>[Aa]nd[· ]he-shall-cut-off)[ \t]*"
    r"(?P<subject>Yahweh)(?=from[· ])"
)


class DanMek011Error(ValueError):
    """Fixed diagnostic, never the user's private source text."""


def discover_candidates(
    reference: str, chapter_sha256: str, texts: list[str],
) -> tuple[list[dict], bool]:
    """At most one proposed English reorder per verse; ambiguous => none."""
    found = []
    for index, text in enumerate(texts):
        joined = JOINED_YAHWEH.match(text)
        if joined:
            found.append({
                "reference": reference, "chapter_json_sha256": chapter_sha256,
                "mode": "inline", "source_syntax_reviewed": False,
                "review_note": "NOT_REVIEWED",
                "verb_fragment_index": index + 1,
                "original_fragment": text,
                "original_verb": joined["verb"],
                "original_subject": joined["subject"],
            })
        if (index + 1 < len(texts) and WHOLE_VERB.fullmatch(text)
                and WHOLE_SUBJECT.fullmatch(texts[index + 1])):
            found.append({
                "reference": reference, "chapter_json_sha256": chapter_sha256,
                "mode": "adjacent", "source_syntax_reviewed": False,
                "review_note": "NOT_REVIEWED",
                "verb_fragment_index": index + 1,
                "subject_fragment_index": index + 2,
                "original_verb": text, "original_subject": texts[index + 1],
            })
        for match in INLINE.finditer(text):
            found.append({
                "reference": reference, "chapter_json_sha256": chapter_sha256,
                "mode": "inline", "source_syntax_reviewed": False,
                "review_note": "NOT_REVIEWED",
                "verb_fragment_index": index + 1,
                "original_fragment": text,
                "original_verb": match["verb"],
                "original_subject": match["subject"],
            })
    return (found if len(found) == 1 else []), len(found) > 1


def apply_owner_approved_candidates(
    *, reference: str, chapter_sha256: str,
    original: list[str], visible: list[str],
) -> tuple[list[str], str]:
    """Opt-in editorial move; never assert verified source syntax.

    Returns an exact reason: APPLIED, AMBIGUOUS, YLT_OVERLAP, NO_CANDIDATE.
    A YLT replacement of the affected source fragment does not authorize a
    further reorder; leave that verse's edited English in place instead.
    """
    if (type(original) is not list or type(visible) is not list
            or len(original) != len(visible)
            or any(type(x) is not str for x in original + visible)):
        raise DanMek011Error("INVALID_PRIVATE_OWNER_ORDER_FRAGMENT_SEQUENCE")
    proposals, ambiguous = discover_candidates(
        reference, chapter_sha256, original,
    )
    if ambiguous:
        return list(visible), "AMBIGUOUS"
    if not proposals:
        return list(visible), "NO_CANDIDATE"
    rule = proposals[0]
    i = rule["verb_fragment_index"] - 1
    affected = (i, i + 1) if rule["mode"] == "adjacent" else (i,)
    if any(visible[position] != original[position] for position in affected):
        return list(visible), "YLT_OVERLAP"
    try:
        rendered, count = apply_reviewed_order(
            reference=reference, chapter_sha256=chapter_sha256,
            original=original, visible=visible,
            rules={reference: rule},
        )
    except DanMek009Error as exc:
        raise DanMek011Error("OWNER_ORDER_CANDIDATE_INTERNAL_MISMATCH") from exc
    if count != 1:
        raise DanMek011Error("OWNER_ORDER_CANDIDATE_NOT_APPLIED")
    if rule["mode"] == "inline":
        joined = JOINED_YAHWEH.match(rule["original_fragment"])
        if joined and (rule["original_verb"] == joined["verb"]
                      and rule["original_subject"] == joined["subject"]):
            # Keep the rest of the unverified gloss tail unchanged.
            # English sentence-initial capitalization is not reverential.
            tail = rule["original_fragment"][joined.end():]
            expected = joined["verb"][:3] + " Yahweh — he-shall-cut-off" + tail
            if rendered[i] != expected:
                raise DanMek011Error("JOINED_YAHWEH_PRESENTATION_MISMATCH")
            rendered[i] = "And Yahweh — he shall cut off " + tail
    return rendered, "APPLIED"
