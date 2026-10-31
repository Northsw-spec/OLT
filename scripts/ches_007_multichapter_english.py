"""CHES-007: small private CHES-backed English working drafts beyond Genesis 1.

CHES green PDF text is used only as *private source evidence*. Mechanical
gloss streams are NOT grammatical English translations, approved OLT verses,
or proof of any Hebrew/Aramaic-to-CHES word/morpheme alignment.

The full original PDF SHA-256 is verified against the pinned manifest by
the source loader. CLI prints numerical/status metadata ONLY.
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
from scripts.ches_006_layout_metrics import PILOT, audit_real_pdf, measure_private_chapter_layout
from scripts.ches_import import import_private_pdf, write_private_json
from scripts.ches_lite_english import (
    CHESLiteError, OWNER_LEMMA_REVIEW_CANDIDATES, SPACE, _safe_text, _source_lemma_parts,
)
from scripts.ches_private_alignment_review import private_file

# Genesis 1's existing CHES-004 generator remains intact. Only extend the
# existing lean approach to already pinned, independent chapter layouts.
NEW_ENGLISH_CHAPTERS = frozenset({("Gen", 2), ("Gen", 3), ("Exod", 1)})
REF_RE = re.compile(r"^(Gen|Exod)\.([1-9]\d*)\.([1-9]\d*)$")


class CHES007Error(ValueError):
    """Original-source verification, editorial safety or privacy gate failed."""


def _validate_private_edits(
    editorial: dict[str, Any] | None, *,
    book: str, chapter: int, source_sha256: str, verse_count: int,
) -> dict[str, dict[str, str]]:
    if editorial is None:
        return {}
    if (not isinstance(editorial, dict) or set(editorial) != {
        "original_source_pdf_sha256", "chapter_reference", "unapproved_verse_edits"
    } or editorial.get("original_source_pdf_sha256") != source_sha256 or
        editorial.get("chapter_reference") != f"{book}.{chapter}" or
        not isinstance(editorial.get("unapproved_verse_edits"), list) or
        len(editorial["unapproved_verse_edits"]) > verse_count):
        raise CHES007Error("Private editorial file mismatches the pinned original chapter")
    validated: dict[str, dict[str, str]] = {}
    for entry in editorial["unapproved_verse_edits"]:
        if (not isinstance(entry, dict) or set(entry) != {
            "reference", "english_text_unapproved", "editor_note_private", "approved"
        } or entry.get("approved") is not False):
            raise CHES007Error("Editor must provide only unapproved private verse edits")
        ref = entry["reference"]
        if (not isinstance(ref, str) or
            ref not in {f"{book}.{chapter}.{i}" for i in range(1, verse_count + 1)} or
            ref in validated):
            raise CHES007Error("Editor verse ID missing, duplicated or outside source chapter")
        try:
            english = _safe_text(entry["english_text_unapproved"], "private English verse", maximum=3000)
            note = _safe_text(entry["editor_note_private"], "private editorial evidence note", maximum=4000)
        except CHESLiteError as err:
            raise CHES007Error("Invalid private editorial text") from err
        if len(note.strip()) < 12:
            raise CHES007Error("Private editorial evidence note is too short")
        validated[ref] = {"english": english, "note": note}
    return validated


def build_private_pinned_english_chapter(
    private_source: dict[str, Any],
    editorial: dict[str, Any] | None = None,
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Build private verse-level CHES English glosses with authentic OSHB IDs.

    This accepts the in-memory result of the original PDF parser, not a text
    replacement engine. Its metadata checks pin source identity, but callers
    must use build_private_english_from_original_pdf for byte-level integrity.
    Tests use invented green strings and authentic pinned Hebrew word tokens.
    """
    if not isinstance(private_source, dict):
        raise CHES007Error("Missing original source chapter")
    book, chapter = private_source.get("book"), private_source.get("chapter")
    if (type(book) is not str or type(chapter) is not int or
        (book, chapter) not in NEW_ENGLISH_CHAPTERS):
        raise CHES007Error("Only three additional pinned private chapters are supported")
    verse_count, _ = PILOT[(book, chapter)]
    layout = measure_private_chapter_layout(private_source, root=root)
    sha = private_source["original_source_pdf_sha256"]
    if layout["authentic_oshb_verse_references_checked"] != verse_count:
        raise CHES007Error("Original language source verse count changed")
    edits = _validate_private_edits(
        editorial, book=book, chapter=chapter, source_sha256=sha, verse_count=verse_count
    )
    original_book = load_ot_book(book, root, read_provenance(root))
    originals = {
        v["reference"]: v for v in original_book["verses"]
        if v["reference"].startswith(f"{book}.{chapter}.")
    }
    if len(originals) != verse_count:
        raise CHES007Error("Exact original Hebrew chapter verse inventory is incomplete")
    result_verses: list[dict[str, Any]] = []
    total_words = total_spans = tense_count = lexical_count = 0
    source_word_ids: set[str] = set()
    for number, private_verse in enumerate(private_source["verses"], 1):
        ref = f"{book}.{chapter}.{number}"
        if (not isinstance(private_verse, dict) or private_verse.get("reference") != ref or
            private_verse.get("publication_status") != "BLOCKED"):
            raise CHES007Error("Original PDF verse boundary or rights flag changed")
        green = private_verse["source_ches_spans_NOT_OLT_TRANSLATION"]
        fragments: list[str] = []
        prior: tuple[int, float, float] | None = None
        for row in green:
            if not isinstance(row, dict):
                raise CHES007Error("Original PDF source fragment is not a record")
            try:
                fragment = _safe_text(
                    row.get("original_ches_line_text"), "original private green PDF text"
                )
            except CHESLiteError as err:
                raise CHES007Error("Missing/invalid original green PDF text") from err
            page, x, y = row.get("page"), row.get("pdf_x"), row.get("pdf_y")
            if (type(page) is not int or not 1 <= page <= private_source["source_pdf_page_count"]
                or type(x) not in (int, float) or type(y) not in (int, float)
                or not math.isfinite(x) or not math.isfinite(y) or x < 0 or y < 0):
                raise CHES007Error("Invalid original PDF geometry")
            position = page, round(float(y), 1), float(x)
            if prior is not None and position < prior:
                raise CHES007Error("CHES text fragment ordering changed within original verse")
            prior = position
            fragments.append(SPACE.sub(" ", fragment).strip())
        originals_in_verse = originals[ref]["words"]
        token_ids: list[str] = []
        tense_checks: list[dict[str, Any]] = []
        lexical_candidates: list[dict[str, Any]] = []
        for ordinal, word in enumerate(originals_in_verse, 1):
            if (not isinstance(word, dict) or word.get("reference") != ref or
                word.get("ordinal") != ordinal or
                not isinstance(word.get("source_id"), str) or not word["source_id"] or
                not isinstance(word.get("morph_raw"), str) or
                not isinstance(word.get("lemma_raw"), str) or
                not isinstance(word.get("hebrew"), str) or not word["hebrew"] or
                word.get("source_status") != "IMPORTED_UNREVIEWED" or
                word["source_id"] in source_word_ids):
                raise CHES007Error("Original Hebrew source ID, order or morphology changed")
            token_ids.append(word["source_id"])
            source_word_ids.add(word["source_id"])
            if verified_wayyiqtol(word["morph_raw"]):
                tense_checks.append({
                    "original_token_id": word["source_id"],
                    "original_morphology": word["morph_raw"],
                    "english_rule": "ENGLISH_SIMPLE_PAST_REQUIRED",
                    "corresponding_ches_gloss_span": "NOT_VERIFIED",
                    "rule_applied_to_english_text": False,
                })
            for lemma, hint in OWNER_LEMMA_REVIEW_CANDIDATES.items():
                if lemma in _source_lemma_parts(word["lemma_raw"]):
                    lexical_candidates.append({
                        "original_token_id": word["source_id"],
                        "original_source_lemma": word["lemma_raw"],
                        "owner_english_candidate": hint["english_candidate"],
                        "ches_gloss_span_mapping": "NOT_VERIFIED",
                        "rule_applied_to_english_text": False,
                    })
        edited = edits.get(ref)
        # This *only* assembles private source gloss fragments, not Hebrew
        # word-aligned English grammar or a published OLT verse.
        raw_gloss_stream = " ".join(fragments)
        result_verses.append({
            "reference": ref,
            "original_source_word_token_ids": token_ids,
            "original_source_word_count": len(token_ids),
            "private_original_ches_green_span_count": len(fragments),
            "ches_raw_gloss_stream_private_unapproved": raw_gloss_stream,
            "english_text_private_unapproved": edited["english"] if edited else raw_gloss_stream,
            "english_text_origin": (
                "EXPLICIT_PRIVATE_EDITORIAL_VERSE_EDIT_UNAPPROVED"
                if edited else "MECHANICAL_CHES_SOURCE_GLOSS_STREAM_NOT_OLT_TRANSLATION"
            ),
            "editorial_evidence_note_private": edited["note"] if edited else None,
            "source_tagged_wayyiqtol_requirements": tense_checks,
            "original_source_lexical_override_candidates": lexical_candidates,
            "oshb_to_ches_word_alignment_verified": False,
            "all_source_grammar_rules_applied": False,
            "english_owner_approved": False,
            "english_draft_status": "UNREVIEWED_PRIVATE_ENGLISH_WORKING_DRAFT",
            "publication_status": "BLOCKED",
        })
        total_words += len(token_ids)
        total_spans += len(fragments)
        tense_count += len(tense_checks)
        lexical_count += len(lexical_candidates)
    if (total_words != layout["authentic_oshb_word_tokens_observed_not_ches_aligned"] or
        total_spans != layout["private_pdf_green_spans_observed_not_oshb_word_aligned"]):
        raise CHES007Error("Source-language words or private PDF spans changed mid-build")
    return {
        "checkpoint": "CHES-007",
        "scope": f"{book}.{chapter}",
        "source_pdf_sha256": sha,
        "original_pdf_source_pin_verified_by_metadata": True,
        "original_pdf_bytes_reparsed_in_this_function": False,
        "english_language_only": True,
        "private_copyrighted_source_text": True,
        "source_verse_qa_count_only": layout,
        "verse_count": len(result_verses),
        "original_hebrew_token_count": total_words,
        "original_ches_pdf_green_span_count": total_spans,
        "source_wayyiqtol_simple_past_requirements": tense_count,
        "owner_lexical_override_candidates_not_applied": lexical_count,
        "private_editorial_verse_edits_unapproved": len(edits),
        "word_alignment_verified": False,
        "all_english_grammar_rules_applied": False,
        "old_full_lexical_engine_required": False,
        "english_translation_owner_approved": False,
        "complete_english_bible_owner_approved": False,
        "publication_status": "BLOCKED",
        "verses": result_verses,
    }


