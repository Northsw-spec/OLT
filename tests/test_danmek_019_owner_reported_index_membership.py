"""DANMEK-019: consistency of owner-reported local index membership evidence.

Synthetic repository consistency test only; no private CHES/index data
and no original-language or full-Bible certification is inferred.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT / "data/observations" /
    "danmek_019_owner_reported_index_membership_20261101.json"
)


class TestDanMek019OwnerReportedIndexMembership(unittest.TestCase):
    def test_record_is_consistent_and_does_not_claim_translation_certification(self):
        report = json.loads(RECORD.read_text(encoding="utf-8"))
        self.assertEqual(
            report["checkpoint"],
            "DANMEK-019-OWNER-REPORTED-PRIVATE-INDEX-MEMBERSHIP-2026-11-01",
        )
        self.assertEqual(
            report["local_code_revision"],
            "bb7e50aeaf602a4af98ba9df8bb28a84bd3d1bb3",
        )
        self.assertEqual(report["parsed_index_chapter_links"], 929)
        self.assertEqual(report["parsed_index_filename_prefixes"], 39)
        self.assertEqual(report["private_imported_chapter_files"], 929)
        self.assertEqual(report["missing_index_chapter_ids_locally"], 0)
        for key in (
            "upstream_index_fetched_by_owner_in_parrot",
            "upstream_url_redirect_rejected_by_owner_script",
            "index_sha256_matches_recorded_private_import",
            "all_local_chapter_ids_found_in_supplied_index",
            "all_local_chapter_embedded_index_hashes_match",
            "all_source_index_chapters_present_in_private_archive",
            "verified_with_danmek_017_require_index_complete",
            "source_index_bytes_saved_privately_when_matched",
            "locked_owner_verified_reader_preserved",
        ):
            self.assertIs(report[key], True, key)
        for key in (
            "downloaded_index_actual_sha256_value_shared",
            "original_private_chapter_json_modified",
            "private_source_text_uploaded_to_public_repository",
            "independent_original_pdf_bytes_authenticated",
            "source_prefixes_philologically_mapped_to_canonical_book_ids",
            "word_by_word_hebrew_english_alignment_verified",
            "complete_english_olt_translation_verified",
            "public_redistribution_rights_confirmed",
        ):
            self.assertIs(report[key], False, key)
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertEqual(
            set(report),
            {
                "checkpoint", "evidence", "source_repository",
                "local_code_revision", "upstream_source_index_url",
                "upstream_index_fetched_by_owner_in_parrot",
                "upstream_url_redirect_rejected_by_owner_script",
                "downloaded_index_actual_sha256_value_shared",
                "index_sha256_matches_recorded_private_import",
                "parsed_index_chapter_links", "parsed_index_filename_prefixes",
                "private_imported_chapter_files",
                "missing_index_chapter_ids_locally",
                "all_local_chapter_ids_found_in_supplied_index",
                "all_local_chapter_embedded_index_hashes_match",
                "all_source_index_chapters_present_in_private_archive",
                "verified_with_danmek_017_require_index_complete",
                "original_private_chapter_json_modified",
                "source_index_bytes_saved_privately_when_matched",
                "private_source_text_uploaded_to_public_repository",
                "independent_original_pdf_bytes_authenticated",
                "source_prefixes_philologically_mapped_to_canonical_book_ids",
                "word_by_word_hebrew_english_alignment_verified",
                "complete_english_olt_translation_verified",
                "public_redistribution_rights_confirmed",
                "publication_status", "locked_owner_verified_reader_preserved",
            },
        )
        self.assertNotIn("source_ches_spans_NOT_OLT_TRANSLATION", RECORD.read_text())
        self.assertNotIn("/home/", RECORD.read_text())


if __name__ == "__main__":
    unittest.main()
