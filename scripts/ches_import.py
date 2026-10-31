"""Private-only import of CHES v2.0 text from Scripture4All chapter PDFs.

The user reports permission for machine-readable use, NOT general public
redistribution or further licensed derivative translations. This tool does
not download automatically, publish extracts, align to OSHB lexemes, or
approve OLT English renderings. It deliberately ignores the black KJV text.
Requires PyMuPDF. Data files MUST remain private and untracked.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import os
from typing import Any

PDF_MIN = 1000
PDF_MAX = 30_000_000
MARKER = re.compile(r"^\s*(\d{1,3})\s*:\s*(\d{1,3})\s*$")
BOOK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,19}$")


def is_ches_green(rgb: int) -> bool:
    """CHES text color is green; do not mistake the AV column for CHES."""
    if type(rgb) is not int or not 0 <= rgb <= 0xFFFFFF:
        return False
    r, g, b = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
    return g >= 65 and g >= r + 35 and g >= b + 25 and r <= 150 and b <= 160


def page_spans(page: Any, pageno: int) -> list[dict[str, Any]]:
    result = []
    for block in page.get_text("dict", flags=0).get("blocks", []):
        for line in block.get("lines", []):
            for s in line.get("spans", []):
                t = s.get("text", "").strip()
                if not t:
                    continue
                box, color = s.get("bbox"), s.get("color")
                if not isinstance(box, (tuple, list)) or len(box) != 4:
                    raise ValueError("PDF span has no geometry")
                if type(color) is not int or any(type(v) not in (int, float) for v in box):
                    raise ValueError("Invalid PDF source text color or position")
                result.append({"text": t, "page": pageno,
                               "x": round(float(box[0]), 2),
                               "y": round(float(box[1]), 2),
                               "color": color})
    return result


def explicit_verse_markers(spans: list[dict[str, Any]], chapter: int) -> list[dict[str, Any]]:
    """Reassemble exact gray printed 1:1 labels from PDF's separate glyph spans.

    The actual Genesis PDF stores chapter and verse digits as multiple gray
    text spans (0x888888), which share one original PDF y coordinate.
    Never infer missing verse labels from CHES lines or KJV prose.
    """
    groups: dict[tuple[int, float], list[dict[str, Any]]] = {}
    for row in spans:
        if row["color"] != 0x888888:
            continue
        key = (row["page"], round(row["y"], 1))
        groups.setdefault(key, []).append(row)
    marks = []
    for (page, y), pieces in groups.items():
        pieces.sort(key=lambda x: x["x"])
        raw = "".join(s["text"].strip() for s in pieces)
        matched = MARKER.fullmatch(raw)
        if matched and int(matched.group(1)) == chapter:
            marks.append({"page": page, "y": y, "x": pieces[0]["x"],
                          "verse": int(matched.group(2))})
    marks.sort(key=lambda x: (x["page"], x["y"], x["x"]))
    return marks


def assign_ches_to_explicit_verses(spans: list[dict[str, Any]],
                                  chapter: int,
                                  expected_verses: int | None = None) -> list[dict[str, Any]]:
    """Reject missing/duplicate verse anchors; NEVER silently guess a join."""
    marks = explicit_verse_markers(spans, chapter)
    numbers = [x["verse"] for x in marks]
    if not marks or numbers != list(range(1, len(marks)+1)):
        raise ValueError("Original PDF verse markers are absent, duplicate or out of sequence")
    if expected_verses is not None and numbers != list(range(1, expected_verses+1)):
        raise ValueError("Original PDF verse inventory disagrees with required verse count")
    verses = [{"verse": m["verse"], "marker_page": m["page"],
               "marker_y": m["y"], "ches_spans": []} for m in marks]
    green = [row for row in spans if is_ches_green(row["color"])]
    green.sort(key=lambda x: (x["page"], round(x["y"], 1), x["x"]))
    for row in green:
        anchor_index = None
        for i, m in enumerate(marks):
            if (m["page"], m["y"]) <= (row["page"], row["y"]):
                anchor_index = i
            else:
                break
        if anchor_index is not None:
            verses[anchor_index]["ches_spans"].append({
                "page": row["page"], "pdf_x": row["x"],
                "pdf_y": row["y"], "original_ches_line_text": row["text"]})
    if any(not x["ches_spans"] for x in verses):
        raise ValueError("No CHES green source spans for one or more explicitly marked verses")
    return verses


def import_private_pdf(original: bytes, book: str, chapter: int,
                       expected_verses: int | None = None) -> dict[str, Any]:
    if not BOOK.fullmatch(book) or type(chapter) is not int or chapter < 1:
        raise ValueError("Invalid source book/chapter identifier")
    if not isinstance(original, bytes) or not original.startswith(b"%PDF-") or not PDF_MIN <= len(original) <= PDF_MAX:
        raise ValueError("Invalid or oversized original chapter PDF")
    import fitz
    with fitz.open(stream=original, filetype="pdf") as pdf:
        if not 1 <= len(pdf) <= 100:
            raise ValueError("Unexpected source PDF page count")
        spans = [s for p, page in enumerate(pdf, 1) for s in page_spans(page, p)]
        verses = assign_ches_to_explicit_verses(spans, chapter, expected_verses)
        result = {
            "source": "Scripture4All Online Hebrew Interlinear CHES 2.0",
            "original_source_pdf_sha256": hashlib.sha256(original).hexdigest(),
            "source_pdf_byte_length": len(original),
            "source_pdf_page_count": len(pdf),
            "book": book, "chapter": chapter,
            "source_book_identifier_is_not_verified_oshb_book_mapping": True,
            "verses_extracted": len(verses),
            "ches_pdf_green_spans": sum(len(v["ches_spans"]) for v in verses),
            "copyright_basis": "USER_REPORTED_PERMISSION_FOR_MACHINE_READABLE_CHES_DATA",
            "copyright_scope_for_publication_or_derived_other_languages": "NOT_ESTABLISHED",
            "full_source_text_in_public_git_permitted": False,
            "alignment_with_oshb_words_verified": False,
            "independent_grammar_or_sense_approved": False,
            "olt_english_translation_approved": False,
            "publication_status": "BLOCKED",
            "verses": [{
                "reference": f"{book}.{chapter}.{v['verse']}",
                "explicit_original_pdf_verse_anchor_page": v["marker_page"],
                "explicit_original_pdf_verse_anchor_y": v["marker_y"],
                "source_ches_spans_NOT_OLT_TRANSLATION": v["ches_spans"],
                "english_draft_status": "CHES_SOURCE_ONLY_UNALIGNED",
                "publication_status": "BLOCKED"
            } for v in verses],
        }
    return result


def write_private_json(data: dict[str, Any], path: Path) -> None:
    target = path.expanduser().resolve()
    if ".olt-private" not in target.parts:
        raise ValueError("Output must be inside a .olt-private directory ignored by Git")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    data_bytes = (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode("utf-8")
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".ches-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data_bytes)
        os.chmod(tmp, 0o600)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    p = argparse.ArgumentParser(description="CHES source import to private JSON, never public repository")
    p.add_argument("--pdf", required=True, type=Path)
    p.add_argument("--book", required=True)
    p.add_argument("--chapter", required=True, type=int)
    p.add_argument("--expected-verses", type=int)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--output-private", type=Path)
    args = p.parse_args()
    extracted = import_private_pdf(args.pdf.read_bytes(), args.book, args.chapter,
                                   args.expected_verses)
    if args.output_private:
        write_private_json(extracted, args.output_private)
    print(json.dumps({key: value for key, value in extracted.items()
                      if key in {"book", "chapter", "original_source_pdf_sha256",
                                 "source_pdf_byte_length", "source_pdf_page_count",
                                 "verses_extracted", "ches_pdf_green_spans",
                                 "alignment_with_oshb_words_verified",
                                 "full_source_text_in_public_git_permitted",
                                 "publication_status"}}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