def build_private_english_from_original_pdf(
    original_pdf_bytes: bytes, *, book: str, chapter: int,
    editorial: dict[str, Any] | None = None, root: Path = ROOT,
) -> dict[str, Any]:
    """Default trusted API: verify the actual PDF bytes, then build in memory."""
    if (type(book) is not str or type(chapter) is not int or
        (book, chapter) not in NEW_ENGLISH_CHAPTERS):
        raise CHES007Error("Unsupported English pilot original chapter")
    verses, _ = PILOT[(book, chapter)]
    # Audits actual original PDF bytes, its hash, every real source span and the
    # authentic original Hebrew verse and word-token references.
    verified_layout = audit_real_pdf(original_pdf_bytes, book=book, chapter=chapter, root=root)
    source = import_private_pdf(original_pdf_bytes, book, chapter, expected_verses=verses)
    report = build_private_pinned_english_chapter(source, editorial, root=root)
    if (report["original_hebrew_token_count"] !=
        verified_layout["authentic_oshb_word_tokens_observed_not_ches_aligned"] or
        report["original_ches_pdf_green_span_count"] !=
        verified_layout["private_pdf_green_spans_observed_not_oshb_word_aligned"]):
        raise CHES007Error("Source integrity drift between PDF and private English draft")
    report["source_verse_qa_count_only"] = verified_layout
    report["original_pdf_bytes_reparsed_in_this_function"] = True
    return report


