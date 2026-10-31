"""CHES-014: offline private importer JSON bridge, synthetic glosses only.

Tests genuine pinned original Hebrew source records, NOT third-party CHES
payloads or original PDF bytes. No network dependency or source text logs.
"""
from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts.ches_006_layout_metrics import PILOT
from scripts.ches_008_private_batch import _source_pin
from scripts.ches_014_offline_english_bridge import (
    BOOK_TO_PREFIX, CHES014BridgeError, bridge_private_chapter, main,
)
from scripts.ches_import import write_private_json

ROOT = Path(__file__).resolve().parents[1]
ARTIFICIAL = "SYNTHETIC_ONLY_NOT_LICENSED_CONTENT"


def fake_archived_chapter(book: str, chapter: int) -> dict:
    pin_key = PILOT[(book, chapter)][1]
    pin = _source_pin(ROOT, pin_key, book, chapter)
    prefix = BOOK_TO_PREFIX[book]
    count = pin["printed_pdf_verses_confirmed_by_engineering"]
    total = pin["green_ches_pdf_spans_extracted"]
    count_per_verse, extra = divmod(total, count)
    rows = []
    for number in range(1, count + 1):
        fragment_count = count_per_verse + int(number <= extra)
        rows.append({
            "reference": f"{prefix}.{chapter}.{number}",
            "publication_status": "BLOCKED",
            "english_draft_status": "CHES_SOURCE_ONLY_UNALIGNED",
            "explicit_original_pdf_verse_anchor_page": 1,
            "explicit_original_pdf_verse_anchor_y": float(number * 8),
            "source_ches_spans_NOT_OLT_TRANSLATION": [
                {
                    "page": 1,
                    "pdf_x": float(75 + i),
                    "pdf_y": float(number * 8 + 2),
                    "original_ches_line_text": f"{ARTIFICIAL}-{number}-{i}",
                }
                for i in range(fragment_count)
            ],
        })
    return {
        "book": prefix,
        "chapter": chapter,
        "source_origin_url": pin["original_pdf_url"],
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "original_source_pdf_sha256": pin["source_pdf_sha256"],
        "source_original_index_sha256": "a" * 64,
        "source_pdf_byte_length": pin["source_pdf_bytes"],
        "source_pdf_page_count": pin["source_pdf_pages"],
        "verses_extracted": count,
        "ches_pdf_green_spans": total,
        "owner_attested_machine_readable_permission_no_public_distribution": True,
        "source_chapter_verse_count_independent_oshb_qa": "NOT_DONE",
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "independent_grammar_or_sense_approved": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }


