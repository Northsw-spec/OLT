"""OLT-037C: exact-source Greek contextual evidence dossiers, not approvals.

Review subjects: RP2018 numeric editor Strong references 3004 (primary) and
3754 (methodological control). Both have two STEPBible dStrong dictionary rows
with the same literal Greek headword but different publisher gloss evidence.
The fact that a source tags one entry 'a Meaning of' is SOURCE METADATA, NOT
independent proof of contextual sense selection, polysemy, or homonymy.

Greek original source: Robinson-Pierpont 2018 ByzTxt v3.3.2, pinned source
word files and accented text files independently verified by OLT-035D/036.
Dictionary source: STEPBible TBESG at original byte-verified pinned commit,
CC BY 4.0. Attribution: STEP Bible (www.STEPBible.org), originally based
on work at Tyndale House Cambridge.
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
from .greek_alignment import ALIGNMENT_STATUS, read_aligned_greek_book
from .greek_lemma_triage import (
    REPORT_PATH as PREVIOUS_REPORT_PATH, _source_candidate_brief,
    _validate_original_word,
)
from .greek_lexicon import read_tbesg, read_tbesg_manifest
from .greek_words import read_word_manifest
from .sources import ROOT

CHECKPOINT = "OLT-037C"
REPORT_PATH = "data/quality/olt_037c_greek_contextual_research_dossiers.json"
CASE_NUMBERS = (3004, 3754)
PREVIOUS_REPORT_SHA256 = "a0291d66b506f7070263e8afc8c78ac160d2f9081720993b487e0cee3bc6db5b"
CONTEXT_RADIUS_WORDS = 3
CHECKLIST = (
    "Review edition source and variants: RP2018 original Greek form, word position, and related textual witnesses independently.",
    "Verify each dictionary headword identity against independent Greek lexica. Shared numeric Strong references and identical headword spelling alone do not establish sense identity.",
    "Distinguish STEPBible's own dStrong sense-relationship metadata from independently established contextual meaning and polysemy/homonymy.",
    "Analyze Greek syntax and literary context before assigning a candidate to any individual Greek word position; do not infer meanings from English glosses.",
    "Review original RP2018 editor morphology against independent linguistic evidence, preserving any alternate original-source parsing.",
    "Record specific primary-source passages, independent lexicon bibliographies, reviewer qualifications and source-bound arguments for any proposed decision.",
    "Keep human scholarly signoff, owner English master-lexicon editorial decision, target-language work and publication as separate approval gates.",
)


def _load_frozen_triage(root: Path) -> dict[str, Any]:
    raw = (root / PREVIOUS_REPORT_PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PREVIOUS_REPORT_SHA256:
        raise SourceContractError("OLT-037B full Greek review queue has changed")
    report = json.loads(raw.decode("utf-8"))
    if (
        report.get("checkpoint") != "OLT-037B"
        or report.get("distinct_numeric_reference_review_cases") != 107
        or report.get("primary_positions_with_multiple_numeric_candidates") != 12539
        or report.get("rp2018_primary_word_positions") != 140149
        or report.get("original_editor_alternative_analyses") != 28
        or report.get("reviewed_cases") != 0
        or report.get("publication_status") != "BLOCKED"
    ):
        raise SourceContractError("OLT-037B scientific boundaries changed")
    return report


def _validate_context(word: dict[str, Any], verse: dict[str, Any],
                      ordinal: int) -> None:
    """Verify the token span refers to the ORIGINAL unicode verse string."""
    if _validate_original_word(word, verse["reference"], ordinal) < 1:
        raise SourceContractError("Invalid source numeric Strong")
    span = word["unicode_verse_character_span"]
    original = verse["original_accented_greek_verse"]
    if (
        not isinstance(span["start"], int) or
        not isinstance(span["end_exclusive"], int) or
        span["start"] < 0 or span["end_exclusive"] <= span["start"] or
        span["end_exclusive"] > len(original) or
        original[span["start"]:span["end_exclusive"]] !=
        word["accented_unicode_word_form"] or
        word["unicode_word_form_alignment"] != ALIGNMENT_STATUS
    ):
        raise SourceContractError("Source word span is not an exact Unicode-verse substring")


def _occurrence(book_id: str, verse: dict[str, Any],
                ordinal: int) -> dict[str, Any]:
    """Actual RP2018 punctuation and accents retained; word window is positional."""
    words = verse["words"]
    word = words[ordinal - 1]
    _validate_context(word, verse, ordinal)
    left = [w["accented_unicode_word_form"]
            for w in words[max(0, ordinal - 1 - CONTEXT_RADIUS_WORDS):ordinal-1]]
    right = [w["accented_unicode_word_form"]
             for w in words[ordinal:ordinal + CONTEXT_RADIUS_WORDS]]
    return {
        "book": book_id,
        "original_verse_reference": verse["reference"],
        "olt_derived_word_locator_NOT_PUBLISHER_NATIVE":
            word["derived_source_locator"],
        "source_word_ordinal": ordinal,
        "original_unicode_word": word["accented_unicode_word_form"],
        "original_bp5_beta_code_word": word["beta_code_word_form"],
        "original_rp2018_editor_morphology": word["official_editor_morphology_code"],
        "original_rp2018_alternative_analyses": word["additional_editor_analyses"],
        "unicode_source_character_span": word["unicode_verse_character_span"],
        "original_unicode_verse_NOT_ENGLISH_TRANSLATION":
            verse["original_accented_greek_verse"],
        "source_previous_three_words": left,
        "source_next_three_words": right,
        "selected_stepbible_sense": None,
        "selected_english_translation": None,
        "publication_status": "BLOCKED",
    }


def _sample_with_reasons(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Deterministic first/last-per-book and first-per-raw-morph/surface audit samples.

    This selection does NOT label senses or infer which dictionary record fits.
    Every observed raw morphology and exact Unicode surface has at least
    one example, plus first/last positions in every observed NT book.
    """
    if not observations:
        raise SourceContractError("No original source words found for requested dossier")
    reasons: dict[str, set[str]] = defaultdict(set)
    by_book: dict[str, list[dict[str, Any]]] = defaultdict(list)
    first_morph: dict[str, dict[str, Any]] = {}
    first_surface: dict[str, dict[str, Any]] = {}

    def add(word: dict[str, Any], reason: str) -> None:
        reasons[word["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"]].add(reason)

    for obs in observations:
        by_book[obs["book"]].append(obs)
        first_morph.setdefault(obs["original_rp2018_editor_morphology"], obs)
        first_surface.setdefault(obs["original_unicode_word"], obs)
    for book_words in by_book.values():
        add(book_words[0], "FIRST_OCCURRENCE_IN_BOOK_SOURCE_ORDER")
        add(book_words[-1], "LAST_OCCURRENCE_IN_BOOK_SOURCE_ORDER")
    for obs in first_morph.values():
        add(obs, "FIRST_OCCURRENCE_OF_ORIGINAL_EDITOR_MORPH_CODE")
    for obs in first_surface.values():
        add(obs, "FIRST_OCCURRENCE_OF_EXACT_UNICODE_SURFACE")
    result = []
    for obs in observations:
        key = obs["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"]
        if key in reasons:
            result.append({**obs, "sample_selection_reasons": sorted(reasons[key])})
    if not all(x["publication_status"] == "BLOCKED" and
               x["selected_stepbible_sense"] is None and
               x["selected_english_translation"] is None for x in result):
        raise SourceContractError("Sample contains an unapproved translation decision")
    return result


