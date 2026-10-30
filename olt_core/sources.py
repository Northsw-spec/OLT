"""OLT-035 original-source integrity adapters.

No English-based translation. The imported OT JSON is verified against exact
Git blob hashes and imported upstream-XML SHA-256 provenance recorded earlier.
The RP2018 Unicode CSV sample is verified against the official upstream Git
blob hash. Its VERSE TEXT is retained without inventing word IDs/morphology.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from hashlib import sha1
from io import StringIO
import json
from pathlib import Path
import re
from typing import Any

from .engine import SourceContractError, validate_source

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ADAPTER_VERSION = "0.1.0"
_PROVENANCE_PATH = Path("data/engine/olt_035_source_provenance.json")
_OT_MANIFEST_PATH = Path("data/imported/manifest.json")
_EXACT_NUMERIC_COMPONENT = re.compile(r"^\d{1,5}(?:\s+[a-z]|\+)?$")
_VERSE_REF = re.compile(r"^[A-Za-z0-9]+\.[1-9]\d*\.[1-9]\d*$")
_GREEK_LETTER = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")


def git_blob_sha1(data: bytes) -> str:
    """SHA-1 of Git blob bytes, not a prose source-text or philological check."""
    if not isinstance(data, bytes):
        raise SourceContractError("Git blob digest input must be raw bytes")
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def read_provenance(root: Path = ROOT) -> dict[str, Any]:
    value = json.loads((root / _PROVENANCE_PATH).read_text(encoding="utf-8"))
    ot, nt = value.get("ot", {}), value.get("nt", {})
    if value.get("checkpoint") != "OLT-035" or value.get("publication_status") != "BLOCKED":
        raise SourceContractError("Wrong source provenance checkpoint or false Bible publication")
    if ot.get("imported_book_count") != 39 or len(ot.get("books", [])) != 39:
        raise SourceContractError("OT source provenance must enumerate all 39 imported books")
    if (ot.get("upstream_commit") != "3d15126fb1ef74867fc1434be1942e837932691f" or
        nt.get("edition") != "ROBINSON_PIERPONT_2018" or
        nt.get("upstream_commit") != "27a45ff1b7be6c17ccbfeac414f3f55732ae8e28" or
        nt.get("upstream_tag") != "v3.3.2"):
        raise SourceContractError("Unexpected original-language source revision")
    if nt.get("full_nt_text_import_complete") is not False or nt.get("full_nt_token_identifiers_imported") is not False:
        raise SourceContractError("RP2018 Greek word corpus is not completely imported")
    if value.get("independent_source_review") != "NOT_DONE":
        raise SourceContractError("Imported text cannot claim independent philological review")
    return value


def _book_spec(registry: dict[str, Any], book: str) -> dict[str, Any]:
    if not isinstance(book, str) or not re.fullmatch(r"[1-9]?[A-Za-z]{2,5}", book):
        raise SourceContractError("Invalid OT book name")
    matches = [row for row in registry["ot"]["books"] if row.get("book") == book]
    if len(matches) != 1:
        raise SourceContractError("Book is not one of 39 pinned original OT books")
    spec = matches[0]
    if spec["book_json_path"] != "data/imported/books/" + book + ".json":
        raise SourceContractError("Book path is not the pinned imported-OT path")
    return spec


def load_ot_book(book: str, root: Path = ROOT, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verify exact immutable OLT-imported bytes, not the remote XML online."""
    reg = registry if registry is not None else read_provenance(root)
    spec = _book_spec(reg, book)
    raw = (root / spec["book_json_path"]).read_bytes()
    if git_blob_sha1(raw) != spec["book_json_git_blob_sha1"]:
        raise SourceContractError("OT imported book Git blob digest differs from pinned source snapshot")
    if len(raw) != spec["book_json_bytes"]:
        raise SourceContractError("OT imported book byte length differs from pinned snapshot")
    contents = json.loads(raw)
    if contents.get("book") != book or contents.get("source_commit") != reg["ot"]["upstream_commit"]:
        raise SourceContractError("OT imported book has wrong upstream source identity")
    if not isinstance(contents.get("verses"), list) or not contents["verses"]:
        raise SourceContractError("OT source book must contain original verses")
    return contents


def ot_morph_language(raw_morph: str) -> str:
    if not isinstance(raw_morph, str) or not raw_morph:
        raise SourceContractError("Missing original OT morphology language tag")
    if raw_morph[0] == "H":
        return "hbo"
    if raw_morph[0] == "A":
        return "arc"
    raise SourceContractError("Unrecognized original OT morphology language tag")


def exact_source_lemma_components(raw_lemma: str) -> list[str]:
    if not isinstance(raw_lemma, str):
        raise SourceContractError("Raw source lemma annotation must be a string")
    return [piece.strip() for piece in raw_lemma.split("/")
            if _EXACT_NUMERIC_COMPONENT.fullmatch(piece.strip())]


