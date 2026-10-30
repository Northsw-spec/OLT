"""OLT-035B exact-byte Greek NT verse reader over all 27 RP2018 source books.

Bible book texts originate from the pinned upstream derived Unicode CCAT CSVs.
They contain chapter/verse/source text, NOT canonical original Greek word IDs,
not Greek morphology, not Greek lemma approval, not a published translation.
Auxiliary separate readings are retained without silently overwriting main text.
"""
from __future__ import annotations

import argparse
import csv
from io import StringIO
import json
from pathlib import Path
import re
from typing import Any

from .engine import SourceContractError
from .sources import ROOT, git_blob_sha1

REGISTRY = Path("data/engine/olt_035b_rp2018_verse_inventory.json")
_GREEK = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")


def read_nt_inventory(root: Path = ROOT) -> dict[str, Any]:
    d = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    if (d.get("checkpoint"), d.get("source_tag"), d.get("source_commit"),
        d.get("text_edition"), d.get("release_status")) != (
        "OLT-035B", "v3.3.2", "27a45ff1b7be6c17ccbfeac414f3f55732ae8e28",
        "ROBINSON_PIERPONT_BYZANTINE_TEXTFORM_2018", "BLOCKED"
    ):
        raise SourceContractError("Incorrect RP2018 source revision or release state")
    if (d.get("continuous_book_count"), d.get("separate_ancillary_file_count")) != (27, 2):
        raise SourceContractError("27 original NT books and two separate source appendices required")
    if (d.get("full_nt_word_token_ids_verified"), d.get("full_nt_lemma_morphology_verified"),
        d.get("full_nt_textual_apparatus_critically_collated"),
        d.get("locale_translation_generated")) != (False, False, False, False):
        raise SourceContractError("Greek source CSV cannot be claimed linguistically reviewed or translated")
    if d.get("upstream_license") != "PUBLIC_DOMAIN" or d.get("source_text_human_review") != "NOT_DONE":
        raise SourceContractError("Greek original source rights or review status changed")
    books, aux = d.get("continuous_books"), d.get("ancillary_readings")
    if not isinstance(books, list) or not isinstance(aux, list) or len(books) != 27 or len(aux) != 2:
        raise SourceContractError("Greek NT source-file inventory incomplete")
    if [x.get("canonical_nt_order") for x in books] != list(range(1, 28)):
        raise SourceContractError("Unexpected order of the 27 Greek NT books")
    for rows, folder in ((books, ""), (aux, "ancillary/")):
        seen: set[str] = set()
        for item in rows:
            code = item.get("upstream_book_code")
            if not isinstance(code, str) or not re.fullmatch(r"[0-9A-Z]{2,5}", code) or code in seen:
                raise SourceContractError("Duplicate or invalid Greek NT book/source file")
            seen.add(code)
            if (item.get("repo_path") != f"data/imported/nt/rp2018/{folder}{code}.csv" or
                item.get("upstream_path") != f"csv-unicode/ccat/no-variants/{code}.csv" or
                not isinstance(item.get("byte_length"), int) or item["byte_length"] < 20 or
                not _SHA1.fullmatch(item.get("upstream_git_blob_sha1", ""))):
                raise SourceContractError("Greek source path/byte count/Git hash is not pinned")
        if rows is aux and seen != {"PA", "ACT24"}:
            raise SourceContractError("Auxiliary Greek passage files must be kept distinct")
    if any(x["upstream_book_code"] in {"PA", "ACT24"} for x in books):
        raise SourceContractError("Greek text variants must not silently become normal books")
    return d


def _load_csv(item: dict[str, Any], root: Path) -> list[tuple[int, int, str]]:
    path = root / item["repo_path"]
    raw = path.read_bytes()
    if len(raw) != item["byte_length"] or git_blob_sha1(raw) != item["upstream_git_blob_sha1"]:
        raise SourceContractError("Pinned RP2018 Greek file bytes disagree with the official upstream Git blob")
    text = raw.decode("utf-8", errors="strict")
    rows = csv.reader(StringIO(text, newline=""), strict=True)
    try:
        header = next(rows)
    except StopIteration as exc:
        raise SourceContractError("Empty Greek original source CSV") from exc
    if header != ["chapter", "verse", "text"]:
        raise SourceContractError("RP2018 Greek text CSV columns changed")
    result = []
    previous = (0, 0)
    seen: set[tuple[int, int]] = set()
    for row in rows:
        if len(row) != 3 or not re.fullmatch(r"[1-9]\d*", row[0]) or not re.fullmatch(r"[1-9]\d*", row[1]):
            raise SourceContractError("Malformed original-language NT verse row")
        chapter, verse = int(row[0]), int(row[1])
        pair = (chapter, verse)
        if pair <= previous or pair in seen:
            raise SourceContractError("Duplicate, reordered or descending NT verse numbering")
        previous = pair
        seen.add(pair)
        greek = row[2]
        if not greek or not _GREEK.search(greek):
            raise SourceContractError("NT source verse contains no Greek script")
        result.append((chapter, verse, greek))
    if not result:
        raise SourceContractError("An NT source book is empty")
    return result


