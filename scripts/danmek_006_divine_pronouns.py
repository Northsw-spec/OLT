"""DANMEK-006: Divine-referent capitalization for a derived OLT English view.

This formatter is deliberately not wired into the source-faithful CHES reader.
A separate, original-language-checked English layer supplies explicit, per-
occurrence referent evidence. Nothing here infers God's identity from nearby
words, capitalizes every he/him, reorders Hebrew, or mutates source JSON.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

PRONOUNS = frozenset(("he", "him", "his", "himself"))
DIVINE_REFERENTS = frozenset(("GOD", "LORD"))
VERSE_REFERENCE = re.compile(r"[a-z0-9_-]{2,20}\.[1-9][0-9]{0,2}\.[1-9][0-9]{0,2}\Z")
EVIDENCE_ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
REVISION = "DANMEK-006-DIVINE-PRONOUN-EXPLICIT-REFERENT-v1"


class DanMekPronounError(ValueError):
    """Fixed safe failure reason. Do not echo source text on error."""


@dataclass(frozen=True)
class VerifiedDivinePronoun:
    """An explicitly certified referent, supplied by a separate source review.

    start: zero-based character offset in the *derived* English verse.
    surface: lowercase original pronoun at that exact location.
    referent: the confirmed antecedent, GOD or LORD (not just a neighbor).
    verse_reference: must match the English verse being transformed.
    evidence_id: private/canonical source-annotation identifier; mere presence
                 is NOT independent proof of morphological or philological QA.
    """

    start: int
    surface: str
    referent: str
    verse_reference: str
    evidence_id: str


def capitalize_verified_divine_pronouns(
    english_verse: str, *, verse_reference: str,
    mentions: Sequence[VerifiedDivinePronoun],
) -> str:
    """Capitalize He/Him/His/Himself only for verified divine referents.

    For example, a verified 'he' in '·he-is-making' becomes '·He-is-making';
    unrelated human 'he' and all punctuation remain unchanged. Call this on
    a derived OLT English verse, NEVER on original CHES JSON or its source
    reader. The calling layer must validate referent evidence first.
    """
    if (type(english_verse) is not str or
        type(verse_reference) is not str or
        not VERSE_REFERENCE.fullmatch(verse_reference) or
        type(mentions) not in (tuple, list)):
        raise DanMekPronounError("INVALID_VERSE_OR_ANNOTATIONS")
    if len(mentions) > 1000:
        raise DanMekPronounError("TOO_MANY_REFERENT_ANNOTATIONS")

    spans: list[tuple[int, int, str]] = []
    for mention in mentions:
        if (type(mention) is not VerifiedDivinePronoun or
            type(mention.start) is not int or
            type(mention.surface) is not str or
            mention.surface not in PRONOUNS or
            mention.referent not in DIVINE_REFERENTS or
            mention.verse_reference != verse_reference or
            type(mention.evidence_id) is not str or
            not EVIDENCE_ID.fullmatch(mention.evidence_id)):
            raise DanMekPronounError("INVALID_DIVINE_REFERENT_EVIDENCE")
        start = mention.start
        end = start + len(mention.surface)
        if (start < 0 or end > len(english_verse) or
            english_verse[start:end] != mention.surface or
            (start > 0 and english_verse[start - 1].isalpha()) or
            (end < len(english_verse) and english_verse[end].isalpha())):
            raise DanMekPronounError("PRONOUN_OFFSET_OR_TOKEN_MISMATCH")
        spans.append((start, end, mention.surface))
    spans.sort(key=lambda m: m[0])
    if any(spans[i][0] < spans[i-1][1] for i in range(1, len(spans))):
        raise DanMekPronounError("OVERLAPPING_DIVINE_REFERENT_ANNOTATIONS")

    updated = english_verse
    for start, _end, surface in reversed(spans):
        updated = updated[:start] + surface.capitalize() + updated[start + len(surface):]
    return updated
