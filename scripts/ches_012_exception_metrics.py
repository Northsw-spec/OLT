"""CHES-012: source-pinned, privacy-safe geometry/exception rates for 14 OT chapters.

Each input must come from the real original PDF audit, with exact SHA-256,
byte-size, original Hebrew source ID counts and printed verse checks. The
output is an allowlisted *numerical* engineering QA report: no CHES source
words, original-language passages, editable glosses or editorial notes.

IMPORTANT: PDF green typography spans are NOT original Hebrew word tokens.
Unequal counts are *layout observations*, not translation errors. A zero
unassigned-fragment count is NOT English translation certification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from olt_core.sources import ROOT
from scripts.ches_006_layout_metrics import audit_real_pdf
from scripts.ches_008_private_batch import (
    ALL_INDEXED_BATCH, _source_pin, _verified_pdf,
)

CHECKPOINT = "CHES-012-FOURTEEN-SOURCE-GEOMETRY-REPORT"
NUMERIC_FIELDS = {
    "authentic_oshb_verse_references_checked": "printed_pdf_verses_confirmed_by_engineering",
    "authentic_oshb_word_tokens_observed_not_ches_aligned": "oshb_original_word_tokens_observed",
    "private_pdf_green_spans_observed_not_oshb_word_aligned": "green_ches_pdf_spans_extracted",
    "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS":
        "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS",
    "verses_with_green_fragments_on_multiple_pdf_pages":
        "verses_with_green_fragments_on_multiple_pdf_pages",
    "min_green_spans_in_one_verse": "min_green_spans_in_one_verse",
    "max_green_spans_in_one_verse": "max_green_spans_in_one_verse",
    "unassigned_original_green_spans": "raw_original_pdf_unassigned_green_spans",
    "source_pdf_byte_length": "source_pdf_bytes",
    "source_pdf_page_count": "source_pdf_pages",
}
TOTAL_FIELDS = (
    "authentic_oshb_verse_references_checked",
    "authentic_oshb_word_tokens_observed_not_ches_aligned",
    "private_pdf_green_spans_observed_not_oshb_word_aligned",
    "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS",
    "verses_with_green_fragments_on_multiple_pdf_pages",
    "unassigned_original_green_spans",
)


class CHES012MetricsError(ValueError):
    """Original PDF/source word/geometry or false approval check failed."""


def _rate_basis_points(numerator: int, denominator: int) -> int:
    if (type(numerator) is not int or type(denominator) is not int or
        denominator <= 0 or not 0 <= numerator <= denominator):
        raise CHES012MetricsError("Invalid engineering numerator or denominator")
    # Integer basis points: 10000 = 100%, deterministic on all Python versions.
    return (numerator * 10000 + denominator // 2) // denominator


def summarize_source_geometry(
    reports: list[dict[str, Any]], *, root: Path = ROOT,
) -> dict[str, Any]:
    """No raw source text in results, even if malicious input adds text keys.

    Only immutable source-pinned chapter identities are accepted. Each real
    PDF SHA and all known geometry warnings must equal its own manifest pin.
    For tests, synthetic metadata reports can be used; they do not establish
    PDF authenticity without the byte-level audit entry point.
    """
    if not isinstance(reports, list) or len(reports) != len(ALL_INDEXED_BATCH):
        raise CHES012MetricsError("Exactly fourteen source-checked chapter reports are required")
    by_scope: dict[str, dict[str, Any]] = {}
    expected_scopes = {f"{book}.{chapter}" for book, chapter, _, _ in ALL_INDEXED_BATCH}
    if len(expected_scopes) != len(ALL_INDEXED_BATCH):
        raise CHES012MetricsError("Original source batch contains duplicate chapter IDs")
    for report in reports:
        if not isinstance(report, dict):
            raise CHES012MetricsError("Untrusted chapter report")
        scope = report.get("scope")
        if type(scope) is not str or scope not in expected_scopes or scope in by_scope:
            raise CHES012MetricsError("Unknown, duplicate or missing original chapter scope")
        by_scope[scope] = report

    totals = {key: 0 for key in TOTAL_FIELDS}
    per_chapter: list[dict[str, Any]] = []
    chapters_with_geometry_review = 0
    for book, chapter, _, source_pin_key in ALL_INDEXED_BATCH:
        scope = f"{book}.{chapter}"
        report = by_scope[scope]
        pin = _source_pin(root, source_pin_key, book, chapter)
        if (report.get("checkpoint") != "CHES-006" or
            report.get("source_pin_status") != "ORIGINAL_PDF_PINNED_EXACT" or
            report.get("source_pdf_sha256") != pin["source_pdf_sha256"] or
            report.get("publication_status") != "BLOCKED" or
            report.get("source_pdf_book_prefix_vs_oshb_mapping_independently_verified") is not False or
            report.get("oshb_to_pdf_word_alignment_verified") is not False or
            report.get("english_translation_automatically_verified") is not False or
            report.get("english_grammar_rules_automatically_applied") is not False or
            report.get("full_old_testament_processed") is not False):
            raise CHES012MetricsError("False original source identity, approval or word alignment")
        for report_key, pin_key in NUMERIC_FIELDS.items():
            measured = report.get(report_key)
            baseline = pin.get(pin_key)
            if (type(measured) is not int or type(baseline) is not int or
                measured != baseline or measured < 0):
                raise CHES012MetricsError("Original geometry changed from immutable PDF source pin")
        verses = report["authentic_oshb_verse_references_checked"]
        mismatches = report[
            "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"
        ]
        crossing = report["verses_with_green_fragments_on_multiple_pdf_pages"]
        unassigned = report["unassigned_original_green_spans"]
        green = report["private_pdf_green_spans_observed_not_oshb_word_aligned"]
        if (verses < 1 or green < verses or
            mismatches > verses or crossing > verses or
            report["min_green_spans_in_one_verse"] < 1 or
            report["max_green_spans_in_one_verse"] < report["min_green_spans_in_one_verse"] or
            type(report.get("printed_verse_markers_checked")) is not int or
            report["printed_verse_markers_checked"] != verses or
            type(report.get("raw_original_pdf_green_span_count")) is not int or
            report["raw_original_pdf_green_span_count"] != green + unassigned or
            type(report.get("raw_original_green_spans_before_first_printed_verse")) is not int or
            report["raw_original_green_spans_before_first_printed_verse"] != unassigned):
            raise CHES012MetricsError("Original PDF verse anchors or green spans cannot be reconciled")
        warned = bool(unassigned or crossing)
        if type(report.get("layout_requires_exception_review")) is not bool or (
            report["layout_requires_exception_review"] != warned
        ):
            raise CHES012MetricsError("Source PDF geometry review flag does not match evidence")
        chapters_with_geometry_review += int(warned)
        for name in TOTAL_FIELDS:
            totals[name] += report[name]
        per_chapter.append({
            "source_scope": scope,
            "original_pdf_sha256": pin["source_pdf_sha256"],
            "original_pdf_page_count": report["source_pdf_page_count"],
            "original_verse_count": verses,
            "original_hebrew_word_token_count_not_ches_aligned":
                report["authentic_oshb_word_tokens_observed_not_ches_aligned"],
            "original_pdf_green_typography_span_count_not_oshb_aligned": green,
            "verses_with_unequal_span_vs_hebrew_word_counts_NOT_TRANSLATION_ERRORS":
                mismatches,
            "unequal_span_word_count_observation_rate_basis_points":
                _rate_basis_points(mismatches, verses),
            "verses_with_green_fragments_on_multiple_pdf_pages": crossing,
            "page_crossing_verse_rate_basis_points": _rate_basis_points(crossing, verses),
            "unassigned_original_green_spans": unassigned,
            "geometry_exception_review_status":
                "REQUIRES_GEOMETRY_REVIEW" if warned else "NO_BOUNDARY_OR_LOSS_WARNING",
            "independent_word_alignment_verified": False,
            "english_owner_approved": False,
            "publication_status": "BLOCKED",
        })
    if not all(total >= 0 for total in totals.values()):
        raise CHES012MetricsError("Invalid original source engineering totals")
    return {
        "checkpoint": CHECKPOINT,
        "real_original_pdf_bytes_reparsed_in_this_function": False,
        "exact_pinned_original_chapters_in_scope": len(per_chapter),
        "source_pdf_hashes_and_geometry_equal_pinned_manifest": True,
        "totals": totals,
        "chapters_requiring_pdf_page_boundary_or_ink_loss_review":
            chapters_with_geometry_review,
        "unequal_span_word_count_observation_rate_basis_points":
            _rate_basis_points(
                totals[
                    "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"
                ], totals["authentic_oshb_verse_references_checked"]
            ),
        "page_crossing_verse_rate_basis_points":
            _rate_basis_points(
                totals["verses_with_green_fragments_on_multiple_pdf_pages"],
                totals["authentic_oshb_verse_references_checked"]
            ),
        "source_word_to_english_gloss_mapping_verified": False,
        "english_translation_grammatically_verified": False,
        "observed_typography_mismatches_are_translation_errors": False,
        "english_owner_approved": False,
        "publication_status": "BLOCKED",
        "per_chapter_metadata": per_chapter,
    }


def audit_fourteen_real_pdfs(folder: Path, *, root: Path = ROOT) -> dict[str, Any]:
    """Trusted entry: check all real original PDF bytes and genuine source data."""
    if not isinstance(folder, Path) or not folder.is_dir() or folder.is_symlink():
        raise CHES012MetricsError("Original private PDF directory is missing or unsafe")
    reports = []
    for book, chapter, filename, pin_key in ALL_INDEXED_BATCH:
        pin = _source_pin(root, pin_key, book, chapter)
        original_bytes = _verified_pdf(folder, filename, pin)
        reports.append(audit_real_pdf(original_bytes, book=book, chapter=chapter, root=root))
    result = summarize_source_geometry(reports, root=root)
    result["real_original_pdf_bytes_reparsed_in_this_function"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CHES-012 source-only numeric geometry and exception QA for 14 original PDFs"
    )
    parser.add_argument("--pdf-directory", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private original source machine-readable use permission required")
    try:
        result = audit_fourteen_real_pdfs(args.pdf_directory)
    except Exception:
        # Original source content, editor text and private filenames cannot
        # enter CI logs via third-party PDF parser exception messages.
        parser.error("CHES-012_ORIGINAL_SOURCE_GEOMETRY_VERIFICATION_FAILED")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
