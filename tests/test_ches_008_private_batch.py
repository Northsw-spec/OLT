"""CHES-008: private resume, interruption recovery, integrity and failure tests.

All glosses below are invented. Original source tokens come from pinned OSHB;
no third-party copyrighted English CHES text or original PDFs are committed.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from olt_core.english_drafts import verified_wayyiqtol
from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_008_private_batch import (
    BATCH, CHESBatchError, STATE_FILE, _canonical_bytes,
    _output_name, _record, _report_contract, _verified_pdf,
    run_private_chapter_batch,
)
from scripts.ches_import import write_private_json

MANIFEST = json.loads(
    (ROOT / "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8")
)


def fake_approved_never(book: str, chapter: int) -> dict:
    match = next((item for item in BATCH if item[:2] == (book, chapter)))
    _, _, _, pin_key = match
    pin = MANIFEST[pin_key]
    source = load_ot_book(book, ROOT, read_provenance(ROOT))
    original = [v for v in source["verses"]
                if v["reference"].startswith(f"{book}.{chapter}.")]
    count = pin["printed_pdf_verses_confirmed_by_engineering"]
    assert len(original) == count
    total = pin["green_ches_pdf_spans_extracted"]
    whole, remainder = divmod(total, count)
    verses = []
    tense_count = 0
    for index, verse in enumerate(original):
        ref = verse["reference"]
        original_ids = [w["source_id"] for w in verse["words"]]
        tense = [
            {"original_token_id": w["source_id"],
             "english_rule": "ENGLISH_SIMPLE_PAST_REQUIRED"}
            for w in verse["words"] if verified_wayyiqtol(w["morph_raw"])
        ]
        tense_count += len(tense)
        private_fake_text = f"FAKE-PRIVATE-ENGLISH-SOURCE-{ref}"
        row = {
            "reference": ref,
            "original_source_word_token_ids": original_ids,
            "original_source_word_count": len(original_ids),
            "private_original_ches_green_span_count": whole + int(index < remainder),
            "ches_raw_gloss_stream_private_unapproved": private_fake_text,
            "english_text_private_unapproved": private_fake_text,
            "english_text_origin": "MECHANICAL_CHES_SOURCE_GLOSS_STREAM_NOT_OLT_TRANSLATION",
            "editorial_evidence_note_private": None,
            "source_tagged_wayyiqtol_requirements": tense,
            "original_source_lexical_override_candidates": [],
            "english_owner_approved": False,
            "all_source_grammar_rules_applied": False,
            "english_draft_status": "UNREVIEWED_PRIVATE_ENGLISH_WORKING_DRAFT",
            "publication_status": "BLOCKED",
        }
        if (book, chapter) == ("Gen", 1):
            row["word_alignment_verified"] = False
        else:
            row["oshb_to_ches_word_alignment_verified"] = False
        verses.append(row)
    report = {
        "checkpoint": "CHES-004" if (book, chapter) == ("Gen", 1) else "CHES-007",
        "scope": "Gen.1_ONLY" if (book, chapter) == ("Gen", 1) else f"{book}.{chapter}",
        "source_pdf_sha256": pin["source_pdf_sha256"],
        "english_language_only": True,
        "private_copyrighted_source_text": True,
        "genesis_verse_count" if (book, chapter) == ("Gen", 1) else "verse_count": count,
        "original_hebrew_token_count": sum(len(v["words"]) for v in original),
        "original_ches_pdf_green_span_count": total,
        "source_wayyiqtol_simple_past_requirements": tense_count,
        "owner_lexical_override_candidates_not_applied": 0,
        "private_editorial_verse_edits_unapproved": 0,
        "word_alignment_verified": False,
        "all_english_grammar_rules_applied": False,
        "old_full_lexical_engine_required": False,
        "english_translation_owner_approved": False,
        "complete_english_bible_owner_approved": False,
        "publication_status": "BLOCKED",
        "verses": verses,
    }
    _report_contract(report, book=book, chapter=chapter, pin=pin, root=ROOT)
    return report


def fake_pdf_loader(_directory: Path, filename: str, pin: dict) -> bytes:
    return ("FAKE-PDF-FOR-TEST-ONLY-" + filename).encode("ascii")


def fake_generator(book: str, chapter: int, _data: bytes, _root: Path) -> dict:
    return fake_approved_never(book, chapter)


class TestCHES008ResumablePrivateEnglishBatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.output = self.directory / ".olt-private" / "ches" / "batch"
        self.assertFalse(self.output.exists())

    def run_fake_batch(self, limit=4):
        with patch("scripts.ches_008_private_batch._verified_pdf",
                   side_effect=fake_pdf_loader), patch(
                   "scripts.ches_008_private_batch._generate",
                   side_effect=fake_generator):
            return run_private_chapter_batch(
                self.directory, self.output, limit=limit
            )

    def test_two_chapters_then_resume_four_then_skip_all(self):
        first = self.run_fake_batch(limit=2)
        self.assertEqual(first["built"], 2)
        self.assertEqual(first["skipped"], 0)
        self.assertEqual(first["recovered"], 0)
        self.assertEqual(first["failed"], 0)
        self.assertEqual(first["completed_chapters_stored_private"], 2)
        self.assertFalse(first["complete"])
        self.assertTrue((self.output / STATE_FILE).is_file())
        self.assertEqual((self.output / STATE_FILE).stat().st_mode & 0o777, 0o600)
        second = self.run_fake_batch(limit=4)
        self.assertEqual(second["built"], 2)
        self.assertEqual(second["skipped"], 2)
        self.assertEqual(second["completed_chapters_stored_private"], 4)
        self.assertTrue(second["complete"])
        outputs = [self.output / _output_name(book, chapter) for book, chapter, _, _ in BATCH]
        hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in outputs]
        for file in outputs:
            self.assertEqual(file.stat().st_mode & 0o777, 0o600)
            self.assertIn("FAKE-PRIVATE-ENGLISH", file.read_text(encoding="utf-8"))
        third = self.run_fake_batch()
        self.assertEqual(third["built"], 0)
        self.assertEqual(third["skipped"], 4)
        self.assertEqual(third["failed"], 0)
        self.assertTrue(third["complete"])
        self.assertEqual(hashes, [hashlib.sha256(f.read_bytes()).hexdigest() for f in outputs])
        self.assertNotIn("FAKE-PRIVATE-ENGLISH", json.dumps(third))
        self.assertFalse(third["english_translation_owner_approved"])
        self.assertEqual(third["publication_status"], "BLOCKED")

    def test_failed_chapter_does_not_erase_completed_and_retries_next_run(self):
        def flaky(_dir, filename, _pin):
            if filename == "ches-gen2.pdf":
                raise CHESBatchError("MISSING_OR_UNSAFE_SOURCE_PDF")
            return fake_pdf_loader(_dir, filename, _pin)

        with patch("scripts.ches_008_private_batch._verified_pdf",
                   side_effect=flaky), patch(
                   "scripts.ches_008_private_batch._generate",
                   side_effect=fake_generator):
            failed = run_private_chapter_batch(self.directory, self.output)
        self.assertEqual(failed["built"], 3)
        self.assertEqual(failed["failed"], 1)
        self.assertFalse(failed["complete"])
        self.assertEqual(failed["failed_chapter_codes"], [{
            "scope": "Gen.2", "code": "MISSING_OR_UNSAFE_SOURCE_PDF"
        }])
        state = json.loads((self.output / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(len(state["chapters"]), 3)
        self.assertIn("Gen.2", state["failures"])
        resumed = self.run_fake_batch()
        self.assertEqual(resumed["built"], 1)
        self.assertEqual(resumed["skipped"], 3)
        self.assertEqual(resumed["failed"], 0)
        self.assertEqual(resumed["failed_chapter_codes"], [])
        self.assertTrue(resumed["complete"])
        state = json.loads((self.output / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(state["failures"], {})

    def test_orphan_private_output_is_adopted_only_if_rebuilt_byte_identical(self):
        self.output.mkdir(parents=True, exist_ok=True)
        original = fake_approved_never("Gen", 1)
        output = self.output / _output_name("Gen", 1)
        write_private_json(original, output)
        self.assertFalse((self.output / STATE_FILE).exists())
        recovered = self.run_fake_batch(limit=1)
        self.assertEqual(recovered["recovered"], 1)
        self.assertEqual(recovered["built"], 0)
        self.assertEqual(recovered["skipped"], 0)
        self.assertEqual(recovered["failed"], 0)
        state = json.loads((self.output / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(state["chapters"]["Gen.1"]["output_sha256"],
                         hashlib.sha256(output.read_bytes()).hexdigest())

    def test_mutated_private_output_not_overwritten_and_false_approval_rejected(self):
        ok = self.run_fake_batch(limit=1)
        self.assertEqual(ok["built"], 1)
        file = self.output / _output_name("Gen", 1)
        changed = json.loads(file.read_text(encoding="utf-8"))
        changed["verses"][0]["english_text_private_unapproved"] = "tampered private English"
        write_private_json(changed, file)
        before = file.read_bytes()
        failed = self.run_fake_batch(limit=1)
        self.assertEqual(failed["failed"], 1)
        self.assertEqual(failed["skipped"], 0)
        self.assertEqual(failed["failed_chapter_codes"][0]["code"],
                         "PRIVATE_DRAFT_UNVERIFIED")
        self.assertEqual(file.read_bytes(), before)
        # State must not erase the earlier successful snapshot on failure.
        state = json.loads((self.output / STATE_FILE).read_text(encoding="utf-8"))
        self.assertIn("Gen.1", state["chapters"])
        self.assertIn("Gen.1", state["failures"])

    def test_fake_owner_approval_and_original_word_id_never_pass_source_contract(self):
        report = fake_approved_never("Gen", 2)
        pin = MANIFEST["additional_chapter_layout_source_reference"]
        for category, tamper in [
            ("owner_approved", lambda a: a.update(english_translation_owner_approved=True)),
            ("Bible_complete", lambda a: a.update(complete_english_bible_owner_approved=True)),
            ("public", lambda a: a.update(publication_status="PUBLIC")),
            ("word_link_certified", lambda a: a.update(word_alignment_verified=True)),
            ("manual_edit", lambda a: a["verses"][0].update(
                english_text_origin="EXPLICIT_PRIVATE_EDITORIAL_VERSE_EDIT_UNAPPROVED")),
            ("false_original_token", lambda a: a["verses"][0][
                "original_source_word_token_ids"].__setitem__(0, "NOT-REAL")),
            ("false_source_word_alignment", lambda a: a["verses"][0].update(
                oshb_to_ches_word_alignment_verified=True)),
        ]:
            with self.subTest(category=category), self.assertRaises(CHESBatchError):
                test = copy.deepcopy(report)
                tamper(test)
                _report_contract(test, book="Gen", chapter=2, pin=pin, root=ROOT)

    def test_cannot_write_outside_private_and_private_state_corruption_is_not_reset(self):
        with self.assertRaises(ValueError):
            run_private_chapter_batch(self.directory, self.directory / "public", limit=1)
        with self.assertRaises(CHESBatchError):
            run_private_chapter_batch(self.directory, self.output, limit=0)
        self.output.mkdir(parents=True, exist_ok=True)
        state = self.output / STATE_FILE
        state.write_text('{"publication_status":"PUBLIC"}', encoding="utf-8")
        with self.assertRaises(CHESBatchError):
            self.run_fake_batch()
        self.assertEqual(state.read_text(encoding="utf-8"), '{"publication_status":"PUBLIC"}')

    def test_strict_original_pdf_size_and_sha_pin_even_on_resume(self):
        pdf = self.directory / "ches-gen1.pdf"
        original = b"%PDF-fake-private-test-payload"
        pin = {"source_pdf_bytes": len(original),
               "source_pdf_sha256": hashlib.sha256(original).hexdigest()}
        pdf.write_bytes(original)
        self.assertEqual(_verified_pdf(self.directory, "ches-gen1.pdf", pin), original)
        pdf.write_bytes(b"%PDF-corrupt-private-test-payload")
        with self.assertRaises(CHESBatchError):
            _verified_pdf(self.directory, "ches-gen1.pdf", pin)
        pdf.unlink()
        with self.assertRaises(CHESBatchError):
            _verified_pdf(self.directory, "ches-gen1.pdf", pin)


if __name__ == "__main__":
    unittest.main()
