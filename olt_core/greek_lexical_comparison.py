"""OLT-037F: source-cited Greek contextual lexical COMPARISON, not translation.

Three original witnesses kept distinct: RP2018 Greek NT original verse text;
Abbott-Smith 1922 NT Greek lexicon (PD asserted by pinned upstream README);
Perseus LSJ original TEI lexicon (CC BY-SA 4.0). STEPBible dStrong remains
a fourth source of editorial candidate IDs (CC BY 4.0). Source labels and
brief excerpt tags are not approvals of lemma, contextual sense or English
translation. No external XML entity processing or unpinned source retrieval.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
import re
from typing import Any

from .engine import SourceContractError
from .sources import ROOT
from .greek_sense_dossier import REPORT_PATH as CONTEXT_REPORT_PATH
from .greek_koine_crosscheck import REPORT_PATH as CROSSCHECK_REPORT_PATH
from scripts.fetch_olt_037d_lsj import read_lsj_source_manifest, verify_original_lsj

CHECKPOINT = "OLT-037F"
REPORT_PATH = "data/quality/olt_037f_source_cited_greek_lexical_comparison.json"
CONTEXT_SHA256 = "08d58d6ce13b9803ed1936dfde1ed249f3c32e44af7bdc50b8665adb593bab69"
CROSSCHECK_SHA256 = "f6e0c31f4a7c736df307e55c10d0860ea47edf7aa6dc2c28b61d6b81430ee435"
TARGETS = ("3004", "3754")
NATIVE_LSJ_ENTRIES = {
    "3004": (("n62204", "le/gw1"), ("n62205", "le/gw2")),
    "3754": (("n75695", "o(/ti^"),),
}
LSJ_OPEN = re.compile(r"<entryFree\b[^>]{0,4096}>", re.DOTALL)
ATTR_ID = re.compile(r'\bid="([^"]+)"')
ATTR_KEY = re.compile(r'\bkey="([^"]+)"')
SENSE_OPEN = re.compile(r"<sense\b([^>]{0,2000})>", re.DOTALL)
TAG_OPEN = {tag: re.compile(r"<" + tag + r"\b", re.DOTALL) for tag in ("tr","bibl","ref","orth")}
TR_CONTENT = re.compile(r"<tr(?:\s[^>]{0,300})?>(.*?)</tr>", re.DOTALL)
TAG_REMOVER = re.compile(r"<[^>]+>", re.DOTALL)
MAX_LSJ_EXCERPT_CHARS = 32


def _verified_json(root: Path, path: str, original_sha: str, checkpoint: str) -> dict[str, Any]:
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != original_sha:
        raise SourceContractError("Original pinned Greek source checkpoint changed: " + path)
    report = json.loads(raw.decode("utf-8"))
    if report.get("checkpoint") != checkpoint or report.get("publication_status") != "BLOCKED":
        raise SourceContractError("Previous original Greek source checkpoint falsely approved")
    return report


def extract_pinned_lsj_entries(xml: bytes, required: tuple[tuple[str, str], ...]) -> list[dict[str, Any]]:
    """Scan ONLY exact native TEI entryFree boundaries; no DTD parser or meaning inference.

    Source SHA/size are verified by the caller before invoking. Keep original
    entry IDs, keys, source text fragment hashes, structural tag counts and at
    most ONE very short original tr excerpt per entry under CC BY-SA attribution.
    """
    data = xml.decode("utf-8", errors="strict")
    matches: dict[str, list[dict[str, Any]]] = {source_id: [] for source_id, _ in required}
    for opening in LSJ_OPEN.finditer(data):
        tag = opening.group()
        idmatch = ATTR_ID.search(tag)
        if idmatch is None or idmatch.group(1) not in matches:
            continue
        keymatch = ATTR_KEY.search(tag)
        if keymatch is None:
            raise SourceContractError("Referenced original LSJ entry has no key")
        next_start = LSJ_OPEN.search(data, opening.end())
        close = data.find("</entryFree>", opening.end())
        if close < 0 or (next_start is not None and next_start.start() < close):
            raise SourceContractError("Pinned LSJ TEI entry boundary inconsistent")
        body = data[opening.end():close]
        if not body or len(body) > 350000:
            raise SourceContractError("Original LSJ entry text suspiciously empty or oversized")
        source_senses = SENSE_OPEN.findall(body)
        native_numbers = []
        for attrs in source_senses:
            num = re.search(r'\bn="([^"]{1,80})"', attrs)
            if num:
                native_numbers.append(num.group(1))
        # Translational phrases in LSJ are quotes from original independent
        # dictionary source and do NOT supply an OLT English rendering.
        snippets = []
        for match in TR_CONTENT.finditer(body):
            source_text = html.unescape(TAG_REMOVER.sub("", match.group(1))).strip()
            source_text = " ".join(source_text.split())
            if source_text:
                snippets.append(source_text[:MAX_LSJ_EXCERPT_CHARS])
                break
        matches[idmatch.group(1)].append({
            "source_original_lsj_tei_entry_id": idmatch.group(1),
            "source_original_lsj_tei_entry_key": keymatch.group(1),
            "original_lsj_entry_body_sha256_NOT_ENG_LITERARY_CERTIFICATION":
                hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "original_lsj_entry_body_unicode_char_length": len(body),
            "source_sense_opening_tag_count": len(source_senses),
            "source_sense_n_labels_FIRST_12_NOT_SEMANTIC_APPROVAL": native_numbers[:12],
            "source_original_tr_tag_count": len(TAG_OPEN["tr"].findall(body)),
            "source_original_bibl_tag_count": len(TAG_OPEN["bibl"].findall(body)),
            "source_original_ref_tag_count": len(TAG_OPEN["ref"].findall(body)),
            "source_original_orth_tag_count": len(TAG_OPEN["orth"].findall(body)),
            "first_short_lsj_source_tr_excerpt_CC_BY_SA_NOT_OLT": snippets,
            "source_entry_consultation_status": "UNREVIEWED_SOURCE_STRUCTURE_AND_SHORT_GLOSS",
            "selected_contextual_sense": None,
            "publication_status": "BLOCKED",
        })
    output = []
    for source_id, key in required:
        found = matches[source_id]
        if len(found) != 1 or found[0]["source_original_lsj_tei_entry_key"] != key:
            raise SourceContractError("Required pinned independent LSJ entry id/key absent or ambiguous")
        output.append(found[0])
    return output


def _source_passage_example(raw: dict[str, Any]) -> dict[str, Any]:
    """Reuse exact original-word Unicode source span and source-derived locator."""
    text = raw["original_unicode_verse_NOT_ENGLISH_TRANSLATION"]
    span = raw["unicode_source_character_span"]
    word = raw["original_unicode_word"]
    if (not isinstance(span["start"], int)
        or not isinstance(span["end_exclusive"], int)
        or text[span["start"]:span["end_exclusive"]] != word
        or raw["selected_stepbible_sense"] is not None
        or raw["selected_english_translation"] is not None
        or raw["publication_status"] != "BLOCKED"):
        raise SourceContractError("Source Greek word evidence changed or falsely approved")
    return {
        "original_greek_reference": raw["original_verse_reference"],
        "original_greek_verse_UNALTERED": text,
        "exact_original_greek_word_UNALTERED": word,
        "original_raw_rp2018_editor_morphology_CODE_NOT_INDEPENDENTLY_VERIFIED":
            raw["original_rp2018_editor_morphology"],
        "original_word_ordinal_in_verse": raw["source_word_ordinal"],
        "olt_derived_greek_word_locator_NOT_NATIVE_ID":
            raw["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"],
        "original_source_unicode_word_character_span": span,
        "earlier_source_sample_selection_reasons": raw["sample_selection_reasons"],
        "source_context_hypothesis_reviewed": False,
        "selected_independent_lexicon_entry": None,
        "selected_original_source_lexical_sense": None,
        "owner_english_lexical_equivalent": None,
        "publication_status": "BLOCKED",
    }


def pick_source_examples(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Five deterministic ORIGINAL verse examples; no guessed context meanings."""
    if len(contexts) < 5:
        raise SourceContractError("Insufficient original Greek source contexts")
    first = contexts[0]
    candidates = [first]
    # Deliberate variation by original editor parsing and source book rather
    # than false automated "say", "call", "that", "because" labels.
    priorities = (
        lambda x: x["book"] != first["book"],
        lambda x: x["original_rp2018_editor_morphology"] != first["original_rp2018_editor_morphology"],
        lambda x: x["original_unicode_word"] != first["original_unicode_word"],
        lambda x: x["book"] not in {y["book"] for y in candidates},
    )
    seen = {first["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"]}
    for predicate in priorities:
        match = next((x for x in contexts if
            x["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"] not in seen
            and predicate(x)), None)
        if match is not None:
            seen.add(match["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"])
            candidates.append(match)
    for x in contexts:
        if len(candidates) >= 5:
            break
        if x["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"] not in seen:
            candidates.append(x)
            seen.add(x["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"])
    if len(candidates) != 5:
        raise SourceContractError("Insufficient distinct original-source examples")
    return [_source_passage_example(x) for x in candidates]


