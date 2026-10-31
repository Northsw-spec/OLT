"""DANMEK-014: suppress standalone lowercase c markers in private OLT HTML.

Only a separate lowercase 'c' or repeated 'cc'/'c c' whitespace-delimited
marker is suppressed, including when it shares a source PDF text fragment
with legitimate words. Never change original CHES JSON or immutable snapshots.
Do not change 'C', 'c.', 'c·', 'c-name', words containing c, or other glyphs.
"""
from __future__ import annotations

import re
from typing import Sequence

# Bump immutable reader snapshot ID, preserving the verified DANMEK-013 view.
REVISION = "DANMEK-014-HIDE-WHITESPACE-BOUND-LOWERCASE-C-v2"
_MARKER = re.compile(r"(?<!\S)c+(?!\S)")


class DanMek012Error(ValueError):
    """Sanitized diagnostic: never disclose a private source text."""


def hide_isolated_c(
    fragments: Sequence[str | None],
) -> tuple[list[str | None], int]:
    """Return display-only fragments and count suppressed lowercase c letters.

    Only whole whitespace-delimited tokens of one or more lowercase c letters
    are eligible. Adjacent whitespace is reduced *only* to remove the marker,
    preventing concatenation of the legitimate words on either side.
    """
    if type(fragments) not in (list, tuple) or len(fragments) > 250_000:
        raise DanMek012Error("INVALID_ISOLATED_C_FRAGMENT_SEQUENCE")
    if any(value is not None and type(value) is not str for value in fragments):
        raise DanMek012Error("INVALID_ISOLATED_C_FRAGMENT_TYPE")

    output: list[str | None] = []
    removed_letters = 0
    for fragment in fragments:
        if fragment is None:
            output.append(None)
            continue
        hits = list(_MARKER.finditer(fragment))
        if not hits:
            output.append(fragment)
            continue
        removed_letters += sum(len(match.group()) for match in hits)

        # Delete only the marker and at most one adjacent separator for
        # each occurrence; never blanket-normalize the rest of a fragment.
        delete_positions: set[int] = set()
        for hit in hits:
            delete_positions.update(range(hit.start(), hit.end()))
            if hit.end() < len(fragment) and fragment[hit.end()].isspace():
                delete_positions.add(hit.end())
            elif hit.start() > 0 and fragment[hit.start() - 1].isspace():
                delete_positions.add(hit.start() - 1)

        visible = "".join(
            character for index, character in enumerate(fragment)
            if index not in delete_positions
        )
        output.append(visible if visible.strip() else None)

    return output, removed_letters
