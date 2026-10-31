"""CHES-009: six-source resumed private batch, backward-compatible four source mode.

Only invented English source strings are placed in tests. Hebrew source IDs,
verse inventories, lexical markers and PDF hashes come from pinned metadata.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from olt_core.english_drafts import verified_wayyiqtol
from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_006_layout_metrics import PILOT
from scripts.ches_007_multichapter_english import NEW_ENGLISH_CHAPTERS
from scripts.ches_008_private_batch import (
    BATCH, EXTENDED_BATCH, INDEXED_BATCH, CHESBatchError, STATE_FILE,
    _report_contract, run_private_chapter_batch,
)

MANIFEST = json.loads(
    (ROOT / "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8")
)


def synthetic_private_report(book: str, chapter: int) -> dict:
    _, _, _, source_key = next(
        item for item in INDEXED_BATCH if item[:2] == (book, chapter)
    )
    pin = MANIFEST[source_key]
    source = load_ot_book(book, ROOT, read_provenance(ROOT))
    originals = [
        v for v in source["verses"]
        if v["reference"].startswith(f"{book}.{chapter}.")
    ]
    assert len(originals) == pin["printed_pdf_verses_confirmed_by_engineering"]
    count = len(originals)
    fragment_total = pin["green_ches_pdf_spans_extracted"]
    per_verse, extra = divmod(fragment_total, count)
    rows = []
    tenses = 0
    for index, original in enumerate(originals):
        words = original["words"]
        raw = f"INVENTED-PRIVATE-ENGLISH-GLOSS-{book}.{chapter}.{index+1}"
        source_rules = [
            {"original_token_id": word["source_id"], "english_rule": "ENGLISH_SIMPLE_PAST_REQUIRED"}
            for word in words if verified_wayyiqtol(word["morph_raw"])
        ]
        tenses += len(source_rules)
        row = {
            "reference": original["reference"],
            "original_source_word_token_ids": [w["source_id"] for w in words],
            "original_source_word_count": len(words),
            "private_original_ches_green_span_count": per_verse + int(index < extra),
            "ches_raw_gloss_stream_private_unapproved": raw,
            "english_text_private_unapproved": raw,
            "english_text_origin": "MECHANICAL_CHES_SOURCE_GLOSS_STREAM_NOT_OLT_TRANSLATION",
            "editorial_evidence_note_private": None,
            "source_tagged_wayyiqtol_requirements": source_rules,
            "original_source_lexical_override_candidates": [],
            "all_source_grammar_rules_applied": False,
            "english_owner_approved": False,
            "english_draft_status": "UNREVIEWED_PRIVATE_ENGLISH_WORKING_DRAFT",
            "publication_status": "BLOCKED",
        }
        if (book, chapter) == ("Gen", 1):
            row["word_alignment_verified"] = False
        else:
            row["oshb_to_ches_word_alignment_verified"] = False
        rows.append(row)
    is_legacy_gen = (book, chapter) == ("Gen", 1)
    result = {
        "checkpoint": "CHES-004" if is_legacy_gen else "CHES-007",
        "scope": "Gen.1_ONLY" if is_legacy_gen else f"{book}.{chapter}",
        "source_pdf_sha256": pin["source_pdf_sha256"],
        "english_language_only": True,
        "private_copyrighted_source_text": True,
        "genesis_verse_count" if is_legacy_gen else "verse_count": count,
        "original_hebrew_token_count": sum(len(v["words"]) for v in originals),
        "original_ches_pdf_green_span_count": fragment_total,
        "source_wayyiqtol_simple_past_requirements": tenses,
        "owner_lexical_override_candidates_not_applied": 0,
        "private_editorial_verse_edits_unapproved": 0,
        "word_alignment_verified": False,
        "all_english_grammar_rules_applied": False,
        "old_full_lexical_engine_required": False,
        "english_translation_owner_approved": False,
        "complete_english_bible_owner_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }
    _report_contract(result, book=book, chapter=chapter, pin=pin, root=ROOT)
    return result


def fake_pdf(_folder: Path, filename: str, _pin: dict) -> bytes:
    return ("FAKE-PDF-NOT-LICENSED-DATA-" + filename).encode("ascii")


def fake_generator(book: str, chapter: int, _data: bytes, _root: Path) -> dict:
    return synthetic_private_report(book, chapter)


class TestCHES009BackwardCompatibleSixSourcePrivateBatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.out = self.base / ".olt-private" / "ches" / "batch"

    def run_fake(self, *, extended=False, limit=None):
        opts = {"extended": extended}
        if limit is not None:
            opts["limit"] = limit
        with patch("scripts.ches_008_private_batch._verified_pdf", side_effect=fake_pdf), patch(
            "scripts.ches_008_private_batch._generate", side_effect=fake_generator
        ):
            return run_private_chapter_batch(self.base, self.out, **opts)

    def test_existing_four_chapter_checkpoint_migrates_to_six_without_changes(self):
        self.assertEqual(len(BATCH), 4)
        self.assertEqual(len(EXTENDED_BATCH), 6)
        self.assertEqual(EXTENDED_BATCH[:4], BATCH)
        first = self.run_fake()
        self.assertEqual((first["built"], first["skipped"], first["failed"]), (4, 0, 0))
        self.assertTrue(first["complete"])
        state = json.loads((self.out / STATE_FILE).read_text(encoding="utf-8"))
        old_record = copy.deepcopy(state["chapters"]["Gen.1"])
        resumed = self.run_fake(extended=True, limit=6)
        self.assertEqual((resumed["built"], resumed["skipped"], resumed["failed"]), (2, 4, 0))
        self.assertTrue(resumed["complete"])
        self.assertEqual(resumed["total_supported_pinned_chapters"], 6)
        self.assertEqual(resumed["completed_chapters_stored_private"], 6)
        again = self.run_fake(extended=True, limit=6)
        self.assertEqual((again["built"], again["skipped"], again["failed"]), (0, 6, 0))
        self.assertTrue(again["complete"])
        old_mode = self.run_fake()
        self.assertEqual((old_mode["built"], old_mode["skipped"]), (0, 4))
        self.assertEqual(old_mode["total_supported_pinned_chapters"], 4)
        self.assertTrue(old_mode["complete"])
        updated = json.loads((self.out / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(updated["chapters"]["Gen.1"], old_record)
        self.assertEqual(len(updated["chapters"]), 6)
        self.assertNotIn("INVENTED-PRIVATE-ENGLISH", json.dumps(resumed))
        self.assertFalse(resumed["source_word_to_english_gloss_alignment_verified"])
        self.assertEqual(resumed["publication_status"], "BLOCKED")

    def test_only_authentic_pinned_new_originals_and_verse_inventories_are_supported(self):
        for book, chapter, total_verses, words, green, name in (
            ("Gen", 4, 26, 341, 418, "fifth_chapter_layout_source_reference"),
            ("Exod", 2, 25, 340, 432, "sixth_chapter_layout_source_reference"),
        ):
            with self.subTest(scope=f"{book}.{chapter}"):
                self.assertIn((book, chapter), NEW_ENGLISH_CHAPTERS)
                self.assertEqual(PILOT[(book, chapter)], (total_verses, name))
                report = synthetic_private_report(book, chapter)
                self.assertEqual(report["original_hebrew_token_count"], words)
                self.assertEqual(report["original_ches_pdf_green_span_count"], green)
                self.assertFalse(report["english_translation_owner_approved"])
                self.assertEqual(report["publication_status"], "BLOCKED")
                pin = MANIFEST[name]
                for tamper in (
                    lambda obj: obj.update(publication_status="PUBLIC"),
                    lambda obj: obj.update(english_translation_owner_approved=True),
                    lambda obj: obj.update(word_alignment_verified=True),
                    lambda obj: obj["verses"][0]["original_source_word_token_ids"].__setitem__(0, "INVALID"),
                ):
                    with self.assertRaises(CHESBatchError):
                        bad = copy.deepcopy(report)
                        tamper(bad)
                        _report_contract(bad, book=book, chapter=chapter, pin=pin, root=ROOT)

    def test_missing_sixth_source_is_a_retryable_failure_while_four_remain_intact(self):
        self.run_fake()
        def missing(_folder, filename, pin):
            if filename == "ches-ex2.pdf":
                raise CHESBatchError("MISSING_OR_UNSAFE_SOURCE_PDF")
            return fake_pdf(_folder, filename, pin)
        with patch("scripts.ches_008_private_batch._verified_pdf", side_effect=missing), patch(
            "scripts.ches_008_private_batch._generate", side_effect=fake_generator
        ):
            result = run_private_chapter_batch(self.base, self.out, limit=6, extended=True)
        self.assertEqual(result["built"], 1)
        self.assertEqual(result["skipped"], 4)
        self.assertEqual(result["failed"], 1)
        self.assertFalse(result["complete"])
        self.assertEqual(result["failed_chapter_codes"], [
            {"scope": "Exod.2", "code": "MISSING_OR_UNSAFE_SOURCE_PDF"}
        ])
        rest = self.run_fake(extended=True, limit=6)
        self.assertEqual((rest["built"], rest["skipped"], rest["failed"]), (1, 5, 0))
        self.assertTrue(rest["complete"])

    def test_bounds_and_bad_mode_flags_rejected(self):
        for args in [
            {"extended": True, "limit": 7},
            {"extended": False, "limit": 5},
            {"extended": "yes", "limit": 4},
        ]:
            with self.subTest(args=args), self.assertRaises(CHESBatchError):
                run_private_chapter_batch(self.base, self.out, **args)


if __name__ == "__main__":
    unittest.main()