class TestCHES014OfflineEnglishBridge(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.private = Path(scratch.name) / ".olt-private"
        self.private.mkdir(mode=0o700)
        self.chapters = self.private / "ches"
        self.chapters.mkdir(mode=0o700)
        self.output_dir = self.private / "olt-english-drafts"

    def write_source(self, book: str, chapter: int, doc=None) -> Path:
        prefix = BOOK_TO_PREFIX[book]
        target = self.chapters / f"{prefix}.{chapter}.json"
        write_private_json(doc if doc is not None else fake_archived_chapter(book, chapter), target)
        return target

    def test_all_fourteen_pinned_chapters_run_without_pdf_or_network(self):
        self.assertEqual(len(PILOT), 14)
        for book, chapter in sorted(PILOT):
            with self.subTest(chapter=(book, chapter)):
                self.write_source(book, chapter)
                with patch("urllib.request.urlopen", side_effect=AssertionError("NO NETWORK")):
                    report = bridge_private_chapter(
                        self.chapters, book=book, chapter=chapter
                    )
                pin = _source_pin(ROOT, PILOT[(book, chapter)][1], book, chapter)
                self.assertEqual(report["checkpoint"], "CHES-014")
                self.assertEqual(
                    report["original_oshb_verse_ids_checked"],
                    pin["printed_pdf_verses_confirmed_by_engineering"],
                )
                self.assertEqual(
                    report["original_pdf_green_text_spans_not_oshb_aligned"],
                    pin["green_ches_pdf_spans_extracted"],
                )
                self.assertFalse(report["original_pdf_bytes_rehashed_by_this_bridge"])
                self.assertFalse(report["original_source_index_membership_independently_reverified"])
                self.assertFalse(report["ches_to_oshb_word_alignment_verified"])
                self.assertFalse(report["english_grammar_rules_applied"])
                self.assertFalse(report["english_translation_owner_approved"])
                self.assertEqual(report["publication_status"], "BLOCKED")
                self.assertNotIn(ARTIFICIAL, json.dumps(report))
                self.assertNotIn(str(self.chapters), json.dumps(report))
                self.assertFalse(self.output_dir.exists())

    def test_private_write_and_exact_repeat_are_idempotent_and_source_immutable(self):
        source_path = self.write_source("Gen", 1)
        original = source_path.read_bytes()
        first = bridge_private_chapter(
            self.chapters, book="Gen", chapter=1, write_private=True
        )
        self.assertEqual(first["private_output_state"], "NEW_PRIVATE_UNAPPROVED_DRAFT_WRITTEN")
        draft_file = self.output_dir / "gen.1.unapproved-english.json"
        self.assertTrue(draft_file.is_file())
        self.assertEqual(self.output_dir.stat().st_mode & 0o777, 0o700)
        self.assertEqual(draft_file.stat().st_mode & 0o777, 0o600)
        draft = json.loads(draft_file.read_text(encoding="utf-8"))
        self.assertEqual(draft["offline_private_archive_bridge_checkpoint"], "CHES-014")
        self.assertFalse(draft["original_pdf_bytes_rehashed_by_offline_bridge"])
        self.assertFalse(draft["word_alignment_verified"])
        self.assertFalse(draft["english_translation_owner_approved"])
        self.assertFalse(draft["all_english_grammar_rules_applied"])
        self.assertEqual(draft["publication_status"], "BLOCKED")
        self.assertIn(ARTIFICIAL, draft["verses"][0]["english_text_private_unapproved"])
        second = bridge_private_chapter(
            self.chapters, book="Gen", chapter=1, write_private=True
        )
        self.assertEqual(second["private_output_state"], "EXISTING_IDENTICAL_PRIVATE_DRAFT_UNCHANGED")
        self.assertEqual(source_path.read_bytes(), original)

    def test_source_prefix_normalization_does_not_change_ches_input(self):
        source_path = self.write_source("Exod", 1)
        before = source_path.read_bytes()
        result = bridge_private_chapter(
            self.chapters, book="Exod", chapter=1, write_private=True
        )
        self.assertEqual(result["scope"], "Exod.1")
        draft = json.loads((self.output_dir / "exo.1.unapproved-english.json").read_text())
        self.assertEqual(draft["scope"], "Exod.1")
        self.assertEqual(draft["verses"][0]["reference"], "Exod.1.1")
        self.assertEqual(draft["verses"][0]["english_draft_status"], "UNREVIEWED_PRIVATE_ENGLISH_WORKING_DRAFT")
        self.assertEqual(source_path.read_bytes(), before)

    def test_wrong_original_pdf_metadata_license_and_verse_fail_closed(self):
        for key, value in [
            ("source_origin_url", "https://example.invalid/gen1.pdf"),
            ("original_source_pdf_sha256", "f"*64),
            ("source_pdf_byte_length", 5000),
            ("source_pdf_page_count", 2),
            ("ches_pdf_green_spans", 525),
            ("source_original_index_sha256", "NOT_HASH"),
            ("owner_attested_machine_readable_permission_no_public_distribution", False),
            ("alignment_with_oshb_words_verified", True),
            ("olt_english_translation_approved", True),
            ("publication_status", "PUBLIC"),
        ]:
            with self.subTest(field=key):
                doc = fake_archived_chapter("Gen", 1)
                doc[key] = value
                self.write_source("Gen", 1, doc)
                with self.assertRaises(ValueError):
                    bridge_private_chapter(self.chapters, book="Gen", chapter=1)
                self.assertFalse(self.output_dir.exists())
        doc = fake_archived_chapter("Gen", 1)
        doc["verses"][1]["reference"] = "gen.1.1"
        self.write_source("Gen", 1, doc)
        with self.assertRaises(CHES014BridgeError):
            bridge_private_chapter(self.chapters, book="Gen", chapter=1)

    def test_unknown_chapters_broad_permissions_and_symlink_refused(self):
        self.write_source("Gen", 1)
        for book, chapter in [("Gen", 99), ("Exod", 99), ("Ruth", 1)]:
            with self.subTest(book=book, chapter=chapter):
                with self.assertRaises(CHES014BridgeError):
                    bridge_private_chapter(self.chapters, book=book, chapter=chapter)
        path = self.chapters / "gen.1.json"
        path.chmod(0o644)
        with self.assertRaises(CHES014BridgeError):
            bridge_private_chapter(self.chapters, book="Gen", chapter=1)
        path.chmod(0o600)
        path.rename(self.chapters / "real-source.json")
        path.symlink_to(self.chapters / "real-source.json")
        with self.assertRaises(CHES014BridgeError):
            bridge_private_chapter(self.chapters, book="Gen", chapter=1)
        path.unlink()
        (self.chapters / "real-source.json").rename(path)
        self.chapters.chmod(0o755)
        with self.assertRaises(CHES014BridgeError):
            bridge_private_chapter(self.chapters, book="Gen", chapter=1)

    def test_existing_private_draft_must_not_be_overwritten(self):
        self.write_source("Gen", 1)
        bridge_private_chapter(self.chapters, book="Gen", chapter=1, write_private=True)
        path = self.output_dir / "gen.1.unapproved-english.json"
        path.write_text("PRESERVE_OWNER_EDITED_PRIVATE_DRAFT", encoding="utf-8")
        path.chmod(0o600)
        with self.assertRaisesRegex(CHES014BridgeError, "REFUSING_OVERWRITE"):
            bridge_private_chapter(self.chapters, book="Gen", chapter=1, write_private=True)
        self.assertEqual(path.read_text(), "PRESERVE_OWNER_EDITED_PRIVATE_DRAFT")

    def test_duplicate_key_and_nonfinite_json_fail_closed_without_private_text(self):
        target = self.chapters / "gen.1.json"
        for body in [
            '{"book":"gen","book":"gen"}',
            '{"book":"gen","chapter":NaN}',
            '{"raw":"'+ARTIFICIAL+'",',
        ]:
            with self.subTest(case=len(body)):
                target.write_text(body, encoding="utf-8")
                target.chmod(0o600)
                with self.assertRaises(CHES014BridgeError) as caught:
                    bridge_private_chapter(self.chapters, book="Gen", chapter=1)
                self.assertNotIn(ARTIFICIAL, str(caught.exception))
        self.assertFalse(self.output_dir.exists())

    def test_cli_only_prints_allowlisted_metadata_and_sanitizes_error(self):
        self.write_source("Gen", 1)
        with patch.object(sys, "argv", [
            "ches_014_offline_english_bridge.py",
            "--book", "Gen", "--chapter", "1",
            "--private-root", str(self.chapters),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
            self.assertEqual(json.loads(out.getvalue())["publication_status"], "BLOCKED")
            self.assertNotIn(ARTIFICIAL, out.getvalue())
            self.assertNotIn(str(self.chapters), out.getvalue())
        bad = self.chapters / "gen.1.json"
        bad.write_text('{"source":"'+ARTIFICIAL+'"}', encoding="utf-8")
        bad.chmod(0o600)
        with patch.object(sys, "argv", [
            "ches_014_offline_english_bridge.py",
            "--book", "Gen", "--chapter", "1",
            "--private-root", str(self.chapters),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            err = io.StringIO()
            with redirect_stderr(err), self.assertRaises(SystemExit) as caught:
                main()
            self.assertEqual(caught.exception.code, 2)
            self.assertNotIn(ARTIFICIAL, err.getvalue())
            self.assertNotIn(str(self.chapters), err.getvalue())


if __name__ == "__main__":
    unittest.main()
