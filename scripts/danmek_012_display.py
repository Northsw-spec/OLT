"""DANMEK-012: hide a whole, isolated lowercase 'c' in the private OLT view.

Never change original CHES JSON; never strip c inside English words, uppercase
C, punctuation-marked notes or other glyphs. Return only display fragments.
"""
from __future__ import annotations

from typing import Sequence

REVISION = "DANMEK-012-HIDE-WHOLE-LOWERCASE-C-FRAGMENT-v1"


class DanMek012Error(ValueError):
    """Fixed diagnostics only; no private source is printed."""


def hide_isolated_c(
    fragments: Sequence[str | None],
) -> tuple[list[str | None], int]:
    """Suppress only fragments containing exactly lowercase c + whitespace."""
    if type(fragments) not in (list, tuple) or len(fragments) > 250_000:
        raise DanMek012Error("INVALID_ISOLATED_C_FRAGMENT_SEQUENCE")
    if any(value is not None and type(value) is not str for value in fragments):
        raise DanMek012Error("INVALID_ISOLATED_C_FRAGMENT_TYPE")
    output: list[str | None] = []
    suppressed = 0
    for fragment in fragments:
        if fragment is not None and fragment.strip() == "c":
            output.append(None)
            suppressed += 1
        else:
            output.append(fragment)
    return output, suppressed
