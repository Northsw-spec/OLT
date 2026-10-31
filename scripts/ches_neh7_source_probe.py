"""CHES NEH7: report marker-only geometry from an ephemeral original PDF.

This diagnostics module emits no Bible text, licensed green source words,
original Hebrew, KJV passages or private data. Verse labels are numeric.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from scripts.ches_import import explicit_verse_markers, page_spans

NUMERIC_ONLY = re.compile(r"[0-9:() ]+\Z")


def marker_geometry_only(source_path: Path) -> dict:
    import fitz
    with fitz.open(stream=source_path.read_bytes(), filetype="pdf") as pdf:
        spans = [span for index, page in enumerate(pdf, 1)
                 for span in page_spans(page, index)]
    primary = explicit_verse_markers(spans, 7, source_book="neh")
    result = []
    for mark in primary:
        if mark["verse"] not in range(69, 74):
            continue
        candidates = [
            {
                "numeric_glyph_only": row["text"].strip(),
                "ink_rgb": f"{row['color']:06x}",
                "x": row["x"],
                "relative_y": round(row["y"] - mark["y"], 2),
            }
            for row in spans
            if (
                row["page"] == mark["page"]
                and abs(row["y"] - mark["y"]) < 20
                and 0 <= row["x"] < 300
                and NUMERIC_ONLY.fullmatch(row["text"].strip())
            )
        ]
        result.append({
            "printed_primary_verse": mark["verse"],
            "marker_page": mark["page"],
            "alternate_combined_in_gray_y_group": mark["alternate_verse"],
            "nearby_numeric_glyphs_only": candidates[:30],
        })
    return {
        "pages_with_source_data": len({row["page"] for row in spans}),
        "primary_marker_count_recognized": len(primary),
        "tail_primary_marker_geometry": result,
        "source_english_text_or_original_hebrew_in_output": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    opts = parser.parse_args()
    print(json.dumps(marker_geometry_only(opts.pdf), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
