"""DANMEK-008: bounded, display-only English simplification.

The owner's requested private OLT presentation changes exact CHES-rendered
'sur faces' into 'faces'. The original CHES interlinear fragments/JSON are
correct source data and never modified. This English-only surface-string rule
does NOT prove the Hebrew lexical identity (e.g., פני) of any occurrence.

Both representations seen in PDF typography are handled: one text fragment
containing the exact phrase, or two consecutive fragment strings 'sur',
'faces' *within the same verse*. Other articles, morphology, words and
inter-verse boundaries are preserved.
"""
from __future__ import annotations

import re
from typing import Sequence

REVISION = "DANMEK-008-SUR-FACES-DISPLAY-ONLY-v1"
_PHRASE = re.compile(r"(?<![A-Za-z])sur[ \t]+faces(?![A-Za-z])", re.IGNORECASE)


class DanMek008DisplayError(ValueError):
    """Sanitized validation error: never disclose private source text."""


def simplify_sur_faces_for_olt_view(
    fragments: Sequence[str],
) -> tuple[list[str | None], int]:
    """Return display-only fragments and a count of exact phrase changes.

    None means suppress a fragment in derived HTML; it never means that
    original text, JSON, PDF metadata or a source span has been deleted.
    """
    if type(fragments) not in (list, tuple) or len(fragments) > 250_000:
        raise DanMek008DisplayError("INVALID_ENGLISH_DISPLAY_FRAGMENT_SEQUENCE")
    if any(type(text) is not str for text in fragments):
        raise DanMek008DisplayError("INVALID_ENGLISH_DISPLAY_FRAGMENT_TYPE")

    result: list[str | None] = []
    replacements = 0
    for fragment in fragments:
        def _replace(m: re.Match[str]) -> str:
            return "Faces" if m.group(0)[0].isupper() else "faces"
        transformed, count = _PHRASE.subn(_replace, fragment)
        result.append(transformed)
        replacements += count

    for i in range(len(result) - 1):
        a, b = result[i], result[i + 1]
        # Only two whole adjacent glyph fragments, in the same verse.
        # No movement across intervening tokens, punctuation or verse labels.
        if (a is not None and b is not None and
            a.strip().lower() == "sur" and b.strip().lower() == "faces"):
            result[i] = None
            result[i + 1] = "Faces" if a.strip()[0].isupper() else "faces"
            replacements += 1

    return result, replacements
