"""OLT-037: provenance-preserving Greek dictionary candidate layer.

STEPBible TBESG is independent *lexicographic evidence*, not the textual
authority for Robinson-Pierpont 2018. The editor's BP5 numbers are not native
STEP dStrong identifiers. Numeric-reference overlap yields a RESEARCH CANDIDATE
SET, NEVER a selected lexical lemma, sense, translational gloss, or morphology.

STEPBible data: CC BY 4.0, STEP Bible (STEPBible.org), based on work at
Tyndale House Cambridge. Reproduce the pinned file using
scripts/fetch_olt_037_tbesg.py. No upstream file modifications or unpinned
branch fetches are performed by this module.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from typing import Any

from .engine import SourceContractError
from .sources import ROOT, git_blob_sha1
from .greek_alignment import read_aligned_greek_book
from .greek_words import read_word_manifest

MANIFEST_PATH = "data/engine/olt_037_tbesg_source_manifest.json"
_STEP_COMMIT = "be4191f0082aeedddb0eff0c02c966292b2bd641"
_STEP_BLOB = "efe271a1dbb73fa01f8fa6e0f164c6687757a9ae"
_STEP_PATH = ("Lexicons/TBESG - Translators Brief lexicon of "
              "Extended Strongs for Greek - STEPBible.org CC BY.txt")
_STEP_BYTES = 4736912
_REVISION = "27a45ff1b7be6c17ccbfeac414f3f55732ae8e28"
_ID = re.compile(r"^G([0-9]{1,5})([A-Za-z]*)$")
_DSTRONG_FIELD = re.compile(r"^(G[0-9]{1,5}[A-Za-z]*)\s*(?:=\s*(.*))?$")
_RAW_ID_PREFIX = re.compile(r"^G[0-9]")


def read_tbesg_manifest(root: Path = ROOT) -> dict[str, Any]:
    source = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
    required = {
        "checkpoint": "OLT-037",
        "source_project": "STEPBible-Data",
        "dataset": "TBESG",
        "pinned_commit": _STEP_COMMIT,
        "pinned_source_path": _STEP_PATH,
        "expected_byte_length": _STEP_BYTES,
        "original_source_git_blob_sha1": _STEP_BLOB,
        "source_data_license": "CC BY 4.0",
        "original_file_not_vendored": True,
        "candidate_ambiguities_must_be_preserved": True,
        "single_candidate_is_not_approved_lemma": True,
        "english_glosses_are_evidence_not_translations": True,
        "source_join_type": "NUMERIC_REFERENCE_CANDIDATES_ONLY",
        "independent_lexical_review": "NOT_DONE",
        "independent_morphological_review": "NOT_DONE",
        "english_master_lexicon_status": "NOT_APPROVED",
        "target_language_translation_status": "NOT_DONE",
        "publication_status": "BLOCKED",
        "rp2018_source_commit": _REVISION,
        "word_alignment_checkpoint": "OLT-036",
    }
    if any(source.get(k) != v for k, v in required.items()):
        raise SourceContractError("Pinned STEP TBESG source or scientific approval rules changed")
    return source


def verify_tbesg_bytes(raw: bytes, manifest: dict[str, Any]) -> None:
    """Original source blob must match the exact upstream Git object."""
    if (len(raw) != manifest["expected_byte_length"] or
            git_blob_sha1(raw) != manifest["original_source_git_blob_sha1"]):
        raise SourceContractError("TBESG file does not equal the pinned original source Git blob")
    try:
        raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SourceContractError("Original TBESG is not valid UTF-8") from exc


def _lexicon_line(line: str, line_no: int) -> dict[str, Any] | None:
    """Parse native TBESG columns without losing disambiguating source IDs.

    Source layout: eStrong#, dStrong, uStrong, Greek, Transliteration,
    Morph, Gloss, Meaning. Textual comments and column headers are ignored.
    A malformed line beginning with a source G-number is never discarded.
    """
    cols = line.rstrip("\r\n").split("\t")
    primary = cols[0].strip()
    if not _RAW_ID_PREFIX.match(primary):
        return None
    if not _ID.fullmatch(primary) or len(cols) != 8:
        raise SourceContractError(f"Malformed TBESG data row at source line {line_no}")
    dfield = cols[1].strip()
    match = _DSTRONG_FIELD.fullmatch(dfield)
    if not match or not _ID.fullmatch(match[1]):
        raise SourceContractError(f"Invalid disambiguated dStrong at source line {line_no}")
    reference = int(_ID.fullmatch(match[1])[1])
    if reference < 1:
        raise SourceContractError(f"Zero dStrong reference in TBESG line {line_no}")
    return {
        "source_line_number": line_no,
        "source_extended_strong": primary,
        "source_disambiguated_strong": match[1],
        "source_dstrong_relation_note": match[2] or None,
        "source_unified_strong": cols[2].strip() or None,
        "source_greek_lemma_form_candidate": cols[3].strip() or None,
        "source_transliteration": cols[4].strip() or None,
        "source_morph_category": cols[5].strip() or None,
        "source_english_short_gloss_EVIDENCE_ONLY": cols[6].strip() or None,
        "source_english_definition_EVIDENCE_ONLY": cols[7].strip() or None,
        "numeric_dstrong_reference": reference,
        "source": "STEPBible_TBESG_CC_BY_4_0",
        "lexical_form_review": "NOT_DONE",
        "sense_selection": "NOT_DONE",
        "translation_approved": False,
        "publication_status": "BLOCKED",
    }


def parse_tbesg_text(text: str) -> dict[int, list[dict[str, Any]]]:
    """Return ALL original dStrong rows, grouped by integer reference."""
    if not isinstance(text, str) or not text:
        raise SourceContractError("Empty STEP Greek lexicon source")
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    seen: set[str] = set()
    for line_no, line in enumerate(text.splitlines(), 1):
        row = _lexicon_line(line, line_no)
        if row is None:
            continue
        unique = row["source_disambiguated_strong"]
        if unique in seen:
            raise SourceContractError(f"Duplicate source dStrong {unique} on line {line_no}")
        seen.add(unique)
        groups[row["numeric_dstrong_reference"]].append(row)
    if not groups:
        raise SourceContractError("TBESG source yielded no Greek dictionary candidates")
    return dict(groups)


def read_tbesg(source_path: Path, root: Path = ROOT) -> dict[int, list[dict[str, Any]]]:
    manifest = read_tbesg_manifest(root)
    raw = source_path.read_bytes()
    verify_tbesg_bytes(raw, manifest)
    return parse_tbesg_text(raw.decode("utf-8-sig", errors="strict"))


def _word_evidence(word: dict[str, Any],
                   groups: dict[int, list[dict[str, Any]]],
                   manifest: dict[str, Any]) -> dict[str, Any]:
    """Candidates are not chosen, even if one or many match numerically."""
    editor_number = word["official_editor_strong_number"]
    if not isinstance(editor_number, str) or not editor_number.isdecimal():
        raise SourceContractError("Unrecognized original BP5 Strong-reference format")
    candidates = groups.get(int(editor_number), [])
    status = ("NO_NUMERIC_SOURCE_CANDIDATE" if not candidates else
              "ONE_NUMERIC_SOURCE_CANDIDATE_NOT_REVIEWED" if len(candidates) == 1 else
              "MULTIPLE_NUMERIC_SOURCE_CANDIDATES_UNRESOLVED")
    return {
        "olt_derived_word_locator": word["derived_source_locator"],
        "verse_reference": word["source_reference"],
        "source_unicode_surface": word["accented_unicode_word_form"],
        "source_beta_code_surface": word["beta_code_word_form"],
        "rp2018_editor_strong_number": editor_number,
        "rp2018_editor_morphology": word["official_editor_morphology_code"],
        "rp2018_editor_alternative_analyses": word["additional_editor_analyses"],
        "stepbible_source_blob_sha1": manifest["original_source_git_blob_sha1"],
        "numeric_only_source_reference_status": status,
        "candidate_count": len(candidates),
        "source_lemma_candidates_NOT_CERTIFIED": candidates,
        "selected_lemma": None,
        "selected_sense": None,
        "approved_english_translation": None,
        "independent_review": "NOT_DONE",
        "publication_status": "BLOCKED",
    }


def research_verse(code: str, reference: str,
                   groups: dict[int, list[dict[str, Any]]],
                   root: Path = ROOT) -> dict[str, Any]:
    manifest = read_tbesg_manifest(root)
    book = read_aligned_greek_book(code, root)
    candidates = [v for v in book["aligned_verses"] if v["reference"] == reference]
    if len(candidates) != 1:
        raise SourceContractError("Greek source verse missing or empty: never manufacture words")
    verse = candidates[0]
    return {
        "checkpoint": "OLT-037",
        "reference": reference,
        "original_accented_greek_verse": verse["original_accented_greek_verse"],
        "word_count": verse["source_word_count"],
        "words": [_word_evidence(w, groups, manifest) for w in verse["words"]],
        "any_lemma_or_sense_approved": False,
        "publication_status": "BLOCKED",
        "stepbible_attribution": manifest["provenance_attribution"],
    }


def audit_lemma_evidence(groups: dict[int, list[dict[str, Any]]],
                         root: Path = ROOT) -> dict[str, Any]:
    """Full 140149-word source-reference coverage audit; no guesses or glosses."""
    manifest = read_tbesg_manifest(root)
    rp = read_word_manifest(root)
    if rp["upstream_commit"] != manifest["rp2018_source_commit"]:
        raise SourceContractError("Original Greek source revisions mismatch")
    counts: Counter[str] = Counter()
    distinct_rp: set[int] = set()
    unmatched: Counter[str] = Counter()
    per_book = []
    for spec in rp["files"]:
        book = read_aligned_greek_book(spec["upstream_book_code"], root)
        local: Counter[str] = Counter()
        for verse in book["aligned_verses"]:
            for word in verse["words"]:
                num = word["official_editor_strong_number"]
                if not isinstance(num, str) or not num.isdecimal():
                    raise SourceContractError("Invalid Greek editor Strong number")
                primary = int(num)
                distinct_rp.add(primary)
                n = len(groups.get(primary, []))
                status = ("without_candidates" if n == 0 else
                          "one_candidate" if n == 1 else "multiple_candidates_unresolved")
                counts[status] += 1
                local[status] += 1
                if not n:
                    unmatched[num] += 1
                counts["primary_word_positions"] += 1
                for alt in word["additional_editor_analyses"]:
                    alt_num = alt["strong_number"]
                    if not isinstance(alt_num, str) or not alt_num.isdecimal():
                        raise SourceContractError("Invalid alternative RP2018 Strong reference")
                    counts["alternative_analyses"] += 1
                    if not groups.get(int(alt_num)):
                        counts["alternative_analyses_without_candidates"] += 1
        per_book.append({"book": book["book_id"],
                         "source_word_positions": book["aligned_word_count"],
                         "numeric_reference_candidates": dict(local)})
    if (counts["primary_word_positions"], counts["alternative_analyses"],
        len(per_book)) != (140149, 28, 27):
        raise SourceContractError("Greek corpus coverage changed since OLT-036")
    rows = sum(map(len, groups.values()))
    return {
        "checkpoint": "OLT-037",
        "source_edition": "STEPBible_TBESG",
        "source_git_blob_sha1": manifest["original_source_git_blob_sha1"],
        "stepbible_source_commit": manifest["pinned_commit"],
        "source_license": "CC BY 4.0",
        "upstream_lexicon_rows": rows,
        "upstream_distinct_numeric_references": len(groups),
        "distinct_rp2018_primary_strong_numbers": len(distinct_rp),
        "rp2018_original_word_positions": counts["primary_word_positions"],
        "word_positions_with_one_numeric_candidate": counts["one_candidate"],
        "word_positions_with_multiple_numeric_candidates_NOT_RESOLVED":
            counts["multiple_candidates_unresolved"],
        "word_positions_without_numeric_candidate": counts["without_candidates"],
        "unmatched_original_strong_numbers": dict(sorted(unmatched.items(), key=lambda x: int(x[0]))),
        "alternative_editor_analyses_preserved": counts["alternative_analyses"],
        "alternative_editor_analyses_without_numeric_candidate":
            counts["alternative_analyses_without_candidates"],
        "source_match_is_only_numeric_reference": True,
        "ambiguity_auto_resolved": False,
        "independent_lemma_form_review": "NOT_DONE",
        "independent_lexical_sense_review": "NOT_DONE",
        "rp2018_morphology_independently_verified": False,
        "english_master_lexicon_approved": False,
        "translation_generated": False,
        "publication_status": "BLOCKED",
        "attribution": manifest["provenance_attribution"],
        "per_book": per_book,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Source Greek lexicon CANDIDATES ONLY; no approval")
    parser.add_argument("--source", required=True, type=Path, help="Exact pinned TBESG file")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--verse", nargs=2, metavar=("BOOK_CODE", "REFERENCE"))
    mode.add_argument("--strong", type=int, help="Numeric RP2018 editor Strong reference")
    args = parser.parse_args()
    groups = read_tbesg(args.source)
    if args.audit:
        result = audit_lemma_evidence(groups)
    elif args.verse:
        result = research_verse(args.verse[0], args.verse[1], groups)
    else:
        if args.strong < 1:
            raise SourceContractError("Numeric original Strong reference must be positive")
        manifest = read_tbesg_manifest()
        result = {
            "original_source_editor_numeric_reference": args.strong,
            "candidate_status": "NOT_APPROVED_NO_AUTOMATIC_SELECTION",
            "candidate_rows": groups.get(args.strong, []),
            "selected_lemma": None,
            "translation": None,
            "publication_status": "BLOCKED",
            "attribution": manifest["provenance_attribution"],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
