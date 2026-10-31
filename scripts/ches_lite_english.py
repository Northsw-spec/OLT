"""CHES-004: smallest honest CHES-backed English Genesis 1 draft pipeline.

The pinned original PDF's English interlinear fragments provide a PRIVATE
gloss-stream starting point; authentic OSHB Hebrew checks provide exceptions.
There is deliberately NO fabricated span-to-Hebrew word alignment, no
automatic tense correction against an unknown English fragment, and no
English Bible publication capability. Raw copyrighted CHES text never goes
to stdout; output may only be stored under .olt-private/.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
from typing import Any

from olt_core.english_drafts import verified_wayyiqtol
from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_import import import_private_pdf, write_private_json
from scripts.ches_oshb_verse_qa import verify_genesis_1_verse_locators
from scripts.ches_private_alignment_review import private_file

# Each number is a source-lexicon annotation, NOT evidence that a green PDF
# span represents the same original word. This is a small editorial pilot.
OWNER_LEMMA_REVIEW_CANDIDATES = {
    "1254": {"lemma_hint": "bara", "english_candidate": "shaped"},
    "6213": {"lemma_hint": "asah", "english_candidate": "make"},
    "7549": {"lemma_hint": "raqia", "english_candidate": "firmament"},
}
SPACE = re.compile(r"\s+")


class CHESLiteError(ValueError):
    """A source, owner-rule, privacy or editorial boundary was violated."""


def _safe_text(value: Any, label: str, *, maximum: int = 4096) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise CHESLiteError("Missing, empty or oversized " + label)
    if "\x00" in value:
        raise CHESLiteError("Forbidden NUL byte in " + label)
    return value


def _source_lemma_parts(raw: Any) -> set[str]:
    if not isinstance(raw, str):
        raise CHESLiteError("Missing original lemma annotation")
    return set(re.split(r"[/+\s]+", raw))


def _editorial_edits(edits: dict[str, Any] | None, source_sha: str) -> dict[str, dict[str, str]]:
    """Explicit private verse-level owner edits, not a word-alignment fiction."""
    if edits is None:
        return {}
    if not isinstance(edits, dict) or set(edits) != {
        "original_source_pdf_sha256", "chapter_reference", "unapproved_verse_edits"
    }:
        raise CHESLiteError("Invalid editorial input contract")
    if (edits["original_source_pdf_sha256"] != source_sha or
        edits["chapter_reference"] != "Gen.1" or
        not isinstance(edits["unapproved_verse_edits"], list)):
        raise CHESLiteError("Editorial notes refer to another source chapter")
    out: dict[str, dict[str, str]] = {}
    for row in edits["unapproved_verse_edits"]:
        if not isinstance(row, dict) or set(row) != {
            "reference", "english_text_unapproved", "editor_note_private", "approved"
        } or row["approved"] is not False:
            raise CHESLiteError("Editorial verse proposal must remain unapproved")
        ref = row["reference"]
        if (not isinstance(ref, str) or not re.fullmatch(r"Gen\.1\.([1-9]|[12]\d|3[01])", ref)
            or ref in out):
            raise CHESLiteError("Duplicate/invalid Genesis 1 editorial verse")
        text = _safe_text(row["english_text_unapproved"], "English editorial draft", maximum=3000)
        note = _safe_text(row["editor_note_private"], "editorial evidence note", maximum=4000)
        if len(note.strip()) < 12:
            raise CHESLiteError("Editorial change needs a meaningful evidence note")
        out[ref] = {"text": text, "note": note}
    return out


def build_private_genesis_one_english_drafts(
    private_chapter: dict[str, Any],
    editorial: dict[str, Any] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Build *real CHES-derived* English gloss streams in private, verse by verse.

    No word mapping is asserted. Original-source lemma/tense policies become
    source-ID-keyed review suggestions, not arbitrary string replacements.
    """
    summary = verify_genesis_1_verse_locators(private_chapter, root)
    sha = private_chapter["original_source_pdf_sha256"]
    changes = _editorial_edits(editorial, sha)
    book = load_ot_book("Gen", root, read_provenance(root))
    original = {
        verse["reference"]: verse for verse in book["verses"]
        if re.fullmatch(r"Gen\.1\.([1-9]|[12]\d|3[01])", verse["reference"])
    }
    if len(original) != 31:
        raise CHESLiteError("No exact authentic Hebrew Genesis 1 original source")
    verses: list[dict[str, Any]] = []
    totals = {"words": 0, "spans": 0, "wayyiqtol": 0, "lexical_candidates": 0}
    for number, ches_verse in enumerate(private_chapter["verses"], 1):
        ref = f"Gen.1.{number}"
        if ches_verse["reference"] not in {ref, f"gen.1.{number}"}:
            raise CHESLiteError("Private English source verse identity changed")
        rows = ches_verse["source_ches_spans_NOT_OLT_TRANSLATION"]
        fragments: list[str] = []
        prior: tuple[int, float, float] | None = None
        for row in rows:
            if not isinstance(row, dict):
                raise CHESLiteError("Malformed source span")
            raw = _safe_text(row.get("original_ches_line_text"), "private green PDF text")
            page, x, y = row.get("page"), row.get("pdf_x"), row.get("pdf_y")
            if (type(page) is not int or not 1 <= page <= private_chapter["source_pdf_page_count"]
                or type(x) not in (int, float) or type(y) not in (int, float)
                or not math.isfinite(x) or not math.isfinite(y)
                or x < 0 or y < 0):
                raise CHESLiteError("Invalid original PDF source span geometry")
            locator = (page, round(y, 1), float(x))
            if prior is not None and locator < prior:
                raise CHESLiteError("Original interlinear span order was modified")
            prior = locator
            fragments.append(SPACE.sub(" ", raw).strip())

        words = original[ref]["words"]
        if not isinstance(words, list) or not words:
            raise CHESLiteError("Missing authentic Hebrew words")
        word_ids: list[str] = []
        tense: list[dict[str, Any]] = []
        candidates: list[dict[str, Any]] = []
        for ordinal, w in enumerate(words, 1):
            if (not isinstance(w, dict) or w.get("reference") != ref or
                w.get("ordinal") != ordinal or not isinstance(w.get("source_id"), str)
                or not isinstance(w.get("morph_raw"), str)):
                raise CHESLiteError("Source Hebrew token identity changed")
            word_ids.append(w["source_id"])
            if verified_wayyiqtol(w["morph_raw"]):
                tense.append({
                    "original_token_id": w["source_id"],
                    "original_morphology": w["morph_raw"],
                    "english_rule": "ENGLISH_SIMPLE_PAST_REQUIRED",
                    "english_source_fragment_mapping": "NOT_VERIFIED",
                    "rule_applied_to_ches_gloss_stream": False,
                })
            seen = _source_lemma_parts(w.get("lemma_raw"))
            for code, hint in OWNER_LEMMA_REVIEW_CANDIDATES.items():
                if code in seen:
                    candidates.append({
                        "original_token_id": w["source_id"],
                        "source_lemma_annotation": w["lemma_raw"],
                        "original_lemma_hint": hint["lemma_hint"],
                        "owner_english_candidate": hint["english_candidate"],
                        "ches_gloss_span_mapping": "NOT_VERIFIED",
                        "rule_application": "PENDING_REVIEW_NO_AUTOMATIC_TEXT_REPLACEMENT",
                    })
        if len(word_ids) != len(set(word_ids)):
            raise CHESLiteError("Duplicate Hebrew original source word IDs")
        edit = changes.get(ref)
        # This is a mechanical reading of the actual third-party interlinear,
        # not a grammatical OLT translation. Spaces are NOT Hebrew word breaks.
        ches_gloss_stream = " ".join(fragments)
        verses.append({
            "reference": ref,
            "original_source_word_token_ids": word_ids,
            "original_source_word_count": len(word_ids),
            "private_original_ches_green_span_count": len(fragments),
            "ches_raw_gloss_stream_private_unapproved": ches_gloss_stream,
            "english_text_private_unapproved": edit["text"] if edit else ches_gloss_stream,
            "english_text_origin": (
                "EXPLICIT_PRIVATE_EDITORIAL_VERSE_EDIT_UNAPPROVED"
                if edit else "MECHANICAL_CHES_SOURCE_GLOSS_STREAM_NOT_OLT_TRANSLATION"
            ),
            "editorial_evidence_note_private": edit["note"] if edit else None,
            "source_tagged_wayyiqtol_requirements": tense,
            "original_source_lexical_override_candidates": candidates,
            "word_alignment_verified": False,
            "all_source_grammar_rules_applied": False,
            "english_draft_status": "UNREVIEWED_PRIVATE_ENGLISH_WORKING_DRAFT",
            "english_owner_approved": False,
            "publication_status": "BLOCKED",
        })
        totals["words"] += len(word_ids)
        totals["spans"] += len(fragments)
        totals["wayyiqtol"] += len(tense)
        totals["lexical_candidates"] += len(candidates)
    if totals["words"] != 434 or totals["spans"] != 526 or totals["wayyiqtol"] != 50:
        raise CHESLiteError("Pinned authentic Genesis English draft source counts changed")
    if not set(changes).issubset({v["reference"] for v in verses}):
        raise CHESLiteError("Editorial references not present in the original text")
    return {
        "checkpoint": "CHES-004",
        "scope": "Gen.1_ONLY",
        "source_pdf_sha256": sha,
        "english_language_only": True,
        "private_copyrighted_source_text": True,
        "source_verse_qa": summary,
        "genesis_verse_count": len(verses),
        "original_hebrew_token_count": totals["words"],
        "original_ches_pdf_green_span_count": totals["spans"],
        "source_wayyiqtol_simple_past_requirements": totals["wayyiqtol"],
        "owner_lexical_override_candidates_not_applied": totals["lexical_candidates"],
        "private_editorial_verse_edits_unapproved": len(changes),
        "word_alignment_verified": False,
        "all_english_grammar_rules_applied": False,
        "old_full_lexical_engine_required": False,
        "english_translation_owner_approved": False,
        "complete_english_bible_owner_approved": False,
        "publication_status": "BLOCKED",
        "verses": verses,
    }


