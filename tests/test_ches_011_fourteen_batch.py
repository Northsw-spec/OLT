"""CHES-011: authentic-source registry and 10→14 private batch regression tests.

All English gloss strings in these tests are synthetic; real source English
is never stored in the repository, emitted to stdout or uploaded as an artifact.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from olt_core.sources import ROOT
from scripts.ches_010_pin_registry import (
    CHES010PinError, INDEXED_BATCH_ITEMS, NEXT_INDEXED_BATCH_ITEMS,
    read_indexed_source_pins, read_next_source_pins, pinned_record,
)
from scripts.ches_006_layout_metrics import PILOT
from scripts.ches_007_multichapter_english import NEW_ENGLISH_CHAPTERS
from scripts.ches_008_private_batch import (
    BATCH, EXTENDED_BATCH, INDEXED_BATCH, ALL_INDEXED_BATCH,
    CHESBatchError, STATE_FILE, run_private_chapter_batch,
)
from test_ches_009_six_source_batch import fake_generator, fake_pdf


class TestCHES011SourcePinnedFourteenChapterBatch(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.private = self.home / ".olt-private" / "english"

    def run_fake(self, **kwargs):
        with patch("scripts.ches_008_private_batch._verified_pdf", side_effect=fake_pdf), patch(
            "scripts.ches_008_private_batch._generate", side_effect=fake_generator
        ):
            return run_private_chapter_batch(self.home, self.private, **kwargs)

    def test_fourteen_original_source_records_preserve_all_previous_batch_scopes(self):
        old, extra = read_indexed_source_pins(), read_next_source_pins()
        self.assertEqual(len(old), 4)
        self.assertEqual(len(extra), 4)
        self.assertEqual(len(BATCH), 4)
        self.assertEqual(len(EXTENDED_BATCH), 6)
        self.assertEqual(len(INDEXED_BATCH), 10)
        self.assertEqual(len(ALL_INDEXED_BATCH), 14)
        self.assertEqual(ALL_INDEXED_BATCH[:10], INDEXED_BATCH)
        self.assertEqual(ALL_INDEXED_BATCH[10:], NEXT_INDEXED_BATCH_ITEMS)
        self.assertEqual(INDEXED_BATCH[6:], INDEXED_BATCH_ITEMS)
        self.assertEqual(
            [(row["original_book"], row["original_chapter"]) for row in extra],
            [("Gen", 7), ("Gen", 8), ("Exod", 5), ("Exod", 6)]
        )
        self.assertEqual(
            sum(row["printed_pdf_verses_confirmed_by_engineering"] for row in extra), 99
        )
        self.assertEqual(sum(row["oshb_original_word_tokens_observed"] for row in extra), 1363)
        self.assertEqual(sum(row["green_ches_pdf_spans_extracted"] for row in extra), 1766)
        for book, chapter in (("Gen", 7), ("Gen", 8), ("Exod", 5), ("Exod", 6)):
            with self.subTest(scope=f"{book}.{chapter}"):
                self.assertIn((book, chapter), NEW_ENGLISH_CHAPTERS)
                row = pinned_record(book, chapter)
                self.assertEqual(
                    PILOT[(book, chapter)],
                    (row["printed_pdf_verses_confirmed_by_engineering"],
                     "additional_indexed_original_source_pins")
                )
                for field in (
                    "independent_pdf_filename_to_oshb_book_mapping_verified",
                    "word_and_morpheme_alignment_verified",
                    "full_source_text_in_public_git_permitted",
                    "source_pdf_stored_in_public_repo",
                ):
                    self.assertIs(row[field], False)

    def test_preserved_ten_source_checkpoint_then_fourteen_and_repeat_skips(self):
        initial = self.run_fake(indexed=True)
        self.assertEqual((initial["built"], initial["skipped"], initial["failed"]), (10, 0, 0))
        self.assertTrue(initial["complete"])
        prior = json.loads((self.private / STATE_FILE).read_text(encoding="utf-8"))["chapters"]
        resumed = self.run_fake(all_indexed=True)
        self.assertEqual((resumed["built"], resumed["skipped"], resumed["failed"]), (4, 10, 0))
        self.assertTrue(resumed["complete"])
        self.assertEqual(resumed["completed_chapters_stored_private"], 14)
        repeated = self.run_fake(all_indexed=True)
        self.assertEqual((repeated["built"], repeated["skipped"], repeated["failed"]), (0, 14, 0))
        self.assertTrue(repeated["complete"])
        for mode, expected in (
            ({}, 4), ({"extended": True}, 6), ({"indexed": True}, 10)
        ):
            with self.subTest(mode=mode):
                prior_mode = self.run_fake(**mode)
                self.assertEqual((prior_mode["built"], prior_mode["skipped"], prior_mode["failed"]),
                                 (0, expected, 0))
                self.assertTrue(prior_mode["complete"])
        current = json.loads((self.private / STATE_FILE).read_text(encoding="utf-8"))["chapters"]
        self.assertEqual(len(current), 14)
        self.assertTrue(all(current[key] == value for key, value in prior.items()))
        self.assertNotIn("INVENTED-PRIVATE-ENGLISH", json.dumps(repeated))
        self.assertFalse(repeated["english_translation_owner_approved"])
        self.assertFalse(repeated["source_word_to_english_gloss_alignment_verified"])
        self.assertEqual(repeated["publication_status"], "BLOCKED")

    def test_one_failed_new_original_is_retryable_without_changing_first_ten(self):
        self.run_fake(indexed=True)
        def fail_one(directory, name, pin):
            if name == "ches-ex6.pdf":
                raise CHESBatchError("MISSING_OR_UNSAFE_SOURCE_PDF")
            return fake_pdf(directory, name, pin)
        with patch("scripts.ches_008_private_batch._verified_pdf",
                   side_effect=fail_one), patch(
            "scripts.ches_008_private_batch._generate", side_effect=fake_generator
        ):
            partial = run_private_chapter_batch(self.home, self.private, all_indexed=True)
        self.assertEqual((partial["built"], partial["skipped"], partial["failed"]), (3, 10, 1))
        self.assertFalse(partial["complete"])
        self.assertEqual(partial["failed_chapter_codes"],
                         [{"scope": "Exod.6", "code": "MISSING_OR_UNSAFE_SOURCE_PDF"}])
        repaired = self.run_fake(all_indexed=True)
        self.assertEqual((repaired["built"], repaired["skipped"], repaired["failed"]), (1, 13, 0))
        self.assertTrue(repaired["complete"])

    def test_false_mode_and_nonprivate_permission_are_rejected(self):
        for opts in (
            {"all_indexed": True, "indexed": True},
            {"all_indexed": True, "extended": True},
            {"all_indexed": "yes"},
            {"all_indexed": True, "limit": 15},
            {"indexed": True, "limit": 11},
            {"limit": 5},
        ):
            with self.subTest(opts=opts), self.assertRaises(CHESBatchError):
                run_private_chapter_batch(self.home, self.private, **opts)

    def test_new_source_pin_rights_redefinition_rejected(self):
        manifest = json.loads((ROOT / "data/engine/olt_ches_source_manifest.json").read_text())
        for k, value in (
            ("original_pdf_url", "https://untrusted.example/exo6.pdf"),
            ("source_pdf_sha256", "bad-hash"),
            ("full_source_text_in_public_git_permitted", True),
            ("word_and_morpheme_alignment_verified", True),
            ("original_chapter", True),
            ("raw_original_pdf_unassigned_green_spans", 1),
        ):
            with self.subTest(field=k), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "data/engine/olt_ches_source_manifest.json"
                target.parent.mkdir(parents=True)
                altered = copy.deepcopy(manifest)
                altered["additional_indexed_original_source_pins"][0][k] = value
                target.write_text(json.dumps(altered), encoding="utf-8")
                with self.assertRaises(CHES010PinError):
                    read_next_source_pins(Path(tmp))


if __name__ == "__main__":
    unittest.main()