def build_context_dossiers(
    groups: dict[int, list[dict[str, Any]]],
    root: Path = ROOT,
    targets: tuple[int, ...] = CASE_NUMBERS,
) -> dict[str, Any]:
    """Fully hash-verified 27-book run; exactly match frozen OLT-037B case counts."""
    if targets != CASE_NUMBERS:
        raise SourceContractError("OLT-037C frozen case scope must not change silently")
    previous = _load_frozen_triage(root)
    previous_cases = {
        int(case["original_rp2018_strong_number"]): case
        for case in previous["cases"]
    }
    manifest = read_tbesg_manifest(root)
    rp = read_word_manifest(root)
    if (
        rp["upstream_commit"] != manifest["rp2018_source_commit"]
        or previous["stepbible_source_git_blob_sha1"] !=
        manifest["original_source_git_blob_sha1"]
        or previous["stepbible_pinned_source_commit"] != manifest["pinned_commit"]
    ):
        raise SourceContractError("Cross-check of original source editions failed")
    for target in targets:
        old = previous_cases.get(target)
        if old is None or len(groups.get(target, [])) <= 1:
            raise SourceContractError("Dossier target not a source-verified ambiguity")
        if [_source_candidate_brief(x) for x in groups[target]] != old["source_dstrong_candidates"]:
            raise SourceContractError("Native STEPBible evidence changed from frozen review queue")

    observed: dict[int, list[dict[str, Any]]] = {t: [] for t in targets}
    # All original word-positions are inspected by the already pinned
    # OLT-036 alignment contract; only actual selected Strong refs enter dossiers.
    total_source_positions = 0
    for book_meta in rp["files"]:
        book = read_aligned_greek_book(book_meta["upstream_book_code"], root)
        if book["publication_status"] != "BLOCKED":
            raise SourceContractError("Greek original edition unexpectedly publishable")
        for verse in book["aligned_verses"]:
            for ordinal, word in enumerate(verse["words"], 1):
                total_source_positions += 1
                raw = word["official_editor_strong_number"]
                if isinstance(raw, str) and raw.isascii() and raw.isdecimal() and int(raw) in observed:
                    _validate_original_word(word, verse["reference"], ordinal)
                    observed[int(raw)].append(_occurrence(book["book_id"], verse, ordinal))
    if total_source_positions != 140149:
        raise SourceContractError("Unexpected change in original NT Greek word inventory")

    dossiers = []
    for number in targets:
        records = observed[number]
        old = previous_cases[number]
        word_counts = Counter(x["book"] for x in records)
        morph_counts = Counter(x["original_rp2018_editor_morphology"] for x in records)
        surface_counts = Counter(x["original_unicode_word"] for x in records)
        if (len(records) != old["source_word_occurrence_count"] or
            dict(word_counts) != old["occurrence_counts_by_book"] or
            dict(morph_counts) != old["rp2018_editor_morphology_annotation_frequencies"] or
            len(surface_counts) != old["observed_rp2018_unicode_surface_form_count"]):
            raise SourceContractError("Full original Greek occurrences differ from pinned triage")
        for sample, original_sample in zip(records[:4], old["up_to_four_original_source_examples"]):
            if (sample["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"] !=
                original_sample["olt_derived_source_word_locator"] or
                sample["original_unicode_word"] != original_sample["source_accented_unicode_word"] or
                sample["original_bp5_beta_code_word"] != original_sample["source_beta_code_word"] or
                sample["original_rp2018_editor_morphology"] !=
                original_sample["rp2018_editor_morphology_code"]):
                raise SourceContractError("First original Greek case examples drifted")
        candidates = [_source_candidate_brief(row) for row in groups[number]]
        all_headwords = [row["greek_lemma_HEADWORD_CANDIDATE_ONLY"] for row in candidates]
        excerpts = _sample_with_reasons(records)
        if (len({x["original_rp2018_editor_morphology"] for x in excerpts}) != len(morph_counts)
            or len({x["original_unicode_word"] for x in excerpts}) != len(surface_counts)
            or {x["book"] for x in excerpts} != set(word_counts)):
            raise SourceContractError("Source sample missing morphology, surface or book coverage")
        dossiers.append({
            "case_id_from_frozen_olt_037b": old["case_id_OLT_DERIVED"],
            "rp2018_original_editor_strong_number": str(number),
            "primary_source_word_positions": len(records),
            "observed_original_greek_unicode_surface_count": len(surface_counts),
            "original_unicode_surface_frequencies": dict(sorted(surface_counts.items())),
            "original_raw_editor_morphology_code_frequencies": dict(sorted(morph_counts.items())),
            "original_source_occurrences_by_book": dict(sorted(word_counts.items())),
            "stepbible_dstrong_candidate_count": len(candidates),
            "source_lexicon_candidates_NOT_APPROVED": candidates,
            "literal_candidate_headwords_all_equal": len(set(all_headwords)) == 1,
            "literal_candidate_headword_count": len(set(all_headwords)),
            "stepbible_relationships_are_unreviewed_publisher_labels": True,
            "original_source_sampling_method":
                "FIRST_LAST_PER_BOOK_AND_FIRST_EACH_RAW_MORPH_AND_EXACT_UNICODE_SURFACE",
            "evidence_sample_count": len(excerpts),
            "all_raw_editor_morphology_codes_covered_by_examples": True,
            "all_exact_unicode_surface_forms_covered_by_examples": True,
            "sampled_original_greek_contexts_NO_SENSE_ASSIGNED": excerpts,
            "review_protocol_requirements": list(CHECKLIST),
            "philological_reviewer_identity": None,
            "review_date": None,
            "independent_lexicon_bibliography": [],
            "contextual_sense_assignments": [],
            "selected_stepbible_dstrong": None,
            "approved_greek_lemma": None,
            "approved_english_translation": None,
            "independent_philological_signoff": False,
            "owner_editorial_approval": False,
            "publication_status": "BLOCKED",
        })
    return {
        "checkpoint": CHECKPOINT,
        "review_state": "CONTEXTUAL_SOURCE_EVIDENCE_READY_HUMAN_REVIEW_NOT_STARTED",
        "rp2018_pinned_upstream_commit": rp["upstream_commit"],
        "stepbible_pinned_upstream_commit": manifest["pinned_commit"],
        "stepbible_original_git_blob_sha1": manifest["original_source_git_blob_sha1"],
        "olt_037b_frozen_review_queue_sha256": PREVIOUS_REPORT_SHA256,
        "stepbible_data_license": "CC BY 4.0",
        "stepbible_attribution": manifest["provenance_attribution"],
        "all_nt_original_greek_word_positions_inspected": total_source_positions,
        "cases": dossiers,
        "number_of_case_studies": len(dossiers),
        "number_of_verified_greek_lemma_decisions": 0,
        "number_of_approved_english_master_entries": 0,
        "number_of_generated_target_translations": 0,
        "all_original_morphologies_are_unreviewed_editor_claims": True,
        "no_english_gloss_treated_as_translation": True,
        "publication_status": "BLOCKED",
    }


