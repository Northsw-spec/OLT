"""CHES-012: synthetic count-only reports against immutable genuine source pins.

No copyrighted original English source text or Hebrew verse content is stored
in public tests. This tests strict metadata controls, not translation quality.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from olt_core.sources import ROOT
from scripts.ches_008_private_batch import ALL_INDEXED_BATCH, _source_pin
from scripts.ches_012_exception_metrics import (
    CHES012MetricsError, CHECKPOINT, NUMERIC_FIELDS,
    _rate_basis_points, summarize_source_geometry, audit_fourteen_real_pdfs,
)


def fake_source_audits():
    reports = []
    for book, chapter, _filename, key in ALL_INDEXED_BATCH:
        pin = _source_pin(ROOT, key, book, chapter)
        result = {
            "checkpoint": "CHES-006",
            "scope": f"{book}.{chapter}",
            "source_pdf_sha256": pin["source_pdf_sha256"],
            "source_pin_status": "ORIGINAL_PDF_PINNED_EXACT",
            "publication_status": "BLOCKED",
            "source_pdf_book_prefix_vs_oshb_mapping_independently_verified": False,
            "oshb_to_pdf_word_alignment_verified": False,
            "english_translation_automatically_verified": False,
            "english_grammar_rules_automatically_applied": False,
            "full_old_testament_processed": False,
        }
        for result_field, manifest_field in NUMERIC_FIELDS.items():
            result[result_field] = pin[manifest_field]
        result["printed_verse_markers_checked"] = pin[
            "printed_pdf_verses_confirmed_by_engineering"
        ]
        result["raw_original_pdf_green_span_count"] = (
            pin["green_ches_pdf_spans_extracted"] +
            pin["raw_original_pdf_unassigned_green_spans"]
        )
        result["raw_original_green_spans_before_first_printed_verse"] = (
            pin["raw_original_pdf_unassigned_green_spans"]
        )
        result["layout_requires_exception_review"] = bool(
            pin["raw_original_pdf_unassigned_green_spans"] or
            pin["verses_with_green_fragments_on_multiple_pdf_pages"]
        )
        reports.append(result)
    return reports


class TestCHES012FourteenOriginalSourceGeometryMetrics(unittest.TestCase):
    def test_all_fourteen_pinned_sources_yield_reproducible_count_only_rates(self):
        actual = summarize_source_geometry(fake_source_audits())
        self.assertEqual(actual["checkpoint"], CHECKPOINT)
        self.assertFalse(actual["real_original_pdf_bytes_reparsed_in_this_function"])
        self.assertEqual(actual["exact_pinned_original_chapters_in_scope"], 14)
        totals = actual["totals"]
        self.assertEqual(totals["authentic_oshb_verse_references_checked"], 359)
        self.assertEqual(totals["authentic_oshb_word_tokens_observed_not_ches_aligned"], 4913)
        self.assertEqual(totals["private_pdf_green_spans_observed_not_oshb_word_aligned"], 6146)
        self.assertEqual(
            totals["verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"],
            286
        )
        self.assertEqual(totals["verses_with_green_fragments_on_multiple_pdf_pages"], 11)
        self.assertEqual(totals["unassigned_original_green_spans"], 0)
        self.assertEqual(actual["chapters_requiring_pdf_page_boundary_or_ink_loss_review"], 9)
        self.assertEqual(actual["unequal_span_word_count_observation_rate_basis_points"],
                         (286*10000+359//2)//359)
        self.assertEqual(actual["page_crossing_verse_rate_basis_points"],
                         (11*10000+359//2)//359)
        self.assertTrue(actual["source_pdf_hashes_and_geometry_equal_pinned_manifest"])
        self.assertFalse(actual["source_word_to_english_gloss_mapping_verified"])
        self.assertFalse(actual["english_translation_grammatically_verified"])
        self.assertFalse(actual["observed_typography_mismatches_are_translation_errors"])
        self.assertFalse(actual["english_owner_approved"])
        self.assertEqual(actual["publication_status"], "BLOCKED")
        self.assertEqual(len(actual["per_chapter_metadata"]), 14)
        self.assertEqual(actual["per_chapter_metadata"][0]["source_scope"], "Gen.1")
        self.assertEqual(actual["per_chapter_metadata"][-1]["source_scope"], "Exod.6")
        self.assertEqual(sum(row["original_verse_count"] for row in
                             actual["per_chapter_metadata"]), 359)
        self.assertEqual(len([row for row in actual["per_chapter_metadata"]
                              if row["geometry_exception_review_status"] ==
                              "REQUIRES_GEOMETRY_REVIEW"]), 9)

    def test_hostile_added_source_text_must_never_leak_to_count_only_output(self):
        inputs = fake_source_audits()
        inputs[0]["raw_licensed_green_text_private"] = "DO-NOT-LEAK-LICENSED-TEXT"
        inputs[0]["verses"] = [{"english_source": "PRIVATE-ENGLISH-PASSAGE"}]
        output = json.dumps(summarize_source_geometry(inputs))
        self.assertNotIn("DO-NOT-LEAK", output)
        self.assertNotIn("PRIVATE-ENGLISH-PASSAGE", output)
        self.assertNotIn("raw_licensed_green_text_private", output)

    def test_source_pin_and_any_geometry_or_approval_tampering_fail_closed(self):
        base = fake_source_audits()
        cases = (
            ("source_pdf_sha256", "0"*64),
            ("source_pdf_page_count", 100),
            ("source_pdf_byte_length", 2),
            ("authentic_oshb_verse_references_checked", 1),
            ("authentic_oshb_word_tokens_observed_not_ches_aligned", 2),
            ("private_pdf_green_spans_observed_not_oshb_word_aligned", 2),
            ("verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS", 0),
            ("verses_with_green_fragments_on_multiple_pdf_pages", 0),
            ("min_green_spans_in_one_verse", 0),
            ("max_green_spans_in_one_verse", 9000),
            ("raw_original_pdf_green_span_count", 10000),
            ("printed_verse_markers_checked", None),
            ("raw_original_green_spans_before_first_printed_verse", 9),
            ("unassigned_original_green_spans", 1),
            ("publication_status", "PUBLIC"),
            ("english_translation_automatically_verified", True),
            ("english_grammar_rules_automatically_applied", True),
            ("oshb_to_pdf_word_alignment_verified", True),
            ("source_pdf_book_prefix_vs_oshb_mapping_independently_verified", True),
            ("layout_requires_exception_review", False),
        )
        for name, value in cases:
            with self.subTest(field=name, value=value), self.assertRaises(CHES012MetricsError):
                changed = copy.deepcopy(base)
                changed[0][name] = value
                summarize_source_geometry(changed)

    def test_wrong_chapter_missing_duplicate_boolean_or_invalid_structure_fails(self):
        reports = fake_source_audits()
        for source in (
            reports[:13],
            reports + [reports[0]],
            [*reports[:-1], reports[0]],
            None,
            {},
        ):
            with self.subTest(source_type=str(type(source))), self.assertRaises(CHES012MetricsError):
                summarize_source_geometry(source)
        for key, value in (
            ("scope", "Gen.900"),
            ("checkpoint", "CHES-011"),
            ("source_pin_status", "DISCOVERY_ONLY_NOT_ENGINE_APPROVED"),
            ("source_pdf_sha256", True),
            ("authentic_oshb_verse_references_checked", True),
        ):
            with self.subTest(field=key), self.assertRaises(CHES012MetricsError):
                changed = copy.deepcopy(reports)
                changed[0][key] = value
                summarize_source_geometry(changed)

    def test_basis_point_rate_rejects_bad_denominator_or_noninteger(self):
        self.assertEqual(_rate_basis_points(0,359),0)
        self.assertEqual(_rate_basis_points(359,359),10000)
        for numerator, denominator in ((1, 0), (-1,359), (360,359),
                                       (False,10),(10,True),(1.5,10)):
            with self.subTest(pair=(numerator,denominator)), self.assertRaises(CHES012MetricsError):
                _rate_basis_points(numerator, denominator)

    def test_trusted_real_pdf_entry_requires_private_existing_directory_and_all_files(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            with self.assertRaises((ValueError, FileNotFoundError, OSError)):
                audit_fourteen_real_pdfs(home)
            with self.assertRaises(CHES012MetricsError):
                audit_fourteen_real_pdfs(home/"not-present")

    def test_metadata_reports_cannot_be_mistaken_for_verified_real_pdf_bytes(self):
        self.assertIs(summarize_source_geometry(fake_source_audits())[
            "real_original_pdf_bytes_reparsed_in_this_function"], False)


if __name__ == "__main__":
    unittest.main()
