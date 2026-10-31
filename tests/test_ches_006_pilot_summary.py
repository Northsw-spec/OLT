"""CHES-006: aggregate numerical diagnostics without any original PDF text."""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from scripts.ches_006_pilot_summary import (
    CHESPilotSummaryError, CHAPTER_FILES, assert_pinned_geometry_warning_baseline, audit_exact_pilot_pdfs,
    summarize_exact_pilot,
)


def numeric_reports():
    rows = [
        ("Gen.1", 31, 434, 526, 24, 1, 6, 35),
        ("Gen.2", 25, 328, 377, 18, 1, 7, 30),
        ("Gen.3", 24, 347, 415, 19, 2, 8, 26),
        ("Exod.1", 22, 240, 350, 16, 0, 3, 30),
    ]
    result = []
    for ref, verses, words, green, different, crosspage, min_span, max_span in rows:
        result.append({
            "checkpoint": "CHES-006",
            "scope": ref,
            "source_pin_status": "ORIGINAL_PDF_PINNED_EXACT",
            "publication_status": "BLOCKED",
            "oshb_to_pdf_word_alignment_verified": False,
            "english_translation_automatically_verified": False,
            "english_grammar_rules_automatically_applied": False,
            "full_old_testament_processed": False,
            "authentic_oshb_verse_references_checked": verses,
            "authentic_oshb_word_tokens_observed_not_ches_aligned": words,
            "private_pdf_green_spans_observed_not_oshb_word_aligned": green,
            "raw_original_pdf_green_span_count": green,
            "unassigned_original_green_spans": 0,
            "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS": different,
            "verses_with_green_fragments_on_multiple_pdf_pages": crosspage,
            "layout_requires_exception_review": bool(crosspage),
            "min_green_spans_in_one_verse": min_span,
            "max_green_spans_in_one_verse": max_span,
        })
    return result


class TestCHES006PilotSummary(unittest.TestCase):
    def test_original_source_metric_aggregate_not_an_alignment_or_translation(self):
        output = summarize_exact_pilot(numeric_reports())
        assert_pinned_geometry_warning_baseline(numeric_reports())
        self.assertEqual(output["original_pdf_chapters_checked_exact_source_hash"], 4)
        self.assertEqual(output["scope"], ["Gen.1", "Gen.2", "Gen.3", "Exod.1"])
        self.assertEqual(output["authentic_oshb_verse_references_checked"], 102)
        self.assertEqual(output["authentic_oshb_word_tokens_observed_not_ches_aligned"], 1349)
        self.assertEqual(output["private_pdf_green_spans_observed_not_oshb_word_aligned"], 1668)
        self.assertEqual(
            output["verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"], 77)
        self.assertEqual(output["verses_with_green_fragments_on_multiple_pdf_pages"], 4)
        self.assertEqual(output["unassigned_original_green_spans"], 0)
        self.assertEqual(
            output["chapters_with_page_boundary_or_unassigned_ink_geometry_warnings"], 3)
        self.assertEqual(output["original_word_to_ches_span_links_independently_verified"], 0)
        self.assertFalse(output["english_translation_owner_approved"])
        self.assertFalse(output["whole_old_testament_imported"])
        self.assertFalse(output["pdf_span_word_count_differences_are_translation_errors"])
        self.assertEqual(output["publication_status"], "BLOCKED")

    def test_bad_chapter_count_duplicates_and_untrusted_status_do_not_aggregate(self):
        good = numeric_reports()
        attempts = [
            good[:3],
            good[:3] + [copy.deepcopy(good[0])],
            good + [copy.deepcopy(good[0])],
        ]
        for candidate in attempts:
            with self.assertRaises(CHESPilotSummaryError):
                summarize_exact_pilot(candidate)
        changes = [
            ("publication_status", "PUBLIC"),
            ("source_pin_status", "DISCOVERY_UNPINNED_NOT_APPROVED_FOR_ENGINE"),
            ("oshb_to_pdf_word_alignment_verified", True),
            ("english_grammar_rules_automatically_applied", True),
            ("full_old_testament_processed", True),
            ("raw_original_pdf_green_span_count", -1),
            ("unassigned_original_green_spans", 5),
            ("authentic_oshb_verse_references_checked", True),
            ("verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS", 300),
        ]
        for key, value in changes:
            with self.subTest(field=key), self.assertRaises(CHESPilotSummaryError):
                candidate = copy.deepcopy(good)
                candidate[0][key] = value
                summarize_exact_pilot(candidate)

    def test_pinned_actual_pdf_geometry_diagnostics_detect_parser_regressions(self):
        original = numeric_reports()
        assert_pinned_geometry_warning_baseline(original)
        for key, value in (
            ("verses_with_green_fragments_on_multiple_pdf_pages", 3),
            ("verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS", 25),
            ("unassigned_original_green_spans", 1),
            ("min_green_spans_in_one_verse", 2),
            ("max_green_spans_in_one_verse", 100),
        ):
            with self.subTest(metric=key), self.assertRaises(CHESPilotSummaryError):
                changed = copy.deepcopy(original)
                changed[0][key] = value
                assert_pinned_geometry_warning_baseline(changed)

    def test_missing_real_pdf_directory_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(FileNotFoundError):
                audit_exact_pilot_pdfs(root)
            with self.assertRaises(CHESPilotSummaryError):
                audit_exact_pilot_pdfs(root / "not-existing")


if __name__ == "__main__":
    unittest.main()