def build_comparison_dossiers(lsj_source_dir: Path, root: Path = ROOT) -> dict[str, Any]:
    source = _verified_json(root, CONTEXT_REPORT_PATH, CONTEXT_SHA256, "OLT-037C")
    previous = _verified_json(root, CROSSCHECK_REPORT_PATH, CROSSCHECK_SHA256, "OLT-037E")
    if (source.get("number_of_verified_greek_lemma_decisions") != 0
        or source.get("number_of_case_studies") != 2
        or previous.get("machine_approved_lexical_senses") != 0
        or previous.get("human_approved_lexical_senses") != 0
        or previous.get("approved_english_master_entries") != 0
        or previous.get("source_abbott_license_status") != "PUBLIC_DOMAIN_AS_STATED_BY_UPSTREAM_PROJECT"):
        raise SourceContractError("Original-source evidence has fabricated semantic approvals")
    lsj_manifest = read_lsj_source_manifest(root)
    if (previous["source_lsj_pinned_commit"] != lsj_manifest["upstream_pinned_commit"]
        or previous["frozen_rp2018_greek_context_snapshot_sha256"] != CONTEXT_SHA256
        or previous["source_lsj_license"] != "CC BY-SA 4.0"):
        raise SourceContractError("Original Greek or source licensing provenance changed")
    original = {x["rp2018_original_editor_strong_number"]: x for x in source["cases"]}
    prev = {x["rp2018_original_strong_number"]: x for x in previous["source_cases"]}
    if set(original) != set(TARGETS) or set(prev) != set(TARGETS):
        raise SourceContractError("Original research group scope changed")
    dossiers = []
    for spec in lsj_manifest["file_specs"]:
        target = spec["research_editor_strong"]
        xml = (lsj_source_dir / spec["filename"]).read_bytes()
        verify_original_lsj(xml, spec)
        comparison = prev[target]
        original_case = original[target]
        key_records = comparison["lsj_original_source_key_diagnostic"]
        requested = NATIVE_LSJ_ENTRIES[target]
        expected_keys = {t[0]:t[1] for t in requested}
        frozen_candidates = (
            key_records["exact_original_source_key_matches_UNREVIEWED"] if target=="3004"
            else key_records["lossy_signature_source_key_records_DIAGNOSTIC_ONLY"]
        )
        if {(x["source_tei_entry_id"],x["source_tei_entry_key_UNREVIEWED"])
             for x in frozen_candidates} != set(requested):
            raise SourceContractError("Original prior LSJ native entries changed")
        if (comparison["original_rp2018_source_word_occurrences"] !=
            original_case["primary_source_word_positions"]
            or comparison["selected_lsj_entry_id"] is not None
            or comparison["selected_abbott_lexical_sense"] is not None
            or comparison["owner_editorial_approval"]):
            raise SourceContractError("Unexpected original Greek source count/lexical approval")
        entries = extract_pinned_lsj_entries(xml, requested)
        abbott_entries = comparison["abbott_smith_original_source_lexical_entries_UNREVIEWED"]
        if len(abbott_entries) != 1:
            raise SourceContractError("Expected one original Abbott lexicon source record")
        native_abbott = abbott_entries[0]
        if (native_abbott["biblical_contextual_sense_selected"] is not None or
            native_abbott["abbott_dictionary_gloss_used_as_translation"] or
            native_abbott["publication_status"] != "BLOCKED"):
            raise SourceContractError("Abbott original lexical evidence auto-approved")
        passage_examples = pick_source_examples(
            original_case["sampled_original_greek_contexts_NO_SENSE_ASSIGNED"])
        dossiers.append({
            "case_id_OLT_DERIVED": original_case["case_id_from_frozen_olt_037b"],
            "original_rp2018_editor_strong_number": target,
            "total_original_rp2018_word_occurrences": original_case["primary_source_word_positions"],
            "source_original_unicode_surface_count":
                original_case["observed_original_greek_unicode_surface_count"],
            "original_source_context_examples_NOT_INTERPRETED": passage_examples,
            "stepbible_dstrong_candidates_ORIGINAL_EDITOR_EVIDENCE":
                comparison["stepbible_native_source_candidate_ids_UNREVIEWED"],
            "abbott_smith_original_entry_native_n_NOT_OLT_LEMMA":
                native_abbott["native_abbott_entry_attribute_n_SOURCE_ONLY"],
            "abbott_smith_original_source_orth_NOT_APPROVED":
                native_abbott["first_source_orth_forms_NOT_APPROVED"],
            "abbott_smith_original_source_def_or_gloss_NOT_OLT_TRANSLATION":
                native_abbott["first_source_def_or_gloss_records_NOT_OLT_TRANSLATION"],
            "abbott_smith_original_strong_references_NOT_UNIQUE_LEXEME_KEYS":
                native_abbott["all_native_abbott_strong_crossrefs_SOURCE_ONLY"],
            "perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA":
                entries,
            "cross_lexicon_same_english_gloss_is_not_independent_agreement": True,
            "lsj_key_digit_suffix_is_NOT_stepbible_dstrong_suffix": True,
            "different_original_rp2018_editor_morphologies_never_auto_assign_senses": True,
            "review_questions_NOT_YET_ANSWERED": [
                "What is the exact textual and morphological reading at each cited original word locator?",
                "Which source dictionary sense definitions, if any, are independently justified by this original Greek syntax and literary context?",
                "Do the source lexica depend on each other for these meanings, and which independent Koine attestations support or challenge the hypothesis?",
                "Which alternative lexical meanings or text-critical readings remain plausible, and what primary Greek evidence rules them out?",
                "Has a qualified human reviewer signed an exact-source rationale, and has the owner separately approved any English translation?"
            ],
            "independently_verified_contextual_greek_lemma": None,
            "expert_approved_contextual_word_senses": [],
            "independent_koine_lexicon_critical_analysis_by_human": None,
            "source_lsj_and_abbott_independent_votes_count": None,
            "human_reviewer_identity": None,
            "human_reviewer_date": None,
            "independent_philological_signoff": False,
            "owner_english_master_approval": False,
            "approved_english_word_or_phrase": None,
            "target_language_verse_approved": False,
            "publication_status": "BLOCKED",
        })
    if [d["original_rp2018_editor_strong_number"] for d in dossiers] != list(TARGETS):
        raise SourceContractError("Original-source study file mapping changed")
    if any(len(x["original_source_context_examples_NOT_INTERPRETED"]) != 5
           or x["independent_philological_signoff"] for x in dossiers):
        raise SourceContractError("Unreviewed Greek research dossier count or signoff changed")
    return {
        "checkpoint": CHECKPOINT,
        "purpose": "ORIGINAL_GREEK_CONTEXT_VS_SOURCE_DICTIONARY_ENTRY_COMPARISON_NO_SEMANTIC_DECISIONS",
        "source_rp2018_olt037c_sha256": CONTEXT_SHA256,
        "source_abbott_olt037e_sha256": CROSSCHECK_SHA256,
        "source_abbott_public_domain_AS_ASSERTED_BY_UPSTREAM": True,
        "source_lsj_license": "CC BY-SA 4.0",
        "source_lsj_attribution": lsj_manifest["attribution"],
        "source_lsj_pinned_commit": lsj_manifest["upstream_pinned_commit"],
        "source_stepbible_license": "CC BY 4.0",
        "original_greek_word_sample_source_is_olt037c": True,
        "lsj_original_entry_structures_verified_against_pinned_git_blobs": 3,
        "number_of_comparison_dossiers": len(dossiers),
        "number_of_original_greek_verse_word_examples": 10,
        "dossiers": dossiers,
        "human_philological_approvals": 0,
        "owner_english_master_approvals": 0,
        "translated_scripture_verses_published": 0,
        "publication_status": "BLOCKED",
    }


