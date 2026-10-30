"""OLT-037B: deterministic, source-first Greek numeric-reference review queue.

This creates research CASES keyed by original RP2018 editor Strong numeric
references, not certified lexemes. It does not decide whether STEPBible rows
represent homonyms, related senses, variant spelling, or unrelated entities.
Every source occurrence and alternative morphology stays in its original slot.
Input: hash-verified OLT-036 Greek source and pinned CC BY 4.0 STEP TBESG.
Output: unapproved evidence packets for later human philological scrutiny.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from .engine import SourceContractError
from .sources import ROOT
from .greek_alignment import ALIGNMENT_STATUS, read_aligned_greek_book
from .greek_lexicon import read_tbesg, read_tbesg_manifest
from .greek_words import read_word_manifest

REPORT_PATH = "data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json"
CHECKPOINT = "OLT-037B"
SOURCE_STATUS = "UNREVIEWED_NUMERIC_REFERENCE_CANDIDATE_SET"
MAX_EXAMPLES = 4


def _source_candidate_brief(row: dict[str, Any]) -> dict[str, Any]:
    """Preserve source IDs/headwords. A source gloss is never an OLT translation."""
    if row["source"] != "STEPBible_TBESG_CC_BY_4_0" or (
        row["publication_status"] != "BLOCKED" or row["translation_approved"]
    ):
        raise SourceContractError("Lexicon source row changed into translation approval")
    return {
        "native_step_dstrong": row["source_disambiguated_strong"],
        "source_extended_strong": row["source_extended_strong"],
        "source_unified_strong": row["source_unified_strong"],
        "source_relation_note": row["source_dstrong_relation_note"],
        "source_line_number": row["source_line_number"],
        "greek_lemma_HEADWORD_CANDIDATE_ONLY": row["source_greek_lemma_form_candidate"],
        "source_morph_category_NOT_VERIFIED_FOR_RP2018": row["source_morph_category"],
        "english_short_gloss_SOURCE_ONLY_NOT_OLT_TRANSLATION":
            row["source_english_short_gloss_EVIDENCE_ONLY"],
    }


def _validate_original_word(word: dict[str, Any], ref: str, position: int) -> int:
    if (word["source_reference"] != ref or
        word["ordinal_in_source_verse"] != position or
        word["unicode_word_form_alignment"] != ALIGNMENT_STATUS or
        word["original_source_native_word_id"] is not None or
        word["publication_status"] != "BLOCKED" or
        word["owner_translation"] is not None):
        raise SourceContractError("Greek word-position/source or approval contract changed")
    strong = word["official_editor_strong_number"]
    if not isinstance(strong, str) or not strong.isascii() or (
        not strong.isdecimal() or int(strong) < 1
    ):
        raise SourceContractError("Invalid original editor Greek numeric Strong reference")
    return int(strong)


def build_review_queue(groups: dict[int, list[dict[str, Any]]],
                       root: Path = ROOT) -> dict[str, Any]:
    """Full exhaustive 27-book pass with no invented disambiguation decisions."""
    source_manifest = read_tbesg_manifest(root)
    rp = read_word_manifest(root)
    if rp["upstream_commit"] != source_manifest["rp2018_source_commit"]:
        raise SourceContractError("Source Greek text revision changed beneath lexicon review")

    observed: dict[int, dict[str, Any]] = {}
    all_counts: Counter[str] = Counter()
    for spec in rp["files"]:
        book = read_aligned_greek_book(spec["upstream_book_code"], root)
        if book["publication_status"] != "BLOCKED":
            raise SourceContractError("Greek word source unexpectedly approved")
        for verse in book["aligned_verses"]:
            ref = verse["reference"]
            for index, word in enumerate(verse["words"], 1):
                number = _validate_original_word(word, ref, index)
                candidates = groups.get(number, [])
                if not candidates:
                    all_counts["unmatched_primary_word_positions"] += 1
                elif len(candidates) == 1:
                    all_counts["unique_numeric_candidate_word_positions"] += 1
                else:
                    all_counts["ambiguous_numeric_candidate_word_positions"] += 1
                    if number not in observed:
                        observed[number] = {
                            "occurrences": 0,
                            "per_book": Counter(),
                            "morphology": Counter(),
                            "unicode_surfaces": set(),
                            "sample_occurrences": [],
                        }
                    case = observed[number]
                    case["occurrences"] += 1
                    case["per_book"][book["book_id"]] += 1
                    case["morphology"][word["official_editor_morphology_code"]] += 1
                    case["unicode_surfaces"].add(word["accented_unicode_word_form"])
                    if len(case["sample_occurrences"]) < MAX_EXAMPLES:
                        case["sample_occurrences"].append({
                            "source_verse_reference": ref,
                            "olt_derived_source_word_locator": word["derived_source_locator"],
                            "source_accented_unicode_word": word["accented_unicode_word_form"],
                            "source_beta_code_word": word["beta_code_word_form"],
                            "rp2018_editor_morphology_code":
                                word["official_editor_morphology_code"],
                            "source_editor_has_alternative_analysis":
                                bool(word["additional_editor_analyses"]),
                        })
                all_counts["source_original_word_positions"] += 1
                for alt in word["additional_editor_analyses"]:
                    number_string = alt["strong_number"]
                    if (not isinstance(number_string, str) or
                        not number_string.isascii() or
                        not number_string.isdecimal() or
                        int(number_string) < 1):
                        raise SourceContractError("Invalid alternative Greek Strong reference")
                    alt_num = int(number_string)
                    alt_candidates = groups.get(alt_num, [])
                    if not alt_candidates:
                        raise SourceContractError("Unresolved missing alternative lexicon source")
                    if alt_num == number:
                        relation = "SAME_NUMERIC_STRONG_DIFFERENT_EDITOR_ANALYSIS_POSSIBLE"
                    else:
                        relation = "DISTINCT_NUMERIC_STRONG_IN_EDITOR_ALTERNATIVE"
                    all_counts["source_additional_alternative_analyses"] += 1
                    # Alternative is evidence on a single existing source word;
                    # it is NOT another primary token or selected morphological parsing.
                    # Collect all 28 in a stable, separate review inventory.
                    if "alternative_instances" not in all_counts:
                        pass

    # A second pass builds the small alternative-review list without ever
    # multiplying primary source word counts or selecting a source interpretation.
    alternative_records: list[dict[str, Any]] = []
    for spec in rp["files"]:
        book = read_aligned_greek_book(spec["upstream_book_code"], root)
        for verse in book["aligned_verses"]:
            for word in verse["words"]:
                for alt in word["additional_editor_analyses"]:
                    alternative_number = int(alt["strong_number"])
                    alternative_records.append({
                        "original_word_locator_OLT_DERIVED": word["derived_source_locator"],
                        "source_reference": verse["reference"],
                        "original_accented_greek_word": word["accented_unicode_word_form"],
                        "original_primary_editor_strong": word["official_editor_strong_number"],
                        "original_primary_editor_morphology":
                            word["official_editor_morphology_code"],
                        "original_alternative_editor_strong": alt["strong_number"],
                        "original_alternative_editor_morphology": alt["morphology_code"],
                        "numeric_strong_relationship": (
                            "SAME_NUMERIC_STRONG_DIFFERENT_EDITOR_ANALYSIS_POSSIBLE"
                            if alternative_number == int(word["official_editor_strong_number"])
                            else "DISTINCT_NUMERIC_STRONG_IN_EDITOR_ALTERNATIVE"
                        ),
                        "primary_source_dstrong_candidates": [
                            r["source_disambiguated_strong"]
                            for r in groups[int(word["official_editor_strong_number"])]
                        ],
                        "alternative_source_dstrong_candidates": [
                            r["source_disambiguated_strong"]
                            for r in groups[alternative_number]
                        ],
                        "selected_primary_or_alternative": None,
                        "linguistic_review_status": "NOT_DONE",
                        "publication_status": "BLOCKED",
                    })

    cases = []
    for number, observation in observed.items():
        rows = groups[number]
        unique_dstrong = [r["source_disambiguated_strong"] for r in rows]
        if len(set(unique_dstrong)) != len(rows) or len(rows) < 2:
            raise SourceContractError("Original candidate rows for ambiguity are not unique")
        names = [r["source_greek_lemma_form_candidate"] for r in rows]
        # Literal form comparison ONLY, never call homonym/sense equivalence.
        cases.append({
            "case_id_OLT_DERIVED": f"RP2018-v3.3.2-NumericStrong-{number}",
            "original_rp2018_strong_number": str(number),
            "source_word_occurrence_count": observation["occurrences"],
            "source_candidate_count": len(rows),
            "source_dstrong_candidates": [
                _source_candidate_brief(r) for r in rows
            ],
            "source_headword_surfaces_differ_literally": len(set(names)) > 1,
            "source_headword_surface_count": len(set(names)),
            "observed_rp2018_unicode_surface_form_count":
                len(observation["unicode_surfaces"]),
            "rp2018_editor_morphology_annotation_frequencies": dict(sorted(
                observation["morphology"].items()
            )),
            "occurrence_counts_by_book": dict(sorted(observation["per_book"].items())),
            "up_to_four_original_source_examples": observation["sample_occurrences"],
            "candidate_ambiguity_kind": "MULTIPLE_STEP_DSTRONG_SAME_NUMERIC_PORTION",
            "scientific_classification": "NOT_YET_DETERMINED",
            "homonym_vs_polysemy_vs_entity_distinction": "NOT_REVIEWED",
            "source_evidence_status": SOURCE_STATUS,
            "selected_dstrong": None,
            "selected_greek_lemma": None,
            "selected_lexical_sense": None,
            "approved_english_master_entry": None,
            "owner_editorial_approval": False,
            "independent_philological_signoff": False,
            "publication_status": "BLOCKED",
        })
    cases.sort(key=lambda x: (-x["source_word_occurrence_count"],
                              int(x["original_rp2018_strong_number"])))
    if (all_counts["source_original_word_positions"] != 140149 or
        all_counts["ambiguous_numeric_candidate_word_positions"] != 12539 or
        all_counts["unique_numeric_candidate_word_positions"] != 127610 or
        all_counts["unmatched_primary_word_positions"] != 0 or
        all_counts["source_additional_alternative_analyses"] != 28 or
        len(alternative_records) != 28 or
        sum(x["source_word_occurrence_count"] for x in cases) != 12539):
        raise SourceContractError("OLT-037B primary source/triage counts disagree with OLT-037A")
    if len({x["case_id_OLT_DERIVED"] for x in cases}) != len(cases):
        raise SourceContractError("Duplicated Greek OLT-derived review case ID")
    if any(len(x["source_dstrong_candidates"]) < 2 or
           x["selected_dstrong"] is not None or
           x["independent_philological_signoff"] for x in cases):
        raise SourceContractError("Source candidate list was silently resolved/approved")

    return {
        "checkpoint": CHECKPOINT,
        "scope": "NUMERIC_REFERENCE_REVIEW_CASES_NOT_APPROVED_LEXEMES",
        "rp2018_pinned_source_commit": rp["upstream_commit"],
        "stepbible_pinned_source_commit": source_manifest["pinned_commit"],
        "stepbible_source_git_blob_sha1": source_manifest["original_source_git_blob_sha1"],
        "stepbible_license": "CC BY 4.0",
        "stepbible_attribution": source_manifest["provenance_attribution"],
        "upstream_row_count": sum(len(v) for v in groups.values()),
        "rp2018_primary_word_positions": all_counts["source_original_word_positions"],
        "primary_positions_with_single_numeric_candidate":
            all_counts["unique_numeric_candidate_word_positions"],
        "primary_positions_with_multiple_numeric_candidates":
            all_counts["ambiguous_numeric_candidate_word_positions"],
        "primary_positions_without_numeric_candidate":
            all_counts["unmatched_primary_word_positions"],
        "distinct_numeric_reference_review_cases": len(cases),
        "original_editor_alternative_analyses": len(alternative_records),
        "queue_sort_order": "WORD_OCCURRENCE_FREQUENCY_DESC_THEN_NUMERIC_STRONG_ASC",
        "numeric_join_proves_lemma": False,
        "word_occurrence_count_does_not_equal_distinct_lexeme_count": True,
        "morphological_tags_independently_verified": False,
        "homonyms_or_senses_automatically_classified": False,
        "reviewed_cases": 0,
        "approved_english_lexical_entries": 0,
        "target_language_translations_generated": 0,
        "publication_status": "BLOCKED",
        "cases": cases,
        "original_editor_alternative_analysis_review_queue": alternative_records,
    }


def serialize_review_queue(result: dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def verify_committed_queue(result: dict[str, Any], root: Path = ROOT) -> None:
    path = root / REPORT_PATH
    if not path.is_file() or path.read_text(encoding="utf-8") != serialize_review_queue(result):
        raise SourceContractError("OLT-037B pinned-source review queue is absent or drifted")


def emit_checkpoint_chunks(result: dict[str, Any]) -> None:
    """Lossless log transfer for the FIRST report pin; final CI verifies file."""
    payload = serialize_review_queue(result).encode("utf-8")
    b64 = base64.b64encode(payload).decode("ascii")
    print("OLT037B_CHECKPOINT_BEGIN")
    for i in range(0, len(b64), 4000):
        print("OLT037B_CHECKPOINT_PART " + b64[i:i+4000])
    print("OLT037B_CHECKPOINT_END " + hashlib.sha256(payload).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser(description="OLT-037B source lexical triage (NOT approval)")
    parser.add_argument("--source", required=True, type=Path)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--summary", action="store_true")
    commands.add_argument("--case", type=int)
    commands.add_argument("--verify-checkpoint", action="store_true")
    commands.add_argument("--emit-checkpoint-chunks", action="store_true")
    args = parser.parse_args()
    groups = read_tbesg(args.source)
    report = build_review_queue(groups)
    if args.verify_checkpoint:
        verify_committed_queue(report)
        result = {"checkpoint": CHECKPOINT,
                  "exact_committed_queue_reproduced": True,
                  "case_count": report["distinct_numeric_reference_review_cases"],
                  "publication_status": "BLOCKED"}
    elif args.emit_checkpoint_chunks:
        emit_checkpoint_chunks(report)
        return 0
    elif args.case is not None:
        if args.case < 1:
            raise SourceContractError("Greek numeric source reference must be positive")
        matches = [x for x in report["cases"]
                   if int(x["original_rp2018_strong_number"]) == args.case]
        if len(matches) != 1:
            raise SourceContractError("No multiple-candidate Greek case with this number")
        result = {"checkpoint": CHECKPOINT, "case": matches[0],
                  "publication_status": "BLOCKED",
                  "attribution": report["stepbible_attribution"]}
    else:
        result = {k: v for k, v in report.items()
                  if k not in {"cases", "original_editor_alternative_analysis_review_queue"}}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