def _audit(result: dict[str, Any]) -> dict[str, Any]:
    """Return numerical/status telemetry ONLY. Never include copyrighted text."""
    return {key: value for key, value in result.items()
            if key in {
                "checkpoint", "scope", "genesis_verse_count",
                "original_hebrew_token_count", "original_ches_pdf_green_span_count",
                "source_wayyiqtol_simple_past_requirements",
                "owner_lexical_override_candidates_not_applied",
                "private_editorial_verse_edits_unapproved",
                "word_alignment_verified", "all_english_grammar_rules_applied",
                "old_full_lexical_engine_required",
                "english_translation_owner_approved", "publication_status",
            }}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CHES-004 private compact English draft pipeline (no public CHES text)")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--output-private", type=Path)
    parser.add_argument("--editorial-private", type=Path)
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Explicit private source-use permission confirmation is required")
    if args.editorial_private is not None and args.output_private is None:
        parser.error("Editorial input requires private output, not audit-only mode")
    source = import_private_pdf(args.pdf.read_bytes(), "Gen", 1, expected_verses=31)
    editorial = (json.loads(private_file(args.editorial_private).read_text(encoding="utf-8"))
                 if args.editorial_private else None)
    result = build_private_genesis_one_english_drafts(source, editorial)
    if args.output_private:
        write_private_json(result, private_file(args.output_private))
    print(json.dumps(_audit(result), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
