"""OLT-037D: Perseus LSJ independent source *entry key* inventory, not sense assignment.

The original LSJ TEI P4 uses a DTD. Never expand external entities,
execute XML transforms, access unpinned resources or substitute LSJ for the
specialized Koine philological research needed for a literal NT translation.
Read ONLY source entryFree opening-tag metadata. An exact search-key match
establishes existence of a lexicon key; it does NOT establish Greek lexical
identity, its occurrence in a Biblical verse, or contextual English meaning.

Source: Perseus Digital Library / LSJ, CC BY-SA 4.0.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .engine import SourceContractError
from .sources import ROOT
from .greek_sense_dossier import (
    REPORT_PATH as CONTEXT_REPORT_PATH,
    CASE_NUMBERS,
)
from scripts.fetch_olt_037d_lsj import (
    read_lsj_source_manifest, verify_original_lsj,
)

CHECKPOINT = "OLT-037D"
REPORT_PATH = "data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json"
CONTEXT_SHA256 = "08d58d6ce13b9803ed1936dfde1ed249f3c32e44af7bdc50b8665adb593bab69"
# Search strings are LITERAL hypotheses in the original TEI key notation.
# They are not automatic Unicode->Beta Code conversions and cannot be used as
# already-corroborated lemma equivalence claims.
RESEARCH_QUERIES = {
    "3004": {"unicode_step_source_candidate_headword": "λέγω",
             "lsj_source_entry_key_query": "le/gw"},
    "3754": {"unicode_step_source_candidate_headword": "ὅτι",
             "lsj_source_entry_key_query": "o(/ti"},
}
_START_TAG = re.compile(r"<entryFree\b(?P<attrs>[^>]{0,4096})>", re.DOTALL)
_ATTR = re.compile(r'(?P<name>id|key)="(?P<value>[^"]+)"')
_SHARD_HEADING = re.compile(r'<div0\s+[^>]*?n="(?P<letter>[^"]+)"', re.DOTALL)


def _frozen_context_dossiers(root: Path) -> dict[str, Any]:
    raw = (root / CONTEXT_REPORT_PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != CONTEXT_SHA256:
        raise SourceContractError("OLT-037C original Greek research dossiers hash changed")
    evidence = json.loads(raw.decode("utf-8"))
    if (evidence.get("checkpoint") != "OLT-037C"
        or evidence.get("all_nt_original_greek_word_positions_inspected") != 140149
        or evidence.get("number_of_case_studies") != 2
        or evidence.get("number_of_verified_greek_lemma_decisions") != 0
        or evidence.get("number_of_approved_english_master_entries") != 0
        or evidence.get("publication_status") != "BLOCKED"):
        raise SourceContractError("Frozen contextual Greek evidence no longer unreviewed")
    if ([case["rp2018_original_editor_strong_number"] for case in evidence["cases"]]
        != list(RESEARCH_QUERIES.keys())):
        raise SourceContractError("Frozen Greek dossier subjects changed")
    return evidence


def source_entry_key_index(source_text: str) -> list[dict[str, str]]:
    """Do not parse DTD, definitions, semantic sense markup, or external entities."""
    if not source_text or "<TEI.2>" not in source_text or "<entryFree" not in source_text:
        raise SourceContractError("Missing original TEI LSJ lexicon source structure")
    results: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    openings = source_text.count("<entryFree")
    for match in _START_TAG.finditer(source_text):
        attrs = {m.group("name"): m.group("value")
                 for m in _ATTR.finditer(match.group("attrs"))}
        source_id = attrs.get("id")
        source_key = attrs.get("key")
        if not source_id or not source_key or source_id in seen_ids:
            raise SourceContractError("Malformed or duplicate original LSJ entry id/key")
        if len(source_key) > 240 or len(source_id) > 150:
            raise SourceContractError("Unexpectedly long original Perseus entry key")
        seen_ids.add(source_id)
        results.append({"source_tei_entry_id": source_id,
                        "source_tei_entry_key_UNREVIEWED": source_key})
    if len(results) != openings or len(results) < 100:
        raise SourceContractError("LSJ source dictionary entries are missing or truncated")
    return results


def _entry_key_candidates(rows: list[dict[str, str]], query: str) -> list[dict[str, str]]:
    """Exact literal match or same key with source digit suffix, no fuzzy join."""
    expected = re.compile(r"^" + re.escape(query) + r"[0-9]*$")
    return [r for r in rows if expected.fullmatch(r["source_tei_entry_key_UNREVIEWED"])]


def build_independent_key_inventory(
    source_dir: Path, root: Path = ROOT
) -> dict[str, Any]:
    primary = _frozen_context_dossiers(root)
    manifest = read_lsj_source_manifest(root)
    cases = []
    for spec in manifest["file_specs"]:
        strong = spec["research_editor_strong"]
        query = RESEARCH_QUERIES[strong]
        matching_dossier = next(
            x for x in primary["cases"]
            if x["rp2018_original_editor_strong_number"] == strong
        )
        candidates = matching_dossier["source_lexicon_candidates_NOT_APPROVED"]
        if (not matching_dossier["literal_candidate_headwords_all_equal"]
            or len(candidates) != 2
            or not all(x["greek_lemma_HEADWORD_CANDIDATE_ONLY"] ==
                       query["unicode_step_source_candidate_headword"] for x in candidates)
            or matching_dossier["approved_greek_lemma"] is not None
            or matching_dossier["approved_english_translation"] is not None
            or matching_dossier["independent_philological_signoff"]):
            raise SourceContractError("Original source headword or scientific signoff drifted")
        blob = (source_dir / spec["filename"]).read_bytes()
        verify_original_lsj(blob, spec)
        txt = blob.decode("utf-8", errors="strict")
        index = source_entry_key_index(txt)
        header_match = _SHARD_HEADING.search(txt)
        heading = header_match.group("letter") if header_match else None
        found = _entry_key_candidates(index, query["lsj_source_entry_key_query"])
        if len({x["source_tei_entry_id"] for x in found}) != len(found):
            raise SourceContractError("Duplicate independent dictionary candidate")
        cases.append({
            "case_id_from_frozen_rp2018_contexts": matching_dossier[
                "case_id_from_frozen_olt_037b"],
            "original_rp2018_strong_number": strong,
            "source_rp2018_occurrences": matching_dossier["primary_source_word_positions"],
            "stepbible_dstrong_ids_UNREVIEWED":
                [x["native_step_dstrong"] for x in candidates],
            "source_stepbible_greek_headword_UNREVIEWED":
                query["unicode_step_source_candidate_headword"],
            "source_lsj_key_query_IS_HYPOTHESIS": query["lsj_source_entry_key_query"],
            "source_lsj_original_shard_path": spec["upstream_path"],
            "source_lsj_original_git_blob_sha1": spec["original_git_blob_sha1"],
            "source_lsj_original_size_bytes": spec["original_byte_length"],
            "lsj_shard_original_div0_letter": heading,
            "number_of_original_lsj_entryFree_start_tags_indexed": len(index),
            "exact_lsj_entry_key_matches_NO_OWNERSHIP_OR_MEANING_INFERRED": found,
            "source_lsj_entry_lookup_status": (
                "EXACT_LITERAL_KEY_EXISTS_NOT_APPROVED"
                if found else "NO_EXACT_SOURCE_KEY_NOT_AUTOFILLED"),
            "greek_orthography_equivalence_independently_proven": False,
            "dictionary_lemma_identity_approved": False,
            "nt_word_sense_assignment": None,
            "independent_philologist_corroboration": None,
            "owner_translation_approval": None,
            "english_master_entry": None,
            "publication_status": "BLOCKED",
        })
    return {
        "checkpoint": CHECKPOINT,
        "research_scope": "INDEPENDENT_CLASSICAL_GREEK_LEXICON_SOURCE_KEYS_ONLY",
        "original_textual_source": "Robinson-Pierpont 2018 pinned OLT-037C Greek contexts",
        "frozen_greek_context_sha256": CONTEXT_SHA256,
        "source_lsj_repo": manifest["upstream_repository"],
        "source_lsj_commit": manifest["upstream_pinned_commit"],
        "license": manifest["source_data_license"],
        "attribution": manifest["attribution"],
        "source_shards_verified_with_original_git_blob_sha1": len(cases),
        "source_lexicon_candidate_key_research_cases": cases,
        "entry_keys_are_raw_source_strings_not_confirmed_koine_lemmas": True,
        "greek_lemma_sense_independent_review": "NOT_DONE",
        "reviewer_identity": None,
        "scholarly_decisions_approved": 0,
        "english_master_entries_approved": 0,
        "greek_to_target_language_verse_translations_approved": 0,
        "publication_status": "BLOCKED",
    }


def serialize_inventory(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def verify_checkpoint(report: dict[str, Any], root: Path = ROOT) -> None:
    path = root / REPORT_PATH
    if not path.is_file() or path.read_text(encoding="utf-8") != serialize_inventory(report):
        raise SourceContractError("OLT-037D independent Greek lexicon key checkpoint absent or drifted")


def emit_checkpoint(report: dict[str, Any]) -> None:
    raw = serialize_inventory(report).encode("utf-8")
    print("OLT037D_CHECKPOINT_BEGIN")
    b64 = base64.b64encode(raw).decode("ascii")
    for i in range(0, len(b64), 4000):
        print("OLT037D_CHECKPOINT_PART " + b64[i:i+4000])
    print("OLT037D_CHECKPOINT_END " + hashlib.sha256(raw).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser(description="Perseus LSJ entry key evidence only, not translation")
    parser.add_argument("--source-dir", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--emit-checkpoint", action="store_true")
    mode.add_argument("--verify-checkpoint", action="store_true")
    args = parser.parse_args()
    report = build_independent_key_inventory(args.source_dir)
    if args.emit_checkpoint:
        emit_checkpoint(report)
    elif args.verify_checkpoint:
        verify_checkpoint(report)
        print(json.dumps({"checkpoint": CHECKPOINT,
                          "original_lsj_source_checkpoint_exactly_reproduced": True,
                          "publication_status": "BLOCKED"}, indent=2))
    else:
        print(serialize_inventory(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