def serialize_dossiers(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def verify_frozen_dossiers(result: dict[str, Any], root: Path = ROOT) -> None:
    path = root / REPORT_PATH
    if not path.is_file() or path.read_text(encoding="utf-8") != serialize_dossiers(result):
        raise SourceContractError("OLT-037C frozen contextual research dossiers missing or drifted")


def emit_source_checkpoint(result: dict[str, Any]) -> None:
    """Initial CI snapshot transfer only; post-freeze CI does exact regeneration."""
    raw = serialize_dossiers(result).encode("utf-8")
    encoded = base64.b64encode(raw).decode("ascii")
    print("OLT037C_CHECKPOINT_BEGIN")
    for idx in range(0, len(encoded), 4000):
        print("OLT037C_CHECKPOINT_PART " + encoded[idx:idx+4000])
    print("OLT037C_CHECKPOINT_END " + hashlib.sha256(raw).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser(description="Source Greek contexts only; no sense selection")
    parser.add_argument("--source", type=Path, required=True)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument("--summary", action="store_true")
    command.add_argument("--case", type=int, choices=CASE_NUMBERS)
    command.add_argument("--verify-checkpoint", action="store_true")
    command.add_argument("--emit-checkpoint-chunks", action="store_true")
    args = parser.parse_args()
    report = build_context_dossiers(read_tbesg(args.source))
    if args.verify_checkpoint:
        verify_frozen_dossiers(report)
        value = {"checkpoint": CHECKPOINT, "source_dossiers_regenerated_exactly": True,
                 "source_case_studies": len(report["cases"]),
                 "publication_status": "BLOCKED"}
    elif args.emit_checkpoint_chunks:
        emit_source_checkpoint(report)
        return 0
    elif args.case is not None:
        value = next(x for x in report["cases"]
                     if int(x["rp2018_original_editor_strong_number"]) == args.case)
    else:
        value = {k: v for k, v in report.items() if k != "cases"}
        value["cases"] = [
            {"original_numeric_strong": x["rp2018_original_editor_strong_number"],
             "source_occurrences": x["primary_source_word_positions"],
             "source_candidate_count": x["stepbible_dstrong_candidate_count"],
             "different_written_source_headwords": not x["literal_candidate_headwords_all_equal"],
             "observed_exact_unicode_surface_count":
                 x["observed_original_greek_unicode_surface_count"],
             "evidence_sample_count": x["evidence_sample_count"],
             "approved_greek_lemma": None,
             "publication_status": "BLOCKED"}
            for x in report["cases"]
        ]
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