def _count_only_audit(report: dict[str, Any]) -> dict[str, Any]:
    allow = (
        "checkpoint", "scope", "verse_count", "original_hebrew_token_count",
        "original_ches_pdf_green_span_count", "source_wayyiqtol_simple_past_requirements",
        "owner_lexical_override_candidates_not_applied", "private_editorial_verse_edits_unapproved",
        "original_pdf_source_pin_verified_by_metadata", "original_pdf_bytes_reparsed_in_this_function",
        "word_alignment_verified", "all_english_grammar_rules_applied",
        "english_translation_owner_approved", "publication_status",
    )
    return {key: report[key] for key in allow}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Private CHES-007 English verse-level gloss pilot (never public source text)"
    )
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--book", required=True, choices=("Gen", "Exod"))
    parser.add_argument("--chapter", required=True, type=int)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--output-private", type=Path)
    parser.add_argument("--editorial-private", type=Path)
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Explicit original-source machine-readable permission required")
    if args.editorial_private and args.output_private is None:
        parser.error("Private editorial file cannot be used in counts-only audit")
    editorial = (json.loads(private_file(args.editorial_private).read_text(encoding="utf-8"))
                 if args.editorial_private is not None else None)
    report = build_private_english_from_original_pdf(
        args.pdf.read_bytes(), book=args.book, chapter=args.chapter, editorial=editorial
    )
    if args.output_private is not None:
        write_private_json(report, private_file(args.output_private))
    # Never print original CHES strings, private editor notes, or Hebrew verses.
    print(json.dumps(_count_only_audit(report), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
