"""DANMEK-021 checks ONLY user-reported numerical evidence consistency.

This does not load private CHES text, certify original-language syntax,
or claim a GitHub Actions rerun of the real local case ledger.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = (ROOT / "data" / "observations" /
        "danmek_021_owner_reported_private_ambiguity_queue_20261101.json")


class TestDanMek021OwnerReportedPrivateQueue(unittest.TestCase):
    def test_owner_research_queue_metadata_reconciles_without_false_signoff(self):
        raw = PATH.read_text(encoding="utf-8")
        obj = json.loads(raw)
        self.assertEqual(
            obj["checkpoint"],
            "DANMEK-021-OWNER-REPORTED-PRIVATE-AMBIGUITY-QUEUE-2026-11-01",
        )
        self.assertEqual(
            obj["source_code_main_commit"],
            "c4c9303f3780e2b4a593618005a8294284b080f7",
        )
        opts = obj["private_command_mode"]
        self.assertIs(opts["confirm_machine_readable_use_permission"], True)
        self.assertIs(opts["require_311"], True)
        self.assertIs(opts["write_private_queue"], True)
        self.assertIs(opts["ylt_authority_enabled"], False)

        o = obj["observation"]
        self.assertEqual(o["source_verses_seen"], 23144)
        self.assertEqual(o["ambiguous_english_verses_queued"], 311)
        self.assertEqual(o["original_source_same_reference_candidates_unreviewed"], 311)
        self.assertEqual(o["original_source_reference_missing"], 0)
        self.assertEqual(o["english_reorders_applied"], 0)
        self.assertIs(o["original_language_subject_verified"], False)
        self.assertIs(o["original_source_word_alignment_verified"], False)
        self.assertIs(o["source_book_mapping_independently_verified"], False)
        self.assertIs(o["owner_verified_english_html_changed"], False)
        self.assertIs(o["private_source_json_modified"], False)
        self.assertIs(o["private_chapter_text_printed"], False)
        self.assertEqual(o["private_output_status"], "NEW_PRIVATE_QUEUE")
        self.assertEqual(o["publication_status"], "BLOCKED")
        self.assertIs(o["private_queue_snapshot_id_not_shared_in_repository"], True)

        by_prefix = obj["by_source_prefix_ambiguous_count"]
        self.assertEqual(len(by_prefix), 24)
        self.assertEqual(o["distinct_prefixes_with_ambiguities"], len(by_prefix))
        self.assertEqual(sum(by_prefix.values()), o["ambiguous_english_verses_queued"])
        self.assertEqual(sum(by_prefix[k] for k in (
            "1sa", "2sa", "gen", "exo", "1kg", "2kg",
        )), 196)
        self.assertTrue(all(type(count) is int and count > 0
                            for count in by_prefix.values()))

        limitations = obj["limitations"]
        self.assertIs(limitations["private_queue_created_by_owner"], True)
        self.assertIs(limitations["private_queue_available_to_github_ci"], False)
        self.assertIs(limitations["original_source_verse_numbers_matched"], True)
        self.assertIs(
            limitations["original_book_verse_crosswalk_independently_reviewed"], False,
        )
        self.assertIs(
            limitations["original_hebrew_aramaic_word_subject_alignment_verified"], False,
        )
        self.assertIs(limitations["ambiguities_automatically_resolved"], False)
        self.assertIs(limitations["owner_approved_html_unchanged"], True)
        self.assertIs(limitations["complete_english_bible_approved"], False)
        self.assertIs(limitations["public_redistribution_permitted"], False)

        for forbidden in ("/home/", "/.olt-private/", "source_ches_spans",
                          "private_ches_text", "original_script"):
            self.assertNotIn(forbidden, raw)


if __name__ == "__main__":
    unittest.main()
