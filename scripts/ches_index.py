"""Enumerate OT chapter PDF links, never download CHES or commit third-party text.

The HTML index is only a discoverable chapter inventory. It cannot prove
the PDF content, CHES text alignment, availability or license scope.
"""
from __future__ import annotations
from html.parser import HTMLParser
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

INDEX = "https://www.scripture4all.org/OnlineInterlinear/Hebrew_Index.htm"
PDF_RE = re.compile(r"^/OnlineInterlinear/OTpdf/([A-Za-z0-9_-]+)\.pdf$")
CHAPTER_RE = re.compile(r"^([A-Za-z0-9_-]*[A-Za-z_-])([1-9][0-9]*)$")


class ChapterIndex(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.hrefs.append(value.strip())


def parse_index(source: bytes) -> dict:
    if not isinstance(source, bytes) or not source:
        raise ValueError("Original index HTML is empty")
    raw = source.decode("utf-8", "replace")
    parser = ChapterIndex()
    parser.feed(raw)
    results: list[dict] = []
    seen: set[str] = set()
    duplicate_pdf_link_occurrences = 0
    for href in parser.hrefs:
        if ".pdf" not in href.lower():
            continue
        if ".." in href or "%" in href:
            raise ValueError("Original PDF index path may not contain traversal/encoding")
        candidate = urljoin(INDEX, href)
        url = urlsplit(candidate)
        if (url.scheme != "https" or url.netloc != "www.scripture4all.org" or
            url.query or url.fragment or url.username or url.password):
            raise ValueError("Index contains noncanonical or external PDF link")
        m = PDF_RE.fullmatch(url.path)
        if not m:
            raise ValueError("Index PDF path outside expected Scripture4All OT folder")
        filename = m.group(1)
        n = CHAPTER_RE.fullmatch(filename)
        if not n:
            raise ValueError("Unrecognized source OT chapter filename convention")
        group, number = n.group(1), int(n.group(2))
        if candidate in seen:
            # Public index can repeat a navigation link. Preserve the
            # occurrence count but do not download/copy it twice.
            duplicate_pdf_link_occurrences += 1
            continue
        seen.add(candidate)
        results.append({"source_book_filename_prefix_NOT_OLT_BOOK_ID": group,
                        "source_chapter_filename_number": number,
                        "original_pdf_url": candidate})
    if not results:
        raise ValueError("Original Scripture4All index lists no OT PDF chapters")
    groups: dict[str, list[int]] = {}
    for row in results:
        groups.setdefault(row["source_book_filename_prefix_NOT_OLT_BOOK_ID"],[]).append(
            row["source_chapter_filename_number"])
    for book, chapters in groups.items():
        if chapters != list(range(1, len(chapters)+1)):
            raise ValueError(f"Original chapter-number gaps/duplicates for source filename prefix {book!r}")
    return {
        "source_index_url": INDEX,
        "source_index_html_sha256": hashlib.sha256(source).hexdigest(),
        "discovered_chapter_pdf_count": len(results),
        "duplicate_index_pdf_link_occurrences_deduplicated": duplicate_pdf_link_occurrences,
        "discovered_original_source_filename_prefix_count": len(groups),
        "chapter_links": results,
        "book_prefixes_are_not_approved_oshb_book_mappings": True,
        "downloaded_chapter_pdf_count": 0,
        "ches_text_extracted_from_this_index": False,
        "rights_for_public_CHES_data_export_confirmed": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Inspect an already downloaded Scripture4All OT HTML index")
    p.add_argument("--index", required=True, type=Path)
    p.add_argument("--require-ot-chapters", type=int, default=929)
    p.add_argument("--require-books", type=int, default=39)
    args = p.parse_args()
    report = parse_index(args.index.read_bytes())
    if report["discovered_chapter_pdf_count"] != args.require_ot_chapters:
        raise ValueError("OT chapter index unexpected total; check original source")
    if report["discovered_original_source_filename_prefix_count"] != args.require_books:
        raise ValueError("OT book prefix index unexpected total; check original source")
    print(json.dumps({k: v for k, v in report.items() if k != "chapter_links"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
