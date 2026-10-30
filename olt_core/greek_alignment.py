"""OLT-036: fail-closed RP2018 BP5 -> accented Greek Unicode word crosswalk.

The BP5 (Strong/morphology) file and the Unicode CSV are independently pinned
upstream-derived witnesses of the same RP2018 source revision. Alignment is
evidence of SOURCE WORD POSITION + LOSSY ORTHOGRAPHIC EQUIVALENCE ONLY.
It is not an original publisher token ID, lexical lemma, spelling identity,
independently reviewed morphology, translation, or approval to publish.

Original Beta Code does not encode accents/breathings/diaeresis or the Greek
iota subscript present in Unicode. Both original spellings remain preserved.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import unicodedata
from typing import Any

from .engine import SourceContractError
from .sources import ROOT
from .greek_words import read_word_manifest, read_parsed_greek_book
from .nt_corpus import read_nt_inventory, read_nt_book

CHECKPOINT = "OLT-036"
ALIGNMENT_STATUS = "MATCHED_POSITION_AND_LOSSY_NORMALIZED_ORTHOGRAPHY"
NORMALIZATION_ID = "OLT-036-RP2018-BP5-UNICODE-V1"
# Beta Code here is the unaccented 24-letter transcription actually observed in
# the pinned source/Strongs/*.BP5 files. Do not silently accept other codes.
_BETA_TO_GREEK = {
    "a": "α", "b": "β", "g": "γ", "d": "δ", "e": "ε", "z": "ζ",
    "h": "η", "q": "θ", "i": "ι", "k": "κ", "l": "λ", "m": "μ",
    "n": "ν", "c": "ξ", "o": "ο", "p": "π", "r": "ρ", "s": "σ",
    "t": "τ", "u": "υ", "f": "φ", "x": "χ", "y": "ψ", "w": "ω",
}
_BETA = re.compile(r"^[a-z]+$")
# Finite, explicitly documented LOSSY operations. U+0345 is iota subscript,
# *not* merely an accent; its removal may mask an orthographic distinction.
_DROPPED_MARKS = frozenset("\u0300\u0301\u0308\u0313\u0314\u0342\u0345")
_IOTA_SUBSCRIPT = "\u0345"
_EXPECTED_EMPTY = frozenset({
    "Luke.17.36", "Acts.8.37", "Acts.15.34", "Acts.24.7",
})


def _beta_to_unaccented_greek(word: str) -> str:
    """Reject unfamiliar source notation instead of inventing equivalents."""
    if not isinstance(word, str) or not _BETA.fullmatch(word):
        raise SourceContractError("Unsupported original RP2018 unaccented Beta Code word")
    try:
        return "".join(_BETA_TO_GREEK[char] for char in word)
    except KeyError as exc:
        raise SourceContractError("Unsupported source Beta Code letter") from exc


def _is_greek_letter(char: str) -> bool:
    return (unicodedata.category(char).startswith("L")
            and "GREEK" in unicodedata.name(char, ""))


def greek_unicode_tokens(text: str) -> list[dict[str, Any]]:
    """Preserve exact original accented surfaces and [start,end) offsets.

    Greek punctuation, paragraph signs and typographic apostrophes separate
    words without becoming invented Greek source tokens. Foreign letters fail.
    """
    if not isinstance(text, str) or not text:
        raise SourceContractError("Missing original accented Greek Unicode verse")
    tokens: list[dict[str, Any]] = []
    start: int | None = None

    def finish(end: int) -> None:
        nonlocal start
        if start is not None:
            tokens.append({
                "surface": text[start:end],
                "start": start,
                "end": end,
            })
            start = None

    for i, char in enumerate(text):
        category = unicodedata.category(char)
        if _is_greek_letter(char):
            if start is None:
                start = i
        elif category.startswith("M") and start is not None:
            # Diacritics belong to the preceding Greek letter.
            continue
        else:
            finish(i)
            if category.startswith("L"):
                raise SourceContractError("Non-Greek letter inside pinned Unicode Greek verse")
            if category.startswith("M"):
                raise SourceContractError("Orphan Greek diacritic outside word")
    finish(len(text))
    if not tokens:
        raise SourceContractError("Unicode verse has zero Greek words")
    return tokens


def _normalized_greek_unicode(surface: str) -> tuple[str, bool]:
    """Lossy comparison key; never substitute it for the original word."""
    if not surface or any(not _is_greek_letter(c) and not unicodedata.category(c).startswith("M")
                          for c in surface):
        raise SourceContractError("Invalid Unicode Greek word surface")
    decomposed = unicodedata.normalize("NFD", surface.lower())
    subscript = _IOTA_SUBSCRIPT in decomposed
    normalized: list[str] = []
    for char in decomposed:
        if char in _DROPPED_MARKS:
            continue
        if unicodedata.category(char).startswith("M"):
            raise SourceContractError("Unknown Unicode Greek diacritic; manual review required")
        if not _is_greek_letter(char):
            raise SourceContractError("Unexpected character in Greek normalized word")
        normalized.append("σ" if char == "ς" else char)
    return "".join(normalized), subscript


def _align_word_verse(source: dict[str, Any], verse: dict[str, Any]) -> dict[str, Any]:
    """One verse only. Any same-length mismatch fails closed, no fuzzy join."""
    reference = source["reference"]
    if verse["reference"] != reference or not source["contains_greek_word_forms"]:
        raise SourceContractError("Verse join requires identical nonempty source references")
    original_text = verse["original_greek_text"]
    tokens = greek_unicode_tokens(original_text)
    words = source["words"]
    if len(words) != len(tokens) or len(words) != source["source_word_count"]:
        raise SourceContractError(f"{reference}: BP5/Unicode word counts differ")
    aligned = []
    subscripts = 0
    for i, (word, token) in enumerate(zip(words, tokens), 1):
        if word["ordinal_in_source_verse"] != i or word["source_reference"] != reference:
            raise SourceContractError("Derived BP5 ordinal/reference has been altered")
        beta_key = _beta_to_unaccented_greek(word["beta_code_word_form"])
        greek_key, subscript = _normalized_greek_unicode(token["surface"])
        if beta_key != greek_key:
            raise SourceContractError(
                f"{reference}: position {i} Beta Code/Unicode mismatch; no alignment allowed"
            )
        subscripts += int(subscript)
        original_word = deepcopy(word)
        if original_word.get("unicode_word_form_alignment") != "NOT_PERFORMED" or (
            original_word.get("accented_unicode_word_form") is not None
        ):
            raise SourceContractError("Already assigned unreviewed original Unicode word surface")
        original_word["accented_unicode_word_form"] = token["surface"]
        original_word["unicode_word_form_alignment"] = ALIGNMENT_STATUS
        original_word["unicode_verse_character_span"] = {
            "start": token["start"], "end_exclusive": token["end"],
        }
        original_word["unicode_word_position_derived_by_olt"] = i
        original_word["alignment_normalization_id"] = NORMALIZATION_ID
        original_word["alignment_is_lossy_and_not_lemma_approval"] = True
        original_word["unicode_surface_has_iota_subscript"] = subscript
        aligned.append(original_word)
    return {
        "reference": reference,
        "original_accented_greek_verse": original_text,
        "source_bp5_file": source["source_file"],
        "source_bp5_git_blob_sha1": source["source_git_blob_sha1"],
        "source_word_count": len(aligned),
        "words_with_unicode_iota_subscript": subscripts,
        "word_alignment_status": ALIGNMENT_STATUS,
        "alignment_normalization_id": NORMALIZATION_ID,
        "words": aligned,
        "independent_lexical_or_morphological_review": "NOT_DONE",
        "owner_translation": None,
        "publication_status": "BLOCKED",
    }


def read_aligned_greek_book(code: str, root: Path = ROOT) -> dict[str, Any]:
    """Read both independently hash-validated sources; require 1:1 verse coverage."""
    word_manifest = read_word_manifest(root)
    verse_inventory = read_nt_inventory(root)
    if [x["upstream_book_code"] for x in word_manifest["files"]] != [
        x["upstream_book_code"] for x in verse_inventory["continuous_books"]
    ] or word_manifest["upstream_commit"] != verse_inventory["source_commit"]:
        raise SourceContractError("RP2018 Greek source revision/book inventories differ")
    book = read_parsed_greek_book(code, root, word_manifest)
    unicode_book = read_nt_book(code, root, verse_inventory)
    if book["book_id"] != unicode_book["book_id"]:
        raise SourceContractError("Mismatched Greek source book IDs")
    original_by_ref = {v["reference"]: v for v in book["verse_records"]}
    unicode_by_ref = {v["reference"]: v for v in unicode_book["verses"]}
    if len(original_by_ref) != book["verse_count"] or (
        len(unicode_by_ref) != unicode_book["verse_count"]
    ):
        raise SourceContractError("Duplicate Greek source verse references")
    extra = set(original_by_ref) - set(unicode_by_ref)
    expected_extra = {ref for ref in _EXPECTED_EMPTY if ref.startswith(book["book_id"] + ".")}
    if extra != expected_extra or set(unicode_by_ref) - set(original_by_ref):
        raise SourceContractError("Unexpected Greek BP5/Unicode verse witness difference")
    empty = []
    aligned = []
    for source in book["verse_records"]:
        ref = source["reference"]
        if ref in extra:
            if source["contains_greek_word_forms"] or source["source_word_count"] != 0:
                raise SourceContractError("Source-only Greek position must have ZERO words")
            empty.append({
                "reference": ref,
                "position_type": "EMPTY_ORIGINAL_BP5_VERSE_PLACEHOLDER",
                "unicode_verse_absent": True,
                "word_count": 0,
                "publication_status": "BLOCKED",
            })
        else:
            aligned.append(_align_word_verse(source, unicode_by_ref[ref]))
    if len(aligned) != unicode_book["verse_count"]:
        raise SourceContractError("Greek Unicode verse alignment incomplete")
    return {
        "checkpoint": CHECKPOINT,
        "book_code": code,
        "book_id": book["book_id"],
        "edition_commit": word_manifest["upstream_commit"],
        "original_bp5_git_blob_sha1": book["source_git_blob_sha1"],
        "original_unicode_git_blob_sha1": unicode_book["original_file_git_blob_sha1"],
        "aligned_verse_count": len(aligned),
        "aligned_word_count": sum(x["source_word_count"] for x in aligned),
        "alternative_editor_parsings_preserved": book["additional_alternative_parse_pairs"],
        "empty_bp5_placeholders": empty,
        "alignment_status": ALIGNMENT_STATUS,
        "normalization_id": NORMALIZATION_ID,
        "normalization_suppresses_iota_subscript": True,
        "publisher_native_word_ids_available": False,
        "independent_morphological_review": "NOT_DONE",
        "independent_lemma_review": "NOT_DONE",
        "publication_status": "BLOCKED",
        "aligned_verses": aligned,
    }


def verify_greek_word_alignment(root: Path = ROOT) -> dict[str, Any]:
    """Full-corpus read-only audit. Reject ANY count, spelling or position drift."""
    manifest = read_word_manifest(root)
    counts = {
        "verses": 0, "words": 0, "alternatives": 0, "empty": 0,
        "tokens_with_unicode_iota_subscript": 0,
    }
    by_book = []
    all_ids = set()
    all_empty = set()
    for spec in manifest["files"]:
        result = read_aligned_greek_book(spec["upstream_book_code"], root)
        words = result["aligned_word_count"]
        counts["verses"] += result["aligned_verse_count"]
        counts["words"] += words
        counts["alternatives"] += result["alternative_editor_parsings_preserved"]
        counts["empty"] += len(result["empty_bp5_placeholders"])
        all_empty.update(x["reference"] for x in result["empty_bp5_placeholders"])
        for verse in result["aligned_verses"]:
            counts["tokens_with_unicode_iota_subscript"] += verse["words_with_unicode_iota_subscript"]
            for word in verse["words"]:
                loc = word["derived_source_locator"]
                if loc in all_ids:
                    raise SourceContractError("Duplicate derived Greek token locator across books")
                all_ids.add(loc)
                if word["original_source_native_word_id"] is not None or (
                    word["owner_translation"] is not None
                ) or word["publication_status"] != "BLOCKED":
                    raise SourceContractError("False native word identity or translation approval")
        by_book.append({
            "book": result["book_id"],
            "aligned_verses": result["aligned_verse_count"],
            "aligned_words": words,
            "alternative_editor_parses": result["alternative_editor_parsings_preserved"],
            "empty_slots": len(result["empty_bp5_placeholders"]),
        })
    if (counts["verses"], counts["words"], counts["alternatives"], counts["empty"]) != (
        7953, 140149, 28, 4
    ) or all_empty != _EXPECTED_EMPTY or len(all_ids) != counts["words"]:
        raise SourceContractError("OLT-036 complete corpus evidence totals changed")
    return {
        "checkpoint": CHECKPOINT,
        "source_revision": manifest["upstream_commit"],
        "books": len(by_book),
        "fully_position_and_normalization_matched_verses": counts["verses"],
        "fully_position_and_normalization_matched_words": counts["words"],
        "unicode_tokens_with_iota_subscript_ignored_in_comparison":
            counts["tokens_with_unicode_iota_subscript"],
        "source_morphology_alternative_analyses_preserved": counts["alternatives"],
        "source_only_empty_verse_positions": sorted(all_empty),
        "alignment_method": ALIGNMENT_STATUS,
        "normalization_id": NORMALIZATION_ID,
        "alignment_requires_same_position_and_normalized_spelling": True,
        "normalization_is_lossy": True,
        "original_source_surfaces_remain_intact": True,
        "publisher_native_word_ids_available": False,
        "independent_morphology_and_lexical_sense_review": "NOT_DONE",
        "english_master_lexicon_approved": False,
        "target_language_translation_approved": False,
        "publication_status": "BLOCKED",
        "per_book": by_book,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="OLT-036 original Greek word join; NOT translation")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--audit", action="store_true")
    action.add_argument("--verse", nargs=2, metavar=("SOURCE_BOOK_CODE", "REFERENCE"))
    args = parser.parse_args()
    if args.audit:
        result = verify_greek_word_alignment()
    else:
        code, ref = args.verse
        book = read_aligned_greek_book(code)
        matches = [v for v in book["aligned_verses"] if v["reference"] == ref]
        if len(matches) != 1:
            raise SystemExit("No verified original Greek word-bearing verse at this reference")
        result = matches[0]
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
