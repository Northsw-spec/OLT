"""CHES-005: small, source-anchored PRIVATE English exception previews.

A correction is permitted only when a specific original Hebrew token, its
exact source morphology/lemma, an explicit same-verse PDF green span and its
unchanged source text all match an operator-supplied private record. This is
a technically gated working-draft preview, NOT linguistic certification or
automatic source-word alignment. It does not build a new dictionary.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from olt_core.english_drafts import (
    GENESIS_ONE_SIMPLE_PAST_FRAGMENTS,
    verified_wayyiqtol,
)
from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_import import import_private_pdf, write_private_json
from scripts.ches_lite_english import (
    CHESLiteError,
    OWNER_LEMMA_REVIEW_CANDIDATES,
    SPACE,
    _safe_text,
    _source_lemma_parts,
    build_private_genesis_one_english_drafts,
)
from scripts.ches_private_alignment_review import private_file

KINDS = frozenset({"WAYYIQTOL_SIMPLE_PAST", "OWNER_LEXICAL_CHOICE"})
MAX_EXCEPTION_PROPOSALS = 64


class CHESExceptionError(ValueError):
    """Unsafe or unsupported CHES-source-anchored English edit."""


def _validated_rules(
    specs: dict[str, Any] | None,
    original_sha: str,
) -> list[dict[str, Any]]:
    if specs is None:
        return []
    if (not isinstance(specs, dict) or set(specs) != {
        "source_pdf_sha256", "chapter_reference", "unapproved_exception_rules"
    } or specs.get("source_pdf_sha256") != original_sha
        or specs.get("chapter_reference") != "Gen.1"):
        raise CHESExceptionError("Exception specification does not match the original PDF")
    rules = specs.get("unapproved_exception_rules")
    if not isinstance(rules, list) or len(rules) > MAX_EXCEPTION_PROPOSALS:
        raise CHESExceptionError("Exception count is not safely bounded")
    required = {
        "reference", "original_oshb_source_token_id", "expected_original_morphology",
        "expected_original_lemma", "kind", "green_span_ordinal",
        "expected_green_span_text_private", "replacement_english_private",
        "operator_checked_original_pdf_hebrew", "evidence_note_private",
        "approved",
    }
    for proposal in rules:
        if not isinstance(proposal, dict) or set(proposal) != required:
            raise CHESExceptionError("Unexpected exception record fields")
        if (proposal["approved"] is not False or
            proposal["operator_checked_original_pdf_hebrew"] is not True):
            raise CHESExceptionError("Explicit source inspection and unapproved status required")
        if (proposal["kind"] not in KINDS or
            type(proposal["green_span_ordinal"]) is not int or
            proposal["green_span_ordinal"] < 1):
            raise CHESExceptionError("Unsupported rule kind or PDF span ordinal")
        for key in (
            "reference", "original_oshb_source_token_id",
            "expected_original_morphology", "expected_original_lemma",
            "expected_green_span_text_private", "replacement_english_private",
            "evidence_note_private",
        ):
            try:
                _safe_text(proposal[key], "private rule field")
            except CHESLiteError as error:
                raise CHESExceptionError("Invalid or oversized private rule field") from error
        if len(proposal["evidence_note_private"].strip()) < 24:
            raise CHESExceptionError("Manual PDF evidence note too short")
        if len(proposal["replacement_english_private"]) > 200:
            raise CHESExceptionError("One-span replacement is too large")
    return rules


def apply_source_anchored_english_exceptions(
    private_chapter: dict[str, Any],
    proposals: dict[str, Any] | None,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Render a private unapproved English edit, never an approved word link.

    Only a small number of explicit *exceptions* are edited. Uncertain or
    missing crosswalks remain plain raw CHES gloss streams for further review.
    """
    drafts = build_private_genesis_one_english_drafts(private_chapter, root=root)
    rules = _validated_rules(proposals, private_chapter["original_source_pdf_sha256"])
    book = load_ot_book("Gen", root, read_provenance(root))
    oshb_by_ref = {
        row["reference"]: row for row in book["verses"]
        if row["reference"].startswith("Gen.1.")
    }
    verse_rows = {
        f"Gen.1.{i}": row for i, row in enumerate(private_chapter["verses"], 1)
    }
    output_by_ref = {row["reference"]: row for row in drafts["verses"]}
    changed_spans: dict[str, dict[int, str]] = {}
    used_tokens: set[tuple[str, str]] = set()
    private_proofs: dict[str, list[dict[str, Any]]] = {}
    for proposal in rules:
        ref = proposal["reference"]
        if ref not in output_by_ref or ref not in oshb_by_ref:
            raise CHESExceptionError("Exception verse not present in pinned Genesis 1")
        original_matches = [
            word for word in oshb_by_ref[ref]["words"]
            if word.get("source_id") == proposal["original_oshb_source_token_id"]
        ]
        if len(original_matches) != 1:
            raise CHESExceptionError("Source word missing or not unique within original verse")
        word = original_matches[0]
        if (word.get("morph_raw") != proposal["expected_original_morphology"] or
            word.get("lemma_raw") != proposal["expected_original_lemma"]):
            raise CHESExceptionError("Original word morphology or lemma does not match")
        token_key = (ref, word["source_id"])
        if token_key in used_tokens:
            raise CHESExceptionError("A source token already has a separate exception")
        index = proposal["green_span_ordinal"] - 1
        green = verse_rows[ref]["source_ches_spans_NOT_OLT_TRANSLATION"]
        if index >= len(green) or not isinstance(green[index], dict):
            raise CHESExceptionError("Green source span ordinal outside original verse")
        observed = green[index].get("original_ches_line_text")
        if (not isinstance(observed, str) or
            observed != proposal["expected_green_span_text_private"]):
            raise CHESExceptionError("Original PDF green English fragment differs from private evidence")
        if index in changed_spans.get(ref, {}):
            raise CHESExceptionError("Overlapping edits to the same private PDF source span")
        kind = proposal["kind"]
        rendered = proposal["replacement_english_private"].strip()
        if rendered != proposal["replacement_english_private"]:
            raise CHESExceptionError("Replacement must have exact, non-padded wording")
        if kind == "WAYYIQTOL_SIMPLE_PAST":
            if not verified_wayyiqtol(word["morph_raw"]):
                raise CHESExceptionError("Simple past owner rule requires actual original wayyiqtol")
            if rendered.casefold() not in GENESIS_ONE_SIMPLE_PAST_FRAGMENTS:
                raise CHESExceptionError("Tense replacement is not in the small vetted Genesis pilot")
        else:
            if verified_wayyiqtol(word["morph_raw"]):
                raise CHESExceptionError("Lexical-only replacement cannot bypass a tense requirement")
            match = [
                item["english_candidate"] for lemma, item in
                OWNER_LEMMA_REVIEW_CANDIDATES.items()
                if lemma in _source_lemma_parts(word["lemma_raw"])
            ]
            if len(match) != 1 or rendered.casefold() != match[0].casefold():
                raise CHESExceptionError("Lexical replacement not a supported owner choice")
        used_tokens.add(token_key)
        changed_spans.setdefault(ref, {})[index] = rendered
        private_proofs.setdefault(ref, []).append({
            "kind": kind,
            "original_oshb_source_token_id": word["source_id"],
            "exact_original_morphology": word["morph_raw"],
            "exact_original_lemma": word["lemma_raw"],
            "green_span_ordinal_in_verse": index + 1,
            "green_span_source_text_private": observed,
            "green_span_replacement_private_unapproved": rendered,
            "operator_checked_original_pdf_hebrew": True,
            "private_evidence_note": proposal["evidence_note_private"].strip(),
            "semantic_mapping_independently_certified": False,
            "english_draft_owner_approved": False,
        })
    for ref, choices in changed_spans.items():
        spans = verse_rows[ref]["source_ches_spans_NOT_OLT_TRANSLATION"]
        # Replace *only* explicitly selected and exactly matched source spans.
        # This cannot silently alter every matching surface word in a chapter.
        preview = [
            choices.get(index, SPACE.sub(" ", row["original_ches_line_text"]).strip())
            for index, row in enumerate(spans)
        ]
        target = output_by_ref[ref]
        target["english_text_private_unapproved"] = " ".join(preview)
        target["english_text_origin"] = "OPERATOR_SOURCE_ANCHORED_EXCEPTION_PREVIEW_UNAPPROVED"
        target["operator_exception_proofs_private_unapproved"] = private_proofs[ref]
        target["word_alignment_verified"] = False
        target["all_source_grammar_rules_applied"] = False
        target["english_owner_approved"] = False
    drafts["checkpoint"] = "CHES-005"
    drafts["source_anchored_exception_previews_unapproved"] = len(rules)
    drafts["original_chapter_english_stream_unchanged_verses"] = 31 - len(changed_spans)
    drafts["independently_verified_word_mappings"] = 0
    drafts["independently_verified_english_translations"] = 0
    drafts["automatic_guess_based_word_substitutions"] = 0
    drafts["unapproved_english_edit_source"] = "PRIVATE_EXPLICIT_OPERATOR_RULES_ONLY"
    return drafts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CHES-005 private, Hebrew-anchored English exception preview")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    parser.add_argument("--rules-private", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--output-private", type=Path)
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Explicit original source permission confirmation is required")
    if args.rules_private is not None and args.output_private is None:
        parser.error("Private exception previews require a private output destination")
    original = import_private_pdf(args.pdf.read_bytes(), "Gen", 1, expected_verses=31)
    rules = (json.loads(private_file(args.rules_private).read_text(encoding="utf-8"))
             if args.rules_private else None)
    preview = apply_source_anchored_english_exceptions(original, rules)
    if args.output_private is not None:
        write_private_json(preview, private_file(args.output_private))
    # Only numeric status fields on stdout: never display the licensed glosses.
    print(json.dumps({
        "checkpoint": preview["checkpoint"],
        "scope": preview["scope"],
        "source_anchored_exception_previews_unapproved":
            preview["source_anchored_exception_previews_unapproved"],
        "original_chapter_english_stream_unchanged_verses":
            preview["original_chapter_english_stream_unchanged_verses"],
        "original_hebrew_token_count": preview["original_hebrew_token_count"],
        "original_ches_pdf_green_span_count": preview["original_ches_pdf_green_span_count"],
        "source_wayyiqtol_simple_past_requirements":
            preview["source_wayyiqtol_simple_past_requirements"],
        "automatic_guess_based_word_substitutions": 0,
        "independently_verified_word_mappings": 0,
        "word_alignment_verified": False,
        "publication_status": "BLOCKED",
    }, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
