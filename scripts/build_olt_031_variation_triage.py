#!/usr/bin/env python3
"""OLT-031: deterministic ORIGINAL SOURCE-ID variant triage; NOT semantic approval.

All English fragments are already-unapproved OLT-016 proposals. Multiple
fragments are a research question, never automatic Hebrew homonym evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITORIAL = ROOT / "data/research/genesis_01_lexeme_editorial_queue.json"
WAVE_A = ROOT / "data/research/olt_017a_scholarly_wave.json"
WAVE_B = ROOT / "data/research/olt_017b_scholarly_lexemes.json"
OUTPUT = ROOT / "data/research/olt_031_lemma_variation_triage.json"
OWNER_LOCKS = {"1254 a": "shape", "6213 a": "make", "7549": "firmament"}


def build(editorial: dict, wave_a: dict, wave_b: dict) -> dict:
    if (
        editorial.get("source_lemma_ids") != 97
        or editorial.get("source_word_tokens") != 434
        or len(editorial.get("entries", [])) != 97
        or editorial.get("lemma_ids_with_multiple_english_fragments") != 42
        or editorial.get("owner_locked_families") != 3
        or editorial.get("new_english_families_pending") != 94
        or editorial.get("approved_homonym_links") != 0
        or editorial.get("english_verse_approval") is not False
        or editorial.get("publication_status") != "BLOCKED"
    ):
        raise ValueError("OLT-016 lexical source coverage or publication firewall changed")

    for source in (wave_a, wave_b):
        if source.get("publication_status") != "BLOCKED" or source.get("approved_homonym_links") != 0:
            raise ValueError("Prior scholarly dossier falsely approved release or homonym identity")
    if wave_a.get("new_english_family_approvals") != 0 or wave_b.get("new_approved_english_families") != 0:
        raise ValueError("Prior dossier silently approved English families")

    previous: dict[str, list[str]] = {}
    for item in wave_a.get("cases", []):
        previous.setdefault(item["source_lemma"], []).append(item["id"])
    for item in wave_b.get("cases", []):
        previous.setdefault(item["exact_lemma"], []).append(item["question_id"])

    seen_lemmas: set[str] = set()
    seen_tokens: set[str] = set()
    owners_found: dict[str, str] = {}
    cases: list[dict] = []
    for row in editorial["entries"]:
        lemma = row["source_lemma_id"]
        if not isinstance(lemma, str) or not lemma or lemma in seen_lemmas:
            raise ValueError("Duplicate or empty exact original source lemma ID")
        seen_lemmas.add(lemma)
        words = row["source_words"]
        if len(words) != row["source_token_count"] or not words:
            raise ValueError("Original source-token count differs")
        for word in words:
            if not all(isinstance(word.get(field), str) for field in (
                "token_id", "reference", "hebrew", "raw_morphology", "english_research_fragment"
            )):
                raise ValueError("Incomplete original Hebrew source trace")
            if not all(word[k] for k in ("token_id", "reference", "hebrew", "raw_morphology")):
                raise ValueError("Missing original Hebrew source identifier")
            if word["token_id"] in seen_tokens:
                raise ValueError("Duplicate original Hebrew source token")
            seen_tokens.add(word["token_id"])
        fragments = row["proposed_english_fragments"]
        if not isinstance(fragments, list) or not fragments or any(not isinstance(x, str) for x in fragments):
            raise ValueError("Unusable English research fragment inventory")
        if len(fragments) != len(set(fragments)):
            raise ValueError("Duplicate variants in one source-lemma inventory")
        if set(fragments) != {w["english_research_fragment"] for w in words}:
            raise ValueError("English research fragments differ from source tokens")
        owner = row.get("owner_english_family")
        if owner is not None:
            if OWNER_LOCKS.get(lemma) != owner or row.get("english_family_approval") != "OWNER_FAMILY_ONLY":
                raise ValueError("Owner-locked Hebrew lexical family changed")
            owners_found[lemma] = owner
        elif row.get("english_family_approval") != "REQUIRES_EDITORIAL_REVIEW":
            raise ValueError("An unapproved English word family was silently approved")
        if row.get("homonym_identity_approved") is not False or (
            row.get("homonym_slot", {}).get("placement") != "BELOW_ENGLISH_WORD"
            or row.get("homonym_slot", {}).get("approved_alternatives") != []
        ):
            raise ValueError("Unreviewed homonym was promoted or vertically linked incorrectly")
        if row.get("source_morphology_independent_review") is not False:
            raise ValueError("OSHB morphological tags are not independent scholarly review")
        if len(fragments) <= 1:
            continue
        cases.append({
            "source_lemma_id": lemma,
            "source_token_count": len(words),
            "research_fragments_exact": fragments,
            "distinct_imported_morphology_tags": sorted({w["raw_morphology"] for w in words}),
            "owner_locked_english_family": owner,
            "source_bdb_ids": row["bdb_ids"],
            "source_strongs_ids": row["strong_ids"],
            "earlier_research_case_ids": sorted(previous.get(lemma, [])),
            "original_source_contexts": [
                {
                    "source_token_id": word["token_id"],
                    "verse": word["reference"],
                    "pointed_hebrew": word["hebrew"],
                    "imported_morphology": word["raw_morphology"],
                    "unapproved_english_fragment": word["english_research_fragment"],
                }
                for word in words
            ],
            "english_variation_cause": "NOT_INDEPENDENTLY_DETERMINED",
            "hebrew_homonym_identity": "NOT_VERIFIED",
            "editorial_status": "REVIEW_REQUIRED",
        })
    if len(seen_tokens) != 427 or owners_found != OWNER_LOCKS or len(cases) != 42:
        raise ValueError("Genesis 1 source component or owner-lock coverage changed")
    cases.sort(key=lambda c: (
        -len(c["research_fragments_exact"]), -c["source_token_count"], c["source_lemma_id"]
    ))
    return {
        "checkpoint": "OLT-031",
        "scope": "GENESIS_1_MULTIPLE_ENGLISH_RESEARCH_FRAGMENT_TRIAGE",
        "canonical_source": "data/research/genesis_01_lexeme_editorial_queue.json",
        "original_hebrew_verse_count": 31,
        "original_hebrew_word_tokens": 434,
        "source_tokens_with_numeric_lemma": len(seen_tokens),
        "source_tokens_without_numeric_lemma": 7,
        "exact_source_lemma_ids": 97,
        "source_lemmas_with_multiple_unapproved_fragments": 42,
        "source_lemmas_with_one_unapproved_fragment": 55,
        "owner_locked_lemma_families": 3,
        "new_english_lexical_approvals": 0,
        "new_independent_morphology_approvals": 0,
        "approved_homonym_links": 0,
        "fragments_are_not_proof_of_lexical_homonymy": True,
        "prior_scholarly_source_limits": "OLT-017A/017B dossiers are research evidence, not independent lexical signoff",
        "publication_status": "BLOCKED",
        "cases": cases,
    }


def render(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare exact committed derived source triage")
    args = parser.parse_args()
    data = build(
        json.loads(EDITORIAL.read_text(encoding="utf-8")),
        json.loads(WAVE_A.read_text(encoding="utf-8")),
        json.loads(WAVE_B.read_text(encoding="utf-8")),
    )
    value = render(data)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != value:
            raise SystemExit("FAIL: OLT-031 triage differs from original-source research; submit a reviewed PR")
        print("PASS: OLT-031 exact source-linked variation review queue; no English approvals")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(value, encoding="utf-8")
        print("Wrote source-linked triage; all 42 variants remain REVIEW_REQUIRED; publication BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
