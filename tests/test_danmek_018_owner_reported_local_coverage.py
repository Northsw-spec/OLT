"""DANMEK-018: ensure owner-reported metadata checkpoint is self-consistent.

This is a check of a *reported aggregate record*, NOT an independent test of
the user's private CHES archive or verification of original-language text.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT / "data" / "observations" /
    "danmek_018_owner_reported_gt_coverage_20261101.json"
)


class TestDanMek018OwnerReportedCoverage(unittest.TestCase):
    def test_owner_reported_metadata_reconciles_without_approval_leap(self):
        obj = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(
            obj["checkpoint"],
            "DANMEK-018-OWNER-REPORTED-LOCAL-OT-COVERAGE-2026-11-01",
        )
        self.assertEqual(
            obj["source_code_main_commit"],
            "156eab909426e86ae0ab56db1d513a4f8f03892b",
        )
        self.assertTrue(obj["command_mode"]["owner_approved_english_candidates"])
        self.assertTrue(obj["command_mode"]["display_faces"])
        self.assertFalse(obj["command_mode"]["optional_ylt_authority"])
        self.assertFalse(obj["command_mode"]["render_html"])

        a = obj["aggregate_reported"]
        rows = obj["per_source_filename_prefix"]
        self.assertEqual(len(rows), 39)
        self.assertEqual(a["source_filename_prefixes"], 39)
        self.assertEqual(a["chapters"], 929)
        self.assertEqual(a["verses"], 23144)
        self.assertEqual(a["source_english_fragments_not_verified_translation"], 401460)
        self.assertEqual(sum(x["chapters"] for x in rows), a["chapters"])
        self.assertEqual(sum(x["verses"] for x in rows), a["verses"])
        self.assertTrue(a["all_929_39_by_count_only"])
        self.assertTrue(a["all_prefixes_internal_chapter_gaps_zero"])
        self.assertEqual(
            a["owner_english_reorders_applied"]
            + a["ambiguous_english_reorders_left_unchanged"]
            + a["verses_without_english_order_candidate"],
            a["verses"],
        )
        self.assertEqual(a["owner_english_reorders_applied"], 2990)
        self.assertEqual(a["ambiguous_english_reorders_left_unchanged"], 311)
        self.assertEqual(a["lowercase_c_letters_hidden"], 9540)
        self.assertEqual(a["faces_simplifications"], 2)
        self.assertEqual(a["verses_with_one_or_more_display_edits"], 9368)
        self.assertLessEqual(a["verses_with_one_or_more_display_edits"], a["verses"])
        self.assertEqual(a["publication_status"], "BLOCKED")

        prefixes = [row["prefix"] for row in rows]
        self.assertEqual(prefixes, sorted(prefixes))
        self.assertEqual(len(prefixes), len(set(prefixes)))
        for row in rows:
            self.assertRegex(row["prefix"], r"\A[a-z0-9]{2,5}\Z")
            self.assertGreater(row["chapters"], 0)
            self.assertGreater(row["verses"], 0)
            self.assertEqual(row["internal_chapter_number_gaps"], 0)

        boundaries = obj["evidence_boundaries"]
        self.assertTrue(boundaries["local_runtime_executed_by_owner"])
        self.assertTrue(boundaries["source_chapter_counts_verified_by_report_only"])
        for key in (
            "real_private_source_index_membership_verified",
            "source_index_html_authenticity_independently_verified",
            "source_prefixes_independently_verified_as_biblical_book_ids",
            "each_verse_original_language_alignment_verified",
            "whole_english_olt_translation_complete",
            "full_corpus_translation_personally_approved",
            "permission_to_publish",
            "complete_private_reader_snapshot_id_supplied",
        ):
            self.assertIs(boundaries[key], False)

        # No raw source text, verse fragments, local paths or HTML
        # in the machine-readable public observation.
        text = EVIDENCE.read_text(encoding="utf-8")
        self.assertNotIn("<html", text.lower())
        self.assertNotIn("source_ches_spans_NOT_OLT_TRANSLATION", text)
        self.assertNotIn("/home/", text)
        self.assertNotIn("~/.olt-private", text)


if __name__ == "__main__":
    unittest.main()
