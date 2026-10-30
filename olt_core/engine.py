"""OLT-034 reusable source-first multilingual research-packet engine.

This module DOES NOT automatically translate Hebrew/Greek into another language.
It produces occurrence-bound packets for future independent locale repositories.
English is an optional annotated reference, never an intermediary authority.
All packets and translation decisions remain research-only and release BLOCKED.
"""
from __future__ import annotations

import re
from typing import Any

ENGINE_VERSION = "0.1.0"
CONTRACT_VERSION = "1.0"
ALLOWED_SOURCES = {"hbo": "OT", "arc": "OT", "grc": "NT"}
DIRECTIONS = {"ltr", "rtl"}
RELEASE_BLOCKED = "BLOCKED"
_LOCALE_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


class SourceContractError(ValueError):
    """An input would remove provenance or silently introduce false source claims."""


def _nonempty(row: dict, key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SourceContractError("Missing source-bound field: " + key)
    return value


def validate_locale(profile: dict[str, Any]) -> None:
    if not isinstance(profile, dict):
        raise SourceContractError("Locale profile must be an object")
    tag = _nonempty(profile, "language_tag")
    if not _LOCALE_RE.fullmatch(tag):
        raise SourceContractError("Invalid language tag")
    if _nonempty(profile, "script") == "Unknown":
        raise SourceContractError("Locale script not configured")
    if profile.get("direction") not in DIRECTIONS:
        raise SourceContractError("Locale direction must be ltr or rtl")
    if profile.get("source_first") is not True or profile.get("english_is_reference_only") is not True:
        raise SourceContractError("English is never an intermediate source language")
    if profile.get("publication_status") != RELEASE_BLOCKED:
        raise SourceContractError("Locale publication cannot be preapproved")
    if profile.get("translation_status") not in {"NO_TRANSLATIONS", "RESEARCH_ONLY"}:
        raise SourceContractError("Unknown locale translation status")
    if not isinstance(profile.get("token_choices"), list):
        raise SourceContractError("Locale token choices must be a list")


def validate_source(source: dict[str, Any]) -> None:
    if not isinstance(source, dict):
        raise SourceContractError("Source token must be an object")
    for k in ("verse_id", "token_id", "original_script", "lemma_id", "raw_morphology",
              "source_language", "corpus", "edition_id", "edition_status"):
        _nonempty(source, k)
    language = source["source_language"]
    if language not in ALLOWED_SOURCES or ALLOWED_SOURCES[language] != source["corpus"]:
        raise SourceContractError("Incompatible OT/NT original source-language identity")
    if source.get("edition_status") not in {"IMPORTED_NOT_INDEPENDENTLY_REVIEWED", "PINNED_UNDER_REVIEW"}:
        raise SourceContractError("Source edition is absent or falsely certified")
    if language == "grc" and source["edition_status"] != "PINNED_UNDER_REVIEW":
        raise SourceContractError("NT Greek must be pinned before use")
    if source.get("scholarly_review") != "NOT_DONE":
        raise SourceContractError("Prototype only accepts source tokens without independent signoff")
    if source.get("publication_status") != RELEASE_BLOCKED:
        raise SourceContractError("Source research cannot be claimed published")
    if "english" in source or "english_as_source" in source:
        raise SourceContractError("Source record cannot originate in English")


def from_genesis_1_verse(verse: dict[str, Any]) -> list[dict[str, Any]]:
    """Read real aligned OSHB Hebrew tokens; do not invent NT forms or token IDs."""
    if (verse.get("reference"), verse.get("publication_status"),
        verse.get("independent_scholarly_review")) != ("Gen.1.1", "BLOCKED", "NOT_DONE"):
        raise SourceContractError("Unapproved or mismatched Genesis source edition")
    rows = verse.get("source_alignment")
    if not isinstance(rows, list) or len(rows) != 7 or verse.get("source_token_count") != 7:
        raise SourceContractError("Genesis 1:1 must contain exactly seven original source tokens")
    if rows != sorted(rows, key=lambda x: x.get("ordinal", 0)):
        raise SourceContractError("Original source-token ordering changed")
    if [x.get("pointed_hebrew") for x in rows] != verse.get("original_hebrew_token_sequence"):
        raise SourceContractError("Hebrew original-script sequence changed")
    seen: set[str] = set()
    out = []
    for row in rows:
        if row.get("ordinal") != len(out) + 1:
            raise SourceContractError("Invalid or missing original word ordinal")
        token = _nonempty(row, "source_token_id")
        if token in seen:
            raise SourceContractError("Duplicate original Hebrew token")
        seen.add(token)
        if row.get("source_morphology_verification") != "OSHB_TAG_IMPORTED_NOT_INDEPENDENTLY_SIGNED_OFF":
            raise SourceContractError("Imported morphology must not be independently certified")
        output = {
            "verse_id": "Gen.1.1",
            "ordinal": row["ordinal"],
            "token_id": token,
            "original_script": _nonempty(row, "pointed_hebrew"),
            "lemma_id": _nonempty(row, "exact_lemma_id"),
            "raw_lemma": _nonempty(row, "source_raw_lemma"),
            "raw_morphology": _nonempty(row, "source_morphology"),
            "source_language": "hbo",
            "corpus": "OT",
            "edition_id": "OSHB_WLC_IMPORTED_SOURCE",
            "edition_status": "IMPORTED_NOT_INDEPENDENTLY_REVIEWED",
            "scholarly_review": "NOT_DONE",
            "publication_status": RELEASE_BLOCKED,
        }
        validate_source(output)
        out.append(output)
    return out


def _find_english_reference(source: dict[str, Any], genesis: dict[str, Any]) -> dict[str, Any] | None:
    if source["verse_id"] != "Gen.1.1":
        return None
    match = next((r for r in genesis.get("source_alignment", []) if
                  r.get("source_token_id") == source["token_id"]), None)
    if not match or match.get("exact_lemma_id") != source["lemma_id"] or (
        match.get("pointed_hebrew") != source["original_script"]
    ):
        raise SourceContractError("English reference has no exact original source identity")
    return {
        "language_tag": "en",
        "role": "NONAUTHORITATIVE_EDITORIAL_REFERENCE",
        "candidate_surface": match.get("proposed_english_surface", ""),
        "english_choice_status": match.get("english_choice_status", "RESEARCH_PROPOSAL"),
        "scholarly_review": "NOT_DONE",
        "not_a_target_locale_translation": True,
    }


def _name_english_research(source: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any] | None:
    if registry.get("publication_status") != RELEASE_BLOCKED:
        raise SourceContractError("Name-underword registry must remain research-only")
    matches = []
    for entry in registry.get("entries", []):
        if source["token_id"] in entry.get("verified_olt_source_token_ids", []):
            if (source["verse_id"] != entry["primary_context"] or
                ("H" + source["lemma_id"]) not in entry.get("lexical_reference_ids", []) or
                entry.get("meaning_certified") is not False or
                entry.get("lexical_automatic_render") is not False):
                raise SourceContractError("Name underword original-language match or approval mismatch")
            matches.append(entry)
    if len(matches) > 1:
        raise SourceContractError("Ambiguous name underword source match")
    if not matches:
        return None
    e = matches[0]
    return {
        "name_registry_id": e["id"],
        "english_underword_proposal": e["owner_requested_underword"],
        "evidence_category": e["evidence_category"],
        "editorial_status": e["status"],
        "lexical_meaning_certified": False,
        "is_a_target_translation": False,
        "target_language_word": None,
        "requires_contextual_review": True,
    }


def _target_decision(source: dict[str, Any], locale: dict[str, Any]) -> dict[str, Any] | None:
    choices = [
        row for row in locale["token_choices"]
        if (row.get("verse_id"), row.get("token_id")) == (
            source["verse_id"], source["token_id"]
        )
    ]
    if len(choices) > 1:
        raise SourceContractError("Multiple conflicting target choices for a source occurrence")
    if not choices:
        return None
    choice = choices[0]
    if (choice.get("source_language"), choice.get("lemma_id"), choice.get("original_script")) != (
        source["source_language"], source["lemma_id"], source["original_script"]
    ):
        raise SourceContractError("Target lexical choice does not match original-language token")
    if choice.get("status") != "UNREVIEWED_LOCALE_DRAFT":
        raise SourceContractError("No independent locale approval has been demonstrated")
    value = _nonempty(choice, "target_surface")
    if locale["language_tag"] != choice.get("language_tag"):
        raise SourceContractError("Locale-specific translation must match its language tag")
    return {
        "text": value,
        "language_tag": locale["language_tag"],
        "source_token_id": source["token_id"],
        "status": "UNREVIEWED_LOCALE_DRAFT",
        "meaning_underword": None,
    }


def make_research_packet(source: dict[str, Any], locale: dict[str, Any],
                         genesis: dict[str, Any], name_registry: dict[str, Any]) -> dict[str, Any]:
    """Source -> reviewed-data packet, never English -> automatic target translation."""
    validate_source(source)
    validate_locale(locale)
    if not isinstance(genesis, dict) or not isinstance(name_registry, dict):
        raise SourceContractError("Source/editorial references must be structured objects")
    target = _target_decision(source, locale)
    return {
        "contract_version": CONTRACT_VERSION,
        "engine_version": ENGINE_VERSION,
        "pipeline": "HEBREW_ARAMAIC_GREEK_TO_SOURCE_PACKET_THEN_LOCALE_DECISIONS",
        "source": dict(source),
        "target_language_tag": locale["language_tag"],
        "target_script": locale["script"],
        "target_direction": locale["direction"],
        "english_reference": _find_english_reference(source, genesis),
        "english_is_intermediate_source": False,
        "name_meaning_research": _name_english_research(source, name_registry),
        "locale_proposal": target,
        "locale_proposal_status": "UNTRANSLATED" if target is None else "UNREVIEWED_LOCALE_DRAFT",
        "independent_locale_signoff": False,
        "publication_status": RELEASE_BLOCKED,
    }


def build_genesis_1_1_research_packets(genesis: dict[str, Any], locale: dict[str, Any],
                                       names: dict[str, Any]) -> dict[str, Any]:
    """Small live integration fixture over ALL SEVEN actual original Genesis 1:1 words."""
    records = from_genesis_1_verse(genesis)
    return {
        "checkpoint": "OLT-034",
        "engine_version": ENGINE_VERSION,
        "reference": "Gen.1.1",
        "target_language_tag": locale.get("language_tag"),
        "source_word_token_count": len(records),
        "name_underword_candidates": sum(bool(_name_english_research(s, names)) for s in records),
        "packets": [make_research_packet(s, locale, genesis, names) for s in records],
        "is_translated_scripture": False,
        "publication_status": RELEASE_BLOCKED,
    }