def serialize_research(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def verify_frozen_source_dossiers(data: dict[str, Any], root: Path = ROOT) -> None:
    path = root / REPORT_PATH
    if not path.is_file() or path.read_text(encoding="utf-8") != serialize_research(data):
        raise SourceContractError("OLT-037F original source lexical comparison is absent or altered")


def emit_initial_checkpoint(data: dict[str, Any]) -> None:
    payload = serialize_research(data).encode("utf-8")
    content = base64.b64encode(payload).decode("ascii")
    print("OLT037F_CHECKPOINT_BEGIN")
    for i in range(0, len(content), 4000):
        print("OLT037F_CHECKPOINT_PART " + content[i:i+4000])
    print("OLT037F_CHECKPOINT_END " + hashlib.sha256(payload).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser(description="Original Greek lexical source comparison, no signoff")
    parser.add_argument("--lsj-dir", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--emit-initial-checkpoint", action="store_true")
    mode.add_argument("--verify-checkpoint", action="store_true")
    args = parser.parse_args()
    report = build_comparison_dossiers(args.lsj_dir)
    if args.emit_initial_checkpoint:
        emit_initial_checkpoint(report)
        return 0
    if args.verify_checkpoint:
        verify_frozen_source_dossiers(report)
        print(json.dumps({"checkpoint": CHECKPOINT,
            "source_greek_lexical_comparison_reproduced_exactly": True,
            "publication_status": "BLOCKED"}, indent=2))
        return 0
    # Summary avoids full copyright-sensitive source snippets in Actions.
    print(json.dumps({
        "checkpoint": CHECKPOINT,
        "original_source_cases": [
            {"original_editor_strong": x["original_rp2018_editor_strong_number"],
             "original_word_occurrences": x["total_original_rp2018_word_occurrences"],
             "original_source_verse_samples":
                 len(x["original_source_context_examples_NOT_INTERPRETED"]),
             "lsj_native_ids": [y["source_original_lsj_tei_entry_id"] for y in
                                x["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]]
            } for x in report["dossiers"]],
        "human_philological_approvals": 0,
        "publication_status": "BLOCKED"
    }, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