def read_nt_book(book_code: str, root: Path = ROOT,
                 registry: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = registry if registry is not None else read_nt_inventory(root)
    hits = [x for x in reg["continuous_books"] if x["upstream_book_code"] == book_code]
    if len(hits) != 1:
        raise SourceContractError("Unknown or ancillary book: only the 27 continuous Greek NT books are accepted")
    item = hits[0]
    rows = _load_csv(item, root)
    return {
        "book_code": book_code,
        "book_id": item["canonical_book_id"],
        "source_edition": "RP2018_BYZTXT_v3.3.2",
        "edition_commit": reg["source_commit"],
        "original_source_file": item["upstream_path"],
        "original_file_git_blob_sha1": item["upstream_git_blob_sha1"],
        "verse_count": len(rows),
        "source_language": "grc",
        "verses": [
            {
                "reference": f"{item['canonical_book_id']}.{chapter}.{verse}",
                "chapter": chapter, "verse": verse, "original_greek_text": greek,
                "source_language": "grc",
                "original_source_token_ids": None,
                "original_lemma_ids": None,
                "original_morphology": None,
                "owner_translation": None,
                "source_review": "NOT_DONE",
                "publication_status": "BLOCKED",
            }
            for chapter, verse, greek in rows
        ],
        "word_alignment_status": "NOT_AVAILABLE_IN_UPSTREAM_VERSE_CSV",
        "independent_source_review": "NOT_DONE",
        "publication_status": "BLOCKED",
    }


def read_nt_ancillary(code: str, root: Path = ROOT,
                      registry: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = registry if registry is not None else read_nt_inventory(root)
    hits = [x for x in reg["ancillary_readings"] if x["upstream_book_code"] == code]
    if len(hits) != 1:
        raise SourceContractError("Unknown Greek ancillary passage")
    spec = hits[0]
    rows = _load_csv(spec, root)
    return {
        "ancillary_id": code,
        "possible_context": spec["possible_context"],
        "upstream_blob_sha1": spec["upstream_git_blob_sha1"],
        "source_edition": "RP2018_BYZTXT_v3.3.2",
        "must_not_merge_without_textual_review": True,
        "passage_text_verses": [
            {"chapter": ch, "verse": v, "original_greek_text": g}
            for ch, v, g in rows
        ],
        "source_word_identifiers": None,
        "publication_status": "BLOCKED",
    }


def verify_nt_corpus(root: Path = ROOT) -> dict[str, Any]:
    reg = read_nt_inventory(root)
    total = 0
    book_counts = []
    for item in reg["continuous_books"]:
        book = read_nt_book(item["upstream_book_code"], root, reg)
        book_counts.append({
            "book": book["book_id"],
            "verses": book["verse_count"],
            "original_git_blob_sha1": book["original_file_git_blob_sha1"],
        })
        total += book["verse_count"]
    for x in reg["ancillary_readings"]:
        read_nt_ancillary(x["upstream_book_code"], root, reg)
    return {
        "status": "BYTE_IDENTICAL_CONTINUOUS_RP2018_GREEK_VERSE_SOURCE_NOT_WORD_LEXICON",
        "source_commit": reg["source_commit"],
        "books": 27,
        "greek_verse_rows": total,
        "verified_ancillary_files": 2,
        "book_verse_counts": book_counts,
        "source_word_token_ids": "NOT_IMPORTED",
        "source_lemma_morphology": "NOT_IMPORTED",
        "textual_variants_independently_reviewed": False,
        "translation_status": "NO_TRANSLATION_CREATED",
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser=argparse.ArgumentParser(description="Read-only 27-book RP2018 Greek source audit, never translation")
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit",action="store_true")
    mode.add_argument("--verse",nargs=2,metavar=("UPSTREAM_BOOK_CODE","VERSE_REFERENCE"))
    mode.add_argument("--ancillary",choices=["ACT24","PA"])
    args=parser.parse_args()
    if args.audit:
        payload=verify_nt_corpus()
    elif args.verse:
        b, verse_ref=args.verse
        book=read_nt_book(b)
        matches=[v for v in book["verses"] if v["reference"]==verse_ref]
        if len(matches)!=1:
            raise SystemExit("FAIL: original Greek NT verse reference absent or mismatched")
        payload=matches[0]
    else:
        payload=read_nt_ancillary(args.ancillary)
    print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