def normalize_ot_verse(book: str, verse_id: str, root: Path = ROOT,
                       registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return original-source words, not target-language words or guessed lexemes."""
    reg = registry if registry is not None else read_provenance(root)
    contents = load_ot_book(book, root, reg)
    if (not isinstance(verse_id, str) or
        not _VERSE_REF.fullmatch(verse_id) or
        not verse_id.startswith(book + ".")):
        raise SourceContractError("Wrong OT verse ID or mismatched book")
    matches = [row for row in contents["verses"] if row.get("reference") == verse_id]
    if len(matches) != 1:
        raise SourceContractError("Requested original OT verse is absent or ambiguous")
    original = matches[0].get("words")
    if not isinstance(original, list) or not original:
        raise SourceContractError("Original OT verse lacks word tokens")
    tokens = []
    seen: set[str] = set()
    for index, word in enumerate(original, 1):
        if (word.get("ordinal") != index or word.get("reference") != verse_id or
            word.get("source_status") != "IMPORTED_UNREVIEWED"):
            raise SourceContractError("Original OT word ordinal/reference or source review was changed")
        token_id = word.get("source_id")
        script = word.get("hebrew")
        morph = word.get("morph_raw")
        raw_lemma = word.get("lemma_raw")
        if (not isinstance(token_id, str) or not token_id or
            not isinstance(script, str) or not script):
            raise SourceContractError("Missing original OT source word ID or original script")
        if token_id in seen:
            raise SourceContractError("Duplicate original word ID in verse")
        seen.add(token_id)
        lang = ot_morph_language(morph)
        components = exact_source_lemma_components(raw_lemma)
        resolved = len(components) == 1 and not components[0].endswith("+")
        token = {
            "verse_id": verse_id,
            "ordinal": index,
            "token_id": token_id,
            "original_script": script,
            "raw_lemma": raw_lemma,
            "source_lemma_components": components,
            "lemma_id": components[0] if resolved else None,
            "lemma_resolution_status": "SOURCE_SINGLE_NUMERIC_COMPONENT_UNREVIEWED" if resolved
                else "UNRESOLVED_OR_FLAGGED_DO_NOT_GUESS",
            "raw_morphology": morph,
            "source_language": lang,
            "corpus": "OT",
            "edition_id": "OSHB_WLC_" + reg["ot"]["upstream_commit"],
            "edition_status": "IMPORTED_NOT_INDEPENDENTLY_REVIEWED",
            "source_snapshot_imported_book_git_blob_sha1":
                _book_spec(reg, book)["book_json_git_blob_sha1"],
            "source_original_osis_xml_sha256_recorded_not_rechecked":
                _book_spec(reg, book)["upstream_osis_xml_sha256"],
            "scholarly_review": "NOT_DONE",
            "publication_status": "BLOCKED",
        }
        if resolved:
            validate_source(token)
        tokens.append(token)
    return {
        "source_ref": verse_id,
        "book": book,
        "source_edition": "OSHB_WLC_" + reg["ot"]["upstream_commit"],
        "source_language_counts": dict(Counter(row["source_language"] for row in tokens)),
        "source_word_count": len(tokens),
        "tokens": tokens,
        "translated_text": None,
        "human_review": "NOT_DONE",
        "publication_status": "BLOCKED",
    }


def verify_ot_corpus(root: Path = ROOT, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verify all 39 imported Git blobs plus exact source IDs, morphology tags, totals."""
    reg = registry if registry is not None else read_provenance(root)
    manifest = json.loads((root / _OT_MANIFEST_PATH).read_text(encoding="utf-8"))
    ot = reg["ot"]
    if (manifest.get("morphhb", {}).get("commit") != ot["upstream_commit"] or
        manifest.get("corpus", {}).get("books_sha256") !=
        {x["book"] + ".xml": x["upstream_osis_xml_sha256"] for x in ot["books"]}):
        raise SourceContractError("Recorded upstream original XML hash/commit differs from imported manifest")
    if (manifest["corpus"].get("word_tokens"), manifest["corpus"].get("verses")) != (
        ot["imported_word_token_count"], ot["imported_verse_count"]
    ):
        raise SourceContractError("Imported source totals differ from provenance manifest")
    all_ids: set[str] = set()
    lang_count: Counter[str] = Counter()
    words, verses = 0, 0
    names: set[str] = set()
    for spec in ot["books"]:
        book = spec["book"]
        if book in names:
            raise SourceContractError("Duplicated book in source provenance registry")
        names.add(book)
        body = load_ot_book(book, root, reg)
        for v in body["verses"]:
            verse_id = v.get("reference", "")
            if not isinstance(verse_id, str) or not _VERSE_REF.fullmatch(verse_id) or not verse_id.startswith(book+"."):
                raise SourceContractError("Invalid original OT verse reference")
            verses += 1
            for expected_order, w in enumerate(v.get("words", []), 1):
                if w.get("reference") != verse_id or w.get("ordinal") != expected_order:
                    raise SourceContractError("Original OT word order or reference broken")
                original_id = w.get("source_id")
                if not isinstance(original_id, str) or not original_id or original_id in all_ids:
                    raise SourceContractError("Missing or duplicate immutable OSHB word ID")
                all_ids.add(original_id)
                if w.get("source_status") != "IMPORTED_UNREVIEWED":
                    raise SourceContractError("Unreviewed source incorrectly certified")
                morph = w.get("morph_raw")
                lang_count[ot_morph_language(morph)] += 1
                if not w.get("hebrew") or not isinstance(w.get("lemma_raw"), str):
                    raise SourceContractError("Missing actual original-language word or lemma field")
                words += 1
    if len(names) != 39 or words != ot["imported_word_token_count"] or verses != ot["imported_verse_count"] or len(all_ids) != words:
        raise SourceContractError("Whole OT source corpus coverage changed")
    if (lang_count["hbo"], lang_count["arc"]) != (
        ot["imported_morphology_tagged_hebrew_tokens"],
        ot["imported_morphology_tagged_aramaic_tokens"]
    ):
        raise SourceContractError("Original OT Hebrew/Aramaic language-tag audit changed")
    return {
        "status": "IMPORTED_OT_SOURCE_BLOBS_MATCH_PINNED_MANIFEST_NOT_PHILOLOGICAL_REVIEW",
        "books": len(names), "verses": verses, "word_tokens": words,
        "tagged_hebrew": lang_count["hbo"], "tagged_aramaic": lang_count["arc"],
        "upstream_xml_sha256_status": "RECORDED_NOT_RECOMPUTED_IN_THIS_CHECK",
        "independent_morphology_review": "NOT_DONE",
        "publication_status": "BLOCKED",
    }


def read_greek_3john(root: Path = ROOT, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verify exact tagged RP2018-derived Greek verse text; DO NOT invent word IDs."""
    reg = registry if registry is not None else read_provenance(root)
    nt = reg["nt"]
    if (nt.get("sample_book_code"), nt.get("sample_standard_book")) != ("3JO", "3John"):
        raise SourceContractError("Unexpected Greek source book identity")
    sample_path = nt.get("sample_local_path")
    if sample_path != "data/imported/nt/rp2018/3JO.csv":
        raise SourceContractError("Unexpected Greek source sample path")
    raw = (root / sample_path).read_bytes()
    if git_blob_sha1(raw) != nt["sample_derived_unicode_csv_upstream_git_blob_sha1"]:
        raise SourceContractError("Greek original RP2018 sample is not byte-identical to pinned upstream")
    contents = raw.decode("utf-8", errors="strict")
    parsed = csv.DictReader(StringIO(contents, newline=""))
    if parsed.fieldnames != ["chapter", "verse", "text"]:
        raise SourceContractError("Greek original Unicode CSV header differs")
    verses = []
    for row in parsed:
        if None in row or set(row) != {"chapter", "verse", "text"}:
            raise SourceContractError("Malformed Greek source verse row")
        if row["chapter"] != "1" or row["verse"] != str(len(verses) + 1):
            raise SourceContractError("Original Greek source verse/order differs")
        text = row["text"]
        if not isinstance(text, str) or not _GREEK_LETTER.search(text):
            raise SourceContractError("Missing real Greek original text")
        verses.append({
            "verse_id": "3John.1." + row["verse"],
            "source_language": "grc",
            "original_script_verse_text": text,
            "source_edition": "ROBINSON_PIERPONT_2018_v3.3.2",
            "source_raw_file": sample_path,
            "source_original_git_blob_sha1": nt["sample_derived_unicode_csv_upstream_git_blob_sha1"],
            "source_kind": "UPSTREAM_DERIVED_UNICODE_CSV_NOT_OFFICIAL_CC_AT_VERIFIED_WORD_LEVEL",
            "word_token_ids": None,
            "lemma_ids": None,
            "raw_morphology": None,
            "translation": None,
            "editorial_review": "NOT_DONE",
            "publication_status": "BLOCKED",
        })
    if len(verses) != nt["expected_verses_in_sample"] or len(verses) != 14:
        raise SourceContractError("Greek original text sample verse coverage incomplete")
    return {
        "edition": "ROBINSON_PIERPONT_2018",
        "upstream_commit": nt["upstream_commit"],
        "source_book": "3John",
        "source_language": "grc",
        "verse_count": len(verses),
        "verses": verses,
        "word_tokenization": "NOT_DONE",
        "source_status": "EXACT_UPSTREAM_CSV_BYTES_PINNED_ONE_BOOK_SAMPLE",
        "greek_morphology_status": "NOT_IMPORTED",
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="OLT-035 original-language source verification (not Bible translation)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--audit-ot", action="store_true")
    group.add_argument("--ot-verse", nargs=2, metavar=("BOOK", "VERSE"))
    group.add_argument("--greek-3john", action="store_true")
    args = parser.parse_args()
    if args.audit_ot:
        output = verify_ot_corpus()
    elif args.ot_verse is not None:
        output = normalize_ot_verse(*args.ot_verse)
    else:
        output = read_greek_3john()
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
