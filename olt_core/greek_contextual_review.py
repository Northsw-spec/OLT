"""OLT-037G: ten original-Greek context-specific scientific research worksheets.

CRITICAL: "hypothesis" labels are QUESTIONS, not conclusions, semantic
predictions, machine translations, or expert review. All evidence comes from
hash-pinned OLT-037F original RP2018 Greek and Greek dictionary source packet,
not from guessed or reconstituted verses. Source text and lexical candidate
lists cannot vote or auto-approve Greek senses or target-language translation.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from .engine import SourceContractError
from .greek_lexical_comparison import REPORT_PATH as FROZEN_F_SOURCE
from .sources import ROOT

CHECKPOINT = "OLT-037G"
REPORT_PATH = "data/research/olt_037g_original_greek_context_review_worksheets.json"
F_SOURCE_SHA256 = "0dca8643adb191e437c7801d7e363450ed07ffbe31138d3bf0090460ca0eba2c"
CASES = ("3004", "3754")

# Question types are explicitly tied to the kind of original editor source
# morphology, but are NOT independent syntactic conclusions.
SYNTAX_RESEARCH_QUESTIONS = {
    "3004": [
        {
            "research_hypothesis_id": "G3004-PREDICATION-SPEECH",
            "candidate_interpretation_AS_QUESTION_ONLY":
                "Could this original occurrence introduce or report spoken discourse? "
                "Test clause boundaries, complement structure, and subject reference.",
            "status": "UNTESTED_NOT_ASSERTED",
        },
        {
            "research_hypothesis_id": "G3004-NAMING-DESIGNATION",
            "candidate_interpretation_AS_QUESTION_ONLY":
                "Could this original occurrence instead introduce a name or designation? "
                "Test construction, appositions, and opposing Greek usage evidence.",
            "status": "UNTESTED_NOT_ASSERTED",
        },
    ],
    "3754": [
        {
            "research_hypothesis_id": "G3754-CLAUSE-CONTENT",
            "candidate_interpretation_AS_QUESTION_ONLY":
                "Could the original conjunction introduce a content/complement clause? "
                "Inspect its governing verb, following clause, and syntactic dependencies.",
            "status": "UNTESTED_NOT_ASSERTED",
        },
        {
            "research_hypothesis_id": "G3754-CAUSAL-EXPLANATION",
            "candidate_interpretation_AS_QUESTION_ONLY":
                "Could the original conjunction instead introduce a causal explanation? "
                "Test the relation to the preceding clause and competing textual readings.",
            "status": "UNTESTED_NOT_ASSERTED",
        },
    ],
}
REVIEW_GATE_QUESTIONS = (
    "What is the source Greek reading and punctuation in this RP2018 original witness, and what alternative ancient textual witnesses need independent comparison?",
    "Is the original publisher's morphology analysis independently justified by inflection, agreement, tense/aspect and nearby syntax? What are alternative parsings?",
    "Which clause contains the focal word? What is its syntactic attachment, scope, referent and discourse function?",
    "Which of the listed hypotheses is supported, refuted or undetermined by this specific Greek sentence? What falsifying counterexamples or contrary readings must be considered?",
    "What are the exact native source IDs, short source glosses and cited primary examples in Abbott-Smith, LSJ and STEPBible? Are these lexica dependent on earlier lexica?",
    "What distinct Koine attestations, modern peer-reviewed philology or critical Greek editions support or contradict the contextual proposal?",
    "Has a qualified human philologist independently signed a specific citation- and source-bound conclusion, with unresolved alternatives recorded?",
    "Has the owner separately approved the English master lexical equivalent and any future target-language translation?",
)


def _read_unchanged_source(root: Path) -> dict[str, Any]:
    raw = (root / FROZEN_F_SOURCE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != F_SOURCE_SHA256:
        raise SourceContractError("OLT-037F original Greek and lexical evidence SHA-256 changed")
    old = json.loads(raw.decode("utf-8"))
    if (old.get("checkpoint") != "OLT-037F"
        or old.get("number_of_comparison_dossiers") != 2
        or old.get("number_of_original_greek_verse_word_examples") != 10
        or old.get("lsj_original_entry_structures_verified_against_pinned_git_blobs") != 3
        or old.get("human_philological_approvals") != 0
        or old.get("owner_english_master_approvals") != 0
        or old.get("translated_scripture_verses_published") != 0
        or old.get("publication_status") != "BLOCKED"):
        raise SourceContractError("Previous original Greek research or approval boundaries drifted")
    if [x["original_rp2018_editor_strong_number"] for x in old["dossiers"]] != list(CASES):
        raise SourceContractError("Previous original Greek research case order changed")
    return old


def _assert_original_greek_span(example: dict[str, Any]) -> None:
    original = example["original_greek_verse_UNALTERED"]
    span = example["original_source_unicode_word_character_span"]
    word = example["exact_original_greek_word_UNALTERED"]
    if (not isinstance(original, str)
        or not isinstance(word, str)
        or not isinstance(span.get("start"), int)
        or not isinstance(span.get("end_exclusive"), int)
        or span["start"] < 0
        or span["end_exclusive"] > len(original)
        or span["start"] >= span["end_exclusive"]
        or original[span["start"]:span["end_exclusive"]] != word
        or example.get("source_context_hypothesis_reviewed") is not False
        or example.get("selected_independent_lexicon_entry") is not None
        or example.get("selected_original_source_lexical_sense") is not None
        or example.get("owner_english_lexical_equivalent") is not None
        or example.get("publication_status") != "BLOCKED"):
        raise SourceContractError("Original Greek verse or original unreviewed context altered")


def _source_citation_references(dossier: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = [
        {
            "source": "Abbott-Smith (1922) Greek New Testament lexicon",
            "original_source_type": "PUBLIC_DOMAIN_AS_STATED_IN_HASH_PINNED_PROJECT_README",
            "native_tei_entry_attribute_n":
                dossier["abbott_smith_original_entry_native_n_NOT_OLT_LEMMA"],
            "source_document_checkpoint_sha256": F_SOURCE_SHA256,
            "dictionary_headword_and_glosses_are_NOT_VERIFIED_GREEK_SENSES": True,
        },
    ]
    entries = dossier["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]
    for original in entries:
        if (original["source_entry_consultation_status"] !=
                "UNREVIEWED_SOURCE_STRUCTURE_AND_SHORT_GLOSS"
            or original["publication_status"] != "BLOCKED"
            or original["selected_contextual_sense"] is not None):
            raise SourceContractError("Original independent LSJ entry falsely approved")
        out.append({
            "source": "Perseus Digital Library LSJ Greek-English lexicon",
            "original_source_type": "CC BY-SA 4.0 ATTRIBUTION REQUIRED",
            "source_tei_entry_id": original["source_original_lsj_tei_entry_id"],
            "source_tei_entry_key": original["source_original_lsj_tei_entry_key"],
            "source_original_entry_body_sha256":
                original["original_lsj_entry_body_sha256_NOT_ENG_LITERARY_CERTIFICATION"],
            "source_document_checkpoint_sha256": F_SOURCE_SHA256,
            "lexicon_original_entry_body_is_NOT_HUMAN_REVIEWED": True,
        })
    return out


def _comparison_witness(examples: list[dict[str, Any]], idx: int) -> dict[str, Any]:
    """A primary-source comparison passage, NOT evidence of a counterexample."""
    own = examples[idx]
    possible = next(
        (x for n, x in enumerate(examples) if n != idx
         and x["original_raw_rp2018_editor_morphology_CODE_NOT_INDEPENDENTLY_VERIFIED"] !=
             own["original_raw_rp2018_editor_morphology_CODE_NOT_INDEPENDENTLY_VERIFIED"]),
        None,
    )
    if possible is None:
        possible = examples[(idx + 1) % len(examples)]
    _assert_original_greek_span(possible)
    return {
        "original_greek_reference": possible["original_greek_reference"],
        "olt_derived_greek_word_locator_NOT_NATIVE_ID":
            possible["olt_derived_greek_word_locator_NOT_NATIVE_ID"],
        "comparison_reason":
            "DIFFERENT_ORIGINAL_EDITOR_MORPHOLOGY_CODE" if
            possible["original_raw_rp2018_editor_morphology_CODE_NOT_INDEPENDENTLY_VERIFIED"] !=
            own["original_raw_rp2018_editor_morphology_CODE_NOT_INDEPENDENTLY_VERIFIED"]
            else "SECOND_DISTINCT_ORIGINAL_CONTEXT",
        "is_this_a_verified_counterexample": False,
        "source_counterevidence_review": "NOT_STARTED",
    }


def _worksheet(dossier: dict[str, Any], example: dict[str, Any],
               all_examples: list[dict[str, Any]], index: int) -> dict[str, Any]:
    number = dossier["original_rp2018_editor_strong_number"]
    _assert_original_greek_span(example)
    span = example["original_source_unicode_word_character_span"]
    locator = example["olt_derived_greek_word_locator_NOT_NATIVE_ID"]
    if not isinstance(locator, str) or len(locator) < 10 or not locator.startswith("rp2018-v3.3.2:"):
        raise SourceContractError("Original OLT-derived Greek word locator malformed")
    raw_morph = example["original_raw_rp2018_editor_morphology_CODE_NOT_INDEPENDENTLY_VERIFIED"]
    if not isinstance(raw_morph, str) or not raw_morph:
        raise SourceContractError("Original editor morphology is not present")
    questions = SYNTAX_RESEARCH_QUESTIONS[number]
    return {
        "research_id_OLT_DERIVED": f"OLT-037G-{number}-W{index+1:02d}",
        "original_rp2018_editor_numeric_strong_reference": number,
        "source_original_greek_reference": example["original_greek_reference"],
        "source_original_unicode_greek_verse_UNCHANGED": example["original_greek_verse_UNALTERED"],
        "source_original_unicode_focus_word_UNCHANGED": example["exact_original_greek_word_UNALTERED"],
        "source_original_unicode_character_span": span,
        "source_original_word_ordinal": example["original_word_ordinal_in_verse"],
        "olt_derived_greek_source_word_locator_NOT_NATIVE":
            locator,
        "original_publisher_morphology_code_NOT_CERTIFIED": raw_morph,
        "morphology_review_hypothesis_QUESTION_ONLY":
            ("Is original publisher morphology code '" + raw_morph +
             "' supported by this Greek inflection and clause? "
             "What independent parse or grammatical counterarguments exist?"),
        "two_competing_syntactic_hypotheses_NOT_ASSERTED":
            [{**question, "human_written_supporting_greek_analysis": None,
              "human_written_refuting_greek_analysis": None,
              "verdict": "UNEXAMINED"} for question in questions],
        "original_other_context_FOR_POSSIBLE_COMPARISON_NOT_COUNTERPROOF":
            _comparison_witness(all_examples, index),
        "original_source_lexicon_candidate_glosses_FOR_REVIEW_NOT_TRANSLATION": [
            {"source": "Abbott-Smith (1922) original TEI public domain",
             "original_source_tag": d["original_source_tag"],
             "original_source_gloss_ORIGINAL_ONLY": d["original_source_text"],
             "this_gloss_assigned_to_this_verse": False}
            for d in dossier["abbott_smith_original_source_def_or_gloss_NOT_OLT_TRANSLATION"]
        ],
        "source_perseus_lsj_original_tei_entries_UNSELECTED": [
            {"original_entry_id": d["source_original_lsj_tei_entry_id"],
             "original_entry_key": d["source_original_lsj_tei_entry_key"],
             "original_cc_by_sa_short_excerpt_SOURCE_ONLY":
                d["first_short_lsj_source_tr_excerpt_CC_BY_SA_NOT_OLT"],
             "this_dictionary_entry_assigned_to_this_verse": False}
            for d in dossier["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]
        ],
        "exact_citable_source_entry_references_NOT_ARGUMENTS":
            _source_citation_references(dossier),
        "original_greek_primary_source_locator_FOR_CITATION": locator,
        "source_greek_editor_strong_is_not_semantic_proof": True,
        "english_dictionary_gloss_is_not_olt_translation": True,
        "independent_greek_syntax_examination": None,
        "genuine_comparative_original_greek_counterevidence": [],
        "alternative_textual_variant_sources_verified": [],
        "human_primary_source_and_lexicon_bibliography": [],
        "philological_analyst_identity": None,
        "philological_analyst_review_date": None,
        "independent_philological_signoff": False,
        "owner_editorial_decision_date": None,
        "owner_english_translation_approval": False,
        "approved_contextual_greek_sense": None,
        "approved_english_master_translation": None,
        "approved_target_language_output": None,
        "review_state": "QUESTIONS_DRAFTED_EVIDENCE_NOT_YET_INTERPRETED",
        "publication_status": "BLOCKED",
    }


def generate_worksheets(root: Path = ROOT) -> dict[str, Any]:
    source = _read_unchanged_source(root)
    result = []
    for dossier in source["dossiers"]:
        number = dossier["original_rp2018_editor_strong_number"]
        contexts = dossier["original_source_context_examples_NOT_INTERPRETED"]
        if (number not in CASES or len(contexts) != 5
            or dossier["independent_philological_signoff"] is not False
            or dossier["owner_english_master_approval"] is not False
            or dossier["approved_english_word_or_phrase"] is not None
            or dossier["expert_approved_contextual_word_senses"] != []
            or dossier["publication_status"] != "BLOCKED"):
            raise SourceContractError("Expected five still-unapproved original Greek contexts per case")
        worksheets = [_worksheet(dossier, item, contexts, i)
                      for i, item in enumerate(contexts)]
        if len({x["olt_derived_greek_source_word_locator_NOT_NATIVE"] for x in worksheets}) != 5:
            raise SourceContractError("Original source Greek words not uniquely located")
        result.append({
            "research_group_original_editor_strong_reference": number,
            "source_original_group_word_occurrence_count":
                dossier["total_original_rp2018_word_occurrences"],
            "source_original_lsj_entry_count":
                len(dossier["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]),
            "native_dstrong_lexicon_source_candidate_ids_UNSELECTED":
                dossier["stepbible_dstrong_candidates_ORIGINAL_EDITOR_EVIDENCE"],
            "context_specific_worksheets": worksheets,
            "group_level_lexical_sense_decisions": [],
            "human_philologist_signoff": False,
            "owner_editorial_signoff": False,
            "publication_status": "BLOCKED",
        })
    generated = {
        "checkpoint": CHECKPOINT,
        "scope": "ORIGINAL_GREEK_QUESTIONS_AND_ALTERNATIVE_HYPOTHESES_UNREVIEWED",
        "source_olt037f_frozen_sha256": F_SOURCE_SHA256,
        "source_rp2018_original_greek_verses_from_verified_olt037f": True,
        "original_abbott_smith_source_1922_public_domain_AS_VERIFIED": True,
        "original_perseus_lsj_source_license": "CC BY-SA 4.0",
        "original_stepbible_source_license": "CC BY 4.0",
        "review_requirements": list(REVIEW_GATE_QUESTIONS),
        "source_case_groups": result,
        "source_group_count": len(result),
        "source_greek_word_context_worksheet_count": sum(
            len(x["context_specific_worksheets"]) for x in result),
        "independently_reviewed_or_approved_greek_senses": 0,
        "owner_approved_english_master_lexicon_entries": 0,
        "approved_target_language_verses": 0,
        "publication_status": "BLOCKED",
    }
    validate_unreviewed_worksheets(generated)
    return generated


def validate_unreviewed_worksheets(data: dict[str, Any]) -> None:
    """Strictly enforce this checkpoint cannot become a falsified approval."""
    if (data.get("checkpoint") != CHECKPOINT
        or data.get("scope") != "ORIGINAL_GREEK_QUESTIONS_AND_ALTERNATIVE_HYPOTHESES_UNREVIEWED"
        or data.get("source_olt037f_frozen_sha256") != F_SOURCE_SHA256
        or data.get("source_group_count") != 2
        or data.get("source_greek_word_context_worksheet_count") != 10
        or data.get("independently_reviewed_or_approved_greek_senses") != 0
        or data.get("owner_approved_english_master_lexicon_entries") != 0
        or data.get("approved_target_language_verses") != 0
        or data.get("publication_status") != "BLOCKED"):
        raise SourceContractError("Unreviewed OLT-037G scope/approval gate has been falsified")
    groups = data.get("source_case_groups")
    if (not isinstance(groups, list) or
        [x.get("research_group_original_editor_strong_reference") for x in groups]
        != list(CASES)):
        raise SourceContractError("Missing or unexpected original Greek source research group")
    seen: set[str] = set()
    for group in groups:
        if (group.get("group_level_lexical_sense_decisions") != []
            or group.get("human_philologist_signoff") is not False
            or group.get("owner_editorial_signoff") is not False
            or group.get("publication_status") != "BLOCKED"
            or not isinstance(group.get("context_specific_worksheets"), list)
            or len(group["context_specific_worksheets"]) != 5):
            raise SourceContractError("Original lexical group is falsely approved or truncated")
        for card in group["context_specific_worksheets"]:
            key = card.get("olt_derived_greek_source_word_locator_NOT_NATIVE")
            verse = card.get("source_original_unicode_greek_verse_UNCHANGED")
            span = card.get("source_original_unicode_character_span")
            if (key in seen or not isinstance(key, str) or
                not isinstance(verse, str) or not isinstance(span, dict) or
                not isinstance(span.get("start"), int) or
                not isinstance(span.get("end_exclusive"), int) or
                verse[span["start"]:span["end_exclusive"]] !=
                    card.get("source_original_unicode_focus_word_UNCHANGED") or
                card.get("independent_philological_signoff") is not False or
                card.get("owner_english_translation_approval") is not False or
                card.get("approved_contextual_greek_sense") is not None or
                card.get("approved_english_master_translation") is not None or
                card.get("approved_target_language_output") is not None or
                card.get("independent_greek_syntax_examination") is not None or
                card.get("genuine_comparative_original_greek_counterevidence") != [] or
                card.get("alternative_textual_variant_sources_verified") != [] or
                card.get("human_primary_source_and_lexicon_bibliography") != [] or
                card.get("philological_analyst_identity") is not None or
                card.get("philological_analyst_review_date") is not None or
                card.get("owner_editorial_decision_date") is not None or
                card.get("review_state") !=
                    "QUESTIONS_DRAFTED_EVIDENCE_NOT_YET_INTERPRETED" or
                card.get("publication_status") != "BLOCKED" or
                card.get("source_greek_editor_strong_is_not_semantic_proof") is not True or
                card.get("english_dictionary_gloss_is_not_olt_translation") is not True):
                raise SourceContractError("A false source, counterevidence, expert or English approval was inserted")
            seen.add(key)
            hypotheses = card.get("two_competing_syntactic_hypotheses_NOT_ASSERTED")
            if (not isinstance(hypotheses, list) or len(hypotheses) != 2 or
                {x.get("research_hypothesis_id") for x in hypotheses} !=
                {x["research_hypothesis_id"] for x in
                 SYNTAX_RESEARCH_QUESTIONS[group["research_group_original_editor_strong_reference"]]} or
                any(x.get("status") != "UNTESTED_NOT_ASSERTED"
                    or x.get("verdict") != "UNEXAMINED"
                    or x.get("human_written_supporting_greek_analysis") is not None
                    or x.get("human_written_refuting_greek_analysis") is not None
                    for x in hypotheses)):
                raise SourceContractError("Grammar hypotheses forged or adjudicated without review")
            comparison = card.get("original_other_context_FOR_POSSIBLE_COMPARISON_NOT_COUNTERPROOF")
            if (not isinstance(comparison, dict) or
                comparison.get("is_this_a_verified_counterexample") is not False or
                comparison.get("source_counterevidence_review") != "NOT_STARTED"):
                raise SourceContractError("Unreviewed Greek comparison labeled proven counterexample")
            if any(item.get("this_gloss_assigned_to_this_verse") is not False
                   for item in card.get("original_source_lexicon_candidate_glosses_FOR_REVIEW_NOT_TRANSLATION", [])):
                raise SourceContractError("Dictionary gloss auto-applied to source verse")
            if any(item.get("this_dictionary_entry_assigned_to_this_verse") is not False
                   for item in card.get("source_perseus_lsj_original_tei_entries_UNSELECTED", [])):
                raise SourceContractError("LSJ lemma auto-applied to source verse")
    if len(seen) != 10:
        raise SourceContractError("Original Greek passage research duplicates a word")


def serialize_worksheets(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def verify_frozen_worksheets(root: Path = ROOT) -> dict[str, Any]:
    report = generate_worksheets(root)
    file = root / REPORT_PATH
    if not file.is_file() or file.read_text(encoding="utf-8") != serialize_worksheets(report):
        raise SourceContractError("OLT-037G original Greek research worksheets absent or altered")
    validate_unreviewed_worksheets(json.loads(file.read_text(encoding="utf-8")))
    return report


def emit_initial_checkpoint(data: dict[str, Any]) -> None:
    raw = serialize_worksheets(data).encode("utf-8")
    b64 = base64.b64encode(raw).decode("ascii")
    print("OLT037G_CHECKPOINT_BEGIN")
    for start in range(0, len(b64), 4000):
        print("OLT037G_CHECKPOINT_PART " + b64[start:start+4000])
    print("OLT037G_CHECKPOINT_END " + hashlib.sha256(raw).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser(description="Greek lexical source review worksheets, no approvals")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--summary", action="store_true")
    mode.add_argument("--case", choices=CASES)
    mode.add_argument("--emit-initial-checkpoint", action="store_true")
    mode.add_argument("--verify-checkpoint", action="store_true")
    args = parser.parse_args()
    report = generate_worksheets()
    if args.emit_initial_checkpoint:
        emit_initial_checkpoint(report)
    elif args.verify_checkpoint:
        verify_frozen_worksheets()
        print(json.dumps({"checkpoint": CHECKPOINT,
            "exact_original_greek_research_worksheets_reproduced": True,
            "case_count": report["source_group_count"],
            "original_greek_contexts": report["source_greek_word_context_worksheet_count"],
            "publication_status": "BLOCKED"}, indent=2))
    elif args.case:
        group = next(x for x in report["source_case_groups"]
                     if x["research_group_original_editor_strong_reference"] == args.case)
        print(json.dumps(group, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(json.dumps({"checkpoint": CHECKPOINT,
            "source_context_worksheets": report["source_greek_word_context_worksheet_count"],
            "original_strong_research_cases": [
                {"original_numeric_reference":
                    g["research_group_original_editor_strong_reference"],
                 "source_greek_word_occurences":
                    g["source_original_group_word_occurrence_count"],
                 "worksheet_count": len(g["context_specific_worksheets"])}
                for g in report["source_case_groups"]],
            "independent_philological_approvals": 0,
            "owner_english_master_approvals": 0,
            "publication_status": "BLOCKED"}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
