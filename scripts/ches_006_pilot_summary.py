"""CHES-006: reproducible aggregate of four exact original-source PDF audits.

The program opens four PRIVATE source PDFs under a caller-provided directory,
verifies each exact source pin and genuine OSHB word inventory, and outputs
NUMBERS ONLY. Original English interlinear text is never logged or exported.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from olt_core.sources import ROOT
from scripts.ches_006_layout_metrics import PILOT, audit_real_pdf

CHAPTER_FILES = (
    ("Gen", 1, "ches-gen1.pdf"),
    ("Gen", 2, "ches-gen2.pdf"),
    ("Gen", 3, "ches-gen3.pdf"),
    ("Exod", 1, "ches-ex1.pdf"),
)


class CHESPilotSummaryError(ValueError):
    """Missing source audit or unsupported promotion of unverified text."""


def summarize_exact_pilot(reports: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(reports, list) or len(reports) != len(CHAPTER_FILES):
        raise CHESPilotSummaryError("Expected exactly four original source chapter audits")
    expected_scopes = {f"{book}.{chapter}" for book, chapter, _ in CHAPTER_FILES}
    observed_scopes: set[str] = set()
    totals = {
        "authentic_oshb_verse_references_checked": 0,
        "authentic_oshb_word_tokens_observed_not_ches_aligned": 0,
        "private_pdf_green_spans_observed_not_oshb_word_aligned": 0,
        "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS": 0,
        "verses_with_green_fragments_on_multiple_pdf_pages": 0,
        "unassigned_original_green_spans": 0,
    }
    chapters_requiring_geometry_review = 0
    for report in reports:
        if not isinstance(report, dict) or (
            report.get("checkpoint") != "CHES-006" or
            report.get("source_pin_status") != "ORIGINAL_PDF_PINNED_EXACT" or
            report.get("publication_status") != "BLOCKED" or
            report.get("oshb_to_pdf_word_alignment_verified") is not False or
            report.get("english_translation_automatically_verified") is not False or
            report.get("english_grammar_rules_automatically_applied") is not False or
            report.get("full_old_testament_processed") is not False
        ):
            raise CHESPilotSummaryError("Unpinned, incomplete or falsely approved chapter audit")
        scope = report.get("scope")
        if not isinstance(scope, str) or scope not in expected_scopes or scope in observed_scopes:
            raise CHESPilotSummaryError("Duplicate or missing original source chapter scope")
        observed_scopes.add(scope)
        for key in totals:
            value = report.get(key)
            if type(value) is not int or value < 0:
                raise CHESPilotSummaryError("Noninteger, negative or unknown layout metric")
            totals[key] += value
        original_count = report.get("raw_original_pdf_green_span_count")
        if (type(original_count) is not int or
            original_count != report["private_pdf_green_spans_observed_not_oshb_word_aligned"] +
            report["unassigned_original_green_spans"]):
            raise CHESPilotSummaryError("Original source green ink was not accounted for")
        if report["authentic_oshb_verse_references_checked"] < 1:
            raise CHESPilotSummaryError("Original source has no authentic verses")
        if report["verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"] > report["authentic_oshb_verse_references_checked"]:
            raise CHESPilotSummaryError("Per-verse typography warning count exceeds source verses")
        warned = bool(report["verses_with_green_fragments_on_multiple_pdf_pages"] or
                      report["unassigned_original_green_spans"])
        if type(report.get("layout_requires_exception_review")) is not bool or (
            report["layout_requires_exception_review"] != warned
        ):
            raise CHESPilotSummaryError("PDF layout review flag contradicts measured source geometry")
        chapters_requiring_geometry_review += int(warned)
    if observed_scopes != expected_scopes:
        raise CHESPilotSummaryError("Exact four source chapters missing")
    return {
        "checkpoint": "CHES-006-FOUR-CHAPTER-AGGREGATE",
        "original_pdf_chapters_checked_exact_source_hash": len(reports),
        "scope": ["Gen.1", "Gen.2", "Gen.3", "Exod.1"],
        **totals,
        "chapters_with_page_boundary_or_unassigned_ink_geometry_warnings":
            chapters_requiring_geometry_review,
        "original_word_to_ches_span_links_independently_verified": 0,
        "original_pdf_filename_prefix_to_oshb_mapping_independently_verified": False,
        "pdf_span_word_count_differences_are_translation_errors": False,
        "english_grammar_rules_automatically_applied": False,
        "whole_old_testament_imported": False,
        "english_translation_owner_approved": False,
        "publication_status": "BLOCKED",
    }


def assert_pinned_geometry_warning_baseline(
    reports: list[dict[str, Any]], *, root: Path = ROOT,
) -> None:
    """Catch parser changes that silently alter the four real PDF layouts.

    Source hashes/pinned byte sizes already establish exact file identity.
    This extra check freezes *diagnostic counts*, not linguistic truth.
    """
    manifest = json.loads(
        (root / "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8")
    )
    by_scope = {r["scope"]: r for r in reports}
    if len(by_scope) != len(CHAPTER_FILES):
        raise CHESPilotSummaryError("Incomplete or duplicated source layout baseline")
    pairs = {
        "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS":
            "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS",
        "verses_with_green_fragments_on_multiple_pdf_pages":
            "verses_with_green_fragments_on_multiple_pdf_pages",
        "raw_original_pdf_unassigned_green_spans": "unassigned_original_green_spans",
        "min_green_spans_in_one_verse": "min_green_spans_in_one_verse",
        "max_green_spans_in_one_verse": "max_green_spans_in_one_verse",
    }
    for book, chapter, _ in CHAPTER_FILES:
        _, manifest_key = PILOT[(book, chapter)]
        pinned = manifest[manifest_key]
        report = by_scope[f"{book}.{chapter}"]
        for source_field, result_field in pairs.items():
            expected, actual = pinned.get(source_field), report.get(result_field)
            if type(expected) is not int or type(actual) is not int or actual != expected:
                raise CHESPilotSummaryError(
                    "Original PDF diagnostic geometry baseline changed: "
                    f"{book}.{chapter} / {source_field}"
                )


def audit_exact_pilot_pdfs(folder: Path) -> dict[str, Any]:
    if not isinstance(folder, Path) or not folder.is_dir():
        raise CHESPilotSummaryError("Private original PDF working directory is absent")
    reports = [
        audit_real_pdf(
            (folder / filename).read_bytes(), book=book, chapter=chapter
        )
        for book, chapter, filename in CHAPTER_FILES
    ]
    summary = summarize_exact_pilot(reports)
    assert_pinned_geometry_warning_baseline(reports)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="CHES four original PDFs count-only QA")
    parser.add_argument("--pdf-directory", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Original machine-readable source-use permission confirmation is required")
    print(json.dumps(audit_exact_pilot_pdfs(args.pdf_directory), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
