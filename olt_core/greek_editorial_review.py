"""OLT-037D unapproved human-review template generator/validator.

No API, CLI, CI, source dictionary, or owner metadata in this checkpoint can
approve a contextual Greek word sense or a translated Bible verse. Research
proposals and separate decisions are future checkpoints requiring actual
documented human action and supporting independent lexicographical sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .engine import SourceContractError
from .sources import ROOT
from .greek_independent_lsj import (
    REPORT_PATH as LSJ_REPORT_PATH,
    CONTEXT_SHA256,
)
from .greek_sense_dossier import REPORT_PATH as CONTEXT_REPORT_PATH

CHECKPOINT = "OLT-037D"
SOURCE_LSJ_SHA256 = "ea9f6e031897630cd5645ace24797e91e145f2018e5dba236b8951d5f1aa4973"
TEMPLATE_PATH = "data/research/olt_037d_independent_greek_review_templates.json"
SOURCE_REVIEW_REQUIREMENTS = [
    "Verify original Greek RP2018 edition word positions, accentuation, context and text-critical alternatives independently.",
    "Read Perseus LSJ source entries and corroborate dictionary lemma identity; matching LSJ key IDs alone is not semantic proof.",
    "Consult a separate scholarly Koine/New Testament lexicon; classical LSJ is not sufficient by itself for contextual New Testament senses.",
    "Distinguish lexicon headword spelling, morphological paradigm, lexical sense, contextual syntactic function and candidate English rendering as separate claims.",
    "Record independently citable bibliography, specific entry/page or stable locators and direct primary Greek usage evidence, including counterexamples and unresolved disagreements.",
    "Require explicit independent philological review with documented identity and date; repository CI can check only machine-readable presence and integrity, not scholarly correctness.",
    "Require separate owner-editor approval for every chosen English lexical equivalent and target-language output. No automated promotion from proposed or candidate glosses.",
]


def _load_verifiable_source(path: Path, expected_sha256: str) -> dict[str, Any]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise SourceContractError("Frozen independent Greek evidence source hash changed")
    return json.loads(raw.decode("utf-8"))


def make_review_templates(root: Path = ROOT) -> dict[str, Any]:
    original = _load_verifiable_source(root / CONTEXT_REPORT_PATH, CONTEXT_SHA256)
    independent = _load_verifiable_source(root / LSJ_REPORT_PATH, SOURCE_LSJ_SHA256)
    if (original["checkpoint"] != "OLT-037C" or
        original["number_of_verified_greek_lemma_decisions"] != 0 or
        original["publication_status"] != "BLOCKED" or
        independent["checkpoint"] != "OLT-037D" or
        independent["scholarly_decisions_approved"] != 0 or
        independent["publication_status"] != "BLOCKED"):
        raise SourceContractError("Previous lexical research was falsely approved")
    crossref = {x["original_rp2018_strong_number"]: x
                for x in independent["source_lexicon_candidate_key_research_cases"]}
    templates: list[dict[str, Any]] = []
    for case in original["cases"]:
        key = case["rp2018_original_editor_strong_number"]
        candidate = crossref.get(key)
        if not candidate or candidate["publication_status"] != "BLOCKED":
            raise SourceContractError("Independent Greek lexicon research subject not found")
        templates.append({
            "original_rp2018_editor_numeric_reference": key,
            "olt_derived_037b_case_id": case["case_id_from_frozen_olt_037b"],
            "original_greek_source_context_dossier_sha256": CONTEXT_SHA256,
            "perseus_lsj_entry_keys_source_evidence_sha256": SOURCE_LSJ_SHA256,
            "external_lexicon_lsj_source_evidence_status":
                candidate["source_lsj_entry_lookup_status"],
            "native_lsj_entry_keys_unreviewed": [
                x["source_tei_entry_key_UNREVIEWED"]
                for x in candidate["exact_lsj_entry_key_matches_NO_OWNERSHIP_OR_MEANING_INFERRED"]
            ],
            "native_lsj_entry_ids_unreviewed": [
                x["source_tei_entry_id"]
                for x in candidate["exact_lsj_entry_key_matches_NO_OWNERSHIP_OR_MEANING_INFERRED"]
            ],
            "original_occurrence_count": case["primary_source_word_positions"],
            "research_state": "UNSTARTED_UNREVIEWED",
            "original_verse_word_locator_selected_FOR_REVIEW": None,
            "proposed_dictionary_lemma": None,
            "proposed_lexical_sense": None,
            "proposed_english_gloss_NOT_OLT_TRANSLATION": None,
            "independently_quoted_or_cited_lexicon_sources": [],
            "additional_koine_lexicon_sources_checked": [],
            "primary_greek_context_argument": None,
            "alternative_hypotheses_or_counterevidence": [],
            "morphology_cross_review": None,
            "independent_reviewer_identifier": None,
            "independent_reviewer_date": None,
            "independent_philological_signoff": False,
            "owner_editorial_approval": False,
            "target_language_translation_generated": False,
            "publication_status": "BLOCKED",
        })
    if [x["original_rp2018_editor_numeric_reference"] for x in templates] != ["3004","3754"]:
        raise SourceContractError("Unexpected OLT-037D review-target ordering")
    return {
        "checkpoint": CHECKPOINT,
        "schema_purpose": "BLANK_HUMAN_REVIEW_TEMPLATES_NOT_PUBLISHED_LEXICAL_DECISIONS",
        "original_rp2018_dossier_sha256": CONTEXT_SHA256,
        "independent_lsj_source_evidence_sha256": SOURCE_LSJ_SHA256,
        "independent_lsj_license": "CC BY-SA 4.0",
        "stepbible_data_license": "CC BY 4.0",
        "research_requirements": SOURCE_REVIEW_REQUIREMENTS,
        "review_case_templates": templates,
        "expert_reviews_performed": 0,
        "owner_approved_english_master_entries": 0,
        "automatic_lexical_sense_decisions": 0,
        "publication_status": "BLOCKED",
    }


def serialize_templates(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def validate_unreviewed_draft(data: dict[str, Any]) -> None:
    """Fail closed on approvals/claims, even if someone edits the JSON by hand."""
    if (data.get("checkpoint") != CHECKPOINT or
        data.get("schema_purpose") !=
            "BLANK_HUMAN_REVIEW_TEMPLATES_NOT_PUBLISHED_LEXICAL_DECISIONS" or
        data.get("expert_reviews_performed") != 0 or
        data.get("owner_approved_english_master_entries") != 0 or
        data.get("automatic_lexical_sense_decisions") != 0 or
        data.get("publication_status") != "BLOCKED"):
        raise SourceContractError("OLT-037D source-only review template incorrectly approved")
    cases = data.get("review_case_templates")
    if not isinstance(cases, list) or len(cases) != 2:
        raise SourceContractError("Both original Greek review subjects required")
    for case in cases:
        if (case.get("research_state") != "UNSTARTED_UNREVIEWED" or
            case.get("publication_status") != "BLOCKED" or
            case.get("original_verse_word_locator_selected_FOR_REVIEW") is not None or
            case.get("proposed_dictionary_lemma") is not None or
            case.get("proposed_lexical_sense") is not None or
            case.get("proposed_english_gloss_NOT_OLT_TRANSLATION") is not None or
            case.get("independently_quoted_or_cited_lexicon_sources") != [] or
            case.get("additional_koine_lexicon_sources_checked") != [] or
            case.get("primary_greek_context_argument") is not None or
            case.get("alternative_hypotheses_or_counterevidence") != [] or
            case.get("morphology_cross_review") is not None or
            case.get("independent_reviewer_identifier") is not None or
            case.get("independent_reviewer_date") is not None or
            case.get("independent_philological_signoff") is not False or
            case.get("owner_editorial_approval") is not False or
            case.get("target_language_translation_generated") is not False):
            raise SourceContractError("Fake human scholarly or owner approval in unreviewed template")


def verify_frozen_templates(root: Path = ROOT) -> dict[str, Any]:
    generated = make_review_templates(root)
    validate_unreviewed_draft(generated)
    path = root / TEMPLATE_PATH
    if not path.is_file() or path.read_text(encoding="utf-8") != serialize_templates(generated):
        raise SourceContractError("Frozen independent Greek human-review template differs")
    validate_unreviewed_draft(json.loads(path.read_text(encoding="utf-8")))
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="OLT-037D blank human research protocol only")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        result = verify_frozen_templates()
        print(json.dumps({"checkpoint": CHECKPOINT,
                          "blank_review_templates_reproduced_exactly": True,
                          "case_count": len(result["review_case_templates"]),
                          "publication_status": "BLOCKED"}, indent=2))
    else:
        result = make_review_templates()
        validate_unreviewed_draft(result)
        print(serialize_templates(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
