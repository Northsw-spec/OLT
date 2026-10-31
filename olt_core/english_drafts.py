"""CHES-002: deterministic, UNAPPROVED English draft preview from pinned OLT research.

No third-party CHES text is read or published here. The original-language
OSHB token source is hash-verified by olt_core.sources. A separate private
CHES chapter can currently be associated by VERSE only, not by word.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

from .sources import ROOT, load_ot_book, read_provenance

RESEARCH_PATH = Path("data/research/genesis_01_complete_research_alignment.json")
WAYYIQTOL_MORPH = re.compile(r"(?:^|/)V[a-z]w[123]")
# This is a deliberately SMALL, source-tested Genesis 1 editorial pilot.
# It is not a general English tense detector or automatic lexicon approval.
GENESIS_ONE_SIMPLE_PAST_FRAGMENTS = frozenset({
    "and he said", "and was", "and he saw", "and he separated",
    "and he called", "and he made", "and she brought forth",
    "and he set", "and he shaped", "and he blessed",
})


class EnglishDraftContractError(ValueError):
    """Source evidence, owner tense policy or publication boundary mismatch."""


def verified_wayyiqtol(original_morphology: str) -> bool:
    if not isinstance(original_morphology, str):
        raise EnglishDraftContractError("Original morphology missing")
    return bool(WAYYIQTOL_MORPH.search(original_morphology))


def validate_research_token(original: dict[str, Any],
                            proposal: dict[str, Any],
                            verse_id: str, ordinal: int) -> bool:
    """Exact research token ↔ pinned source word identity; never guess alignment."""
    expected = {
        "source_ordinal": ordinal,
        "source_token_id": original.get("source_id"),
        "original_hebrew": original.get("hebrew"),
        "original_morphology": original.get("morph_raw"),
        "original_lemma": original.get("lemma_raw"),
    }
    for field, value in expected.items():
        if proposal.get(field) != value:
            raise EnglishDraftContractError(
                f"{verse_id}: source token {ordinal} identity mismatch: {field}")
    if proposal.get("english_approved") is not False:
        raise EnglishDraftContractError("Research-only English fragment incorrectly approved")
    wayyiqtol = verified_wayyiqtol(original.get("morph_raw"))
    if proposal.get("source_wayyiqtol") is not wayyiqtol:
        raise EnglishDraftContractError(
            f"{verse_id}: wrong wayyiqtol classification at source token {ordinal}")
    fragment = proposal.get("english_fragment_research_only")
    if not isinstance(fragment, str):
        raise EnglishDraftContractError("Missing English research fragment")
    if wayyiqtol and fragment.lower().strip() not in GENESIS_ONE_SIMPLE_PAST_FRAGMENTS:
        raise EnglishDraftContractError(
            f"{verse_id}: wayyiqtol must use vetted simple-past research fragment")
    return wayyiqtol


def build_genesis_one_drafts(root: Path = ROOT) -> dict[str, Any]:
    """Generate 31 unapproved verse drafts, with every research source token checked."""
    registry = read_provenance(root)
    original_book = load_ot_book("Gen", root, registry)
    source = {v["reference"]: v for v in original_book["verses"]
              if re.fullmatch(r"Gen\.1\.[1-9][0-9]*", v["reference"])}
    research = json.loads((root / RESEARCH_PATH).read_text(encoding="utf-8"))
    proposals = research.get("genesis_1_research_verses")
    if not isinstance(proposals, list) or len(proposals) != 31 or len(source) != 31:
        raise EnglishDraftContractError("Genesis 1 needs exactly 31 pinned source and research verses")
    if (research.get("authoritatively_approved_english_verses") != 0 or
        research.get("publication_status") != "BLOCKED"):
        raise EnglishDraftContractError("Research must not assert approved or published Scripture")

    output: list[dict[str, Any]] = []
    original_count = 0
    wayyiqtol_count = 0
    for number, entry in enumerate(proposals, 1):
        verse_id = f"Gen.1.{number}"
        if entry.get("reference") != verse_id:
            raise EnglishDraftContractError("Research order/verse changed")
        original_verse = source.get(verse_id)
        if original_verse is None:
            raise EnglishDraftContractError("No pinned original-language source verse")
        words = original_verse.get("words")
        alignment = entry.get("original_token_alignment")
        if (not isinstance(words, list) or not isinstance(alignment, list) or
            len(words) != len(alignment) or len(words) != entry.get("source_token_count")):
            raise EnglishDraftContractError(f"{verse_id}: original token count differs")
        ids: list[str] = []
        morph_forms: list[dict[str, Any]] = []
        for ordinal, (word, proposal) in enumerate(zip(words, alignment), 1):
            if word.get("ordinal") != ordinal or word.get("reference") != verse_id:
                raise EnglishDraftContractError("Original source ordinal changed")
            is_wayyiqtol = validate_research_token(word, proposal, verse_id, ordinal)
            ids.append(word["source_id"])
            if is_wayyiqtol:
                morph_forms.append({
                    "source_token_id": word["source_id"],
                    "original_morphology": word["morph_raw"],
                    "english_fragment_simple_past_research": proposal["english_fragment_research_only"],
                    "tense_review_status": "MATCHES_CURATED_PILOT_NOT_PHILOLOGICALLY_APPROVED",
                })
        if len(ids) != len(set(ids)) or len(morph_forms) != entry.get("source_wayyiqtol_count"):
            raise EnglishDraftContractError(f"{verse_id}: duplicate IDs or wayyiqtol count mismatch")
        text = entry.get("proposed_english_research_text")
        if not isinstance(text, str) or not text.strip():
            raise EnglishDraftContractError(f"{verse_id}: no existing unapproved English proposal")
        original_count += len(words)
        wayyiqtol_count += len(morph_forms)
        output.append({
            "reference": verse_id,
            "english_text_unapproved": text,
            "original_source_word_token_ids": ids,
            "original_word_count": len(ids),
            "verified_source_wayyiqtol_simple_past_fragment_checks": morph_forms,
            "english_status": "UNREVIEWED_ENGLISH_DRAFT",
            "ches_word_level_mapping": "NOT_DONE",
            "lexical_and_scholarly_signoff": "NOT_DONE",
            "publication_status": "BLOCKED",
        })
    if original_count != 434 or wayyiqtol_count != 50:
        raise EnglishDraftContractError("Frozen Genesis 1 token or wayyiqtol totals changed")
    return {
        "checkpoint": "CHES-002",
        "english_target": "en",
        "english_source": "EXISTING_OLT_GENESIS_RESEARCH_NOT_COPIED_CHES",
        "original_language_source": "PINNED_OSHB_WLC",
        "original_word_count_verified": original_count,
        "original_verse_count_verified": len(output),
        "wayyiqtol_simple_past_token_fragment_checks": wayyiqtol_count,
        "ches_pdf_verse_correspondence": "SEPARATE_PRIVATE_QA_REQUIRED",
        "ches_word_level_correspondence": "NOT_DONE",
        "english_translation_owner_approved": False,
        "complete_english_bible_owner_approved": False,
        "publication_status": "BLOCKED",
        "verses": output,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review-only original-source-linked English Genesis 1 draft")
    parser.add_argument("--verse", default="Gen.1.1", help="One Genesis 1 verse, or 'all'")
    args = parser.parse_args()
    result = build_genesis_one_drafts()
    if args.verse != "all":
        result["verses"] = [v for v in result["verses"] if v["reference"] == args.verse]
        if not result["verses"]:
            parser.error("Only Gen.1.1 ... Gen.1.31 are supported")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
