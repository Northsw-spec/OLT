"""DANMEK-023 verifies only owner-reported numeric provenance consistency.

No copyrighted private CHES text or Hebrew word data is used. This test
cannot independently authenticate the actual owner's private files.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT / "data" / "observations" /
    "danmek_023_owner_reported_311_case_automated_triage_20261101.json"
)


class TestDanMek023OwnerRunPrivateTriage(unittest.TestCase):
    def test_report_counts_and_no_false_approval(self):
        raw = EVIDENCE.read_text(encoding="utf-8")
        obj = json.loads(raw)
        self.assertEqual(
            obj["checkpoint"],
            "DANMEK-023-OWNER-REPORTED-REAL-PRIVATE-AUTOMATED-TRIAGE-2026-11-01",
        )
        self.assertEqual(
            obj["observed_code_main_commit"],
            "85f61f963203fb0bd067da21e8d58f1503a4228f",
        )
        command = obj["private_command"]
        self.assertEqual(
            command["module"], "scripts.danmek_022_private_automated_triage",
        )
        self.assertIs(command["require_311"], True)
        self.assertIs(command["write_private_html"], True)

        r = obj["aggregate"]
        self.assertEqual(r["ambiguous_cases_rechecked"], 311)
        self.assertEqual(
            r["source_reference_candidates_present_unaligned"],
            r["ambiguous_cases_rechecked"],
        )
        self.assertEqual(r["missing_original_reference_cases"], 0)
        self.assertEqual(
            r["raw_original_verb_morphology_tag_hints_unreviewed"], 701,
        )
        self.assertEqual(r["grammatical_subjects_verified"], 0)
        self.assertEqual(r["english_editorial_changes_applied"], 0)
        self.assertEqual(r["distinct_source_prefixes_with_cases"], 24)
        self.assertEqual(
            r["private_review_html_status"], "NEW_PRIVATE_QUEUE",
        )
        self.assertEqual(r["publication_status"], "BLOCKED")
        for key in (
            "candidate_original_book_mapping_verified",
            "original_word_subject_alignment_verified",
            "owner_verified_html_modified",
            "private_original_files_modified",
            "private_text_printed",
        ):
            self.assertIs(r[key], False, key)
        self.assertIs(r["all_cases_still_require_evidence_review"], True)
        counts = obj["by_source_prefix_ambiguous_count"]
        self.assertEqual(len(counts), 24)
        self.assertEqual(sum(counts.values()), 311)
        self.assertTrue(all(type(v) is int and v > 0 for v in counts.values()))
        self.assertEqual(
            sum(counts[k] for k in (
                "1sa", "2sa", "gen", "exo", "1kg", "2kg",
            )), 196,
        )

        bounds = obj["evidence_boundaries"]
        for key in (
            "owner_executed_private_triage",
            "owner_generated_private_html",
            "original_source_verb_codes_are_hints_only",
        ):
            self.assertIs(bounds[key], True)
        for key in (
            "private_html_inspected_by_assistant",
            "private_html_uploaded_to_github",
            "private_original_language_verse_contents_reviewed_by_assistant",
            "original_subjects_linguistically_certified",
            "automated_english_edits_authorized",
            "whole_english_olt_translation_approved",
            "public_redistribution_rights_verified",
        ):
            self.assertIs(bounds[key], False)
        for forbidden in (
            "/home/", ".olt-private/", "source_ches_spans",
            "private_ches_text", "original_script",
            "snapshot-649183af75b671393494",
        ):
            self.assertNotIn(forbidden, raw)


if __name__ == "__main__":
    unittest.main()
