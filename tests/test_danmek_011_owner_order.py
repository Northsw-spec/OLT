"""DANMEK-011: owner-approved English ordering, synthetic data only."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.ches_015_direct_private_reader import (
    CHES015ReaderError, build_private_reader, main,
)
from scripts.danmek_011_owner_order import (
    apply_owner_approved_candidates, discover_candidates,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestOwnerApprovedEnglishOrder(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.folder = self.base / "ches"
        self.folder.mkdir(mode=0o700)
        doc = invented_chapter("gen", 1)
        first = doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
        first[0]["original_ches_line_text"] = "and·he-shaped"
        first.append({
            "page": 1, "pdf_x": 27, "pdf_y": 6.5,
            "original_ches_line_text": "God",
        })
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker the·work sur faces"
        doc["ches_pdf_green_spans"] = 3
        self.path = self.folder / "gen.1.json"
        write_private_json(doc, self.path)

    def test_owner_approved_batch_renders_without_individual_review_manifest(self):
        source_bytes = self.path.read_bytes()
        with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            faithful = build_private_reader(self.folder, render=True)
            result = build_private_reader(
                self.folder, render=True,
                olt_owner_approved_candidates=True, olt_display_faces=True,
            )
        self.assertNotEqual(faithful["snapshot_id"], result["snapshot_id"])
        self.assertEqual(result["mode"], "PRIVATE_OLT_ENGLISH_DISPLAY")
        self.assertEqual(result["olt_owner_approved_candidate_reorders_applied"], 2)
        self.assertEqual(result["olt_owner_candidate_ambiguous_verses_unchanged"], 0)
        self.assertEqual(result["olt_owner_candidate_ylt_conflicts_unchanged"], 0)
        self.assertEqual(result["olt_owner_candidate_other_verses_unchanged"], 0)
        self.assertFalse(result["olt_owner_candidate_original_language_subject_verified"])
        self.assertTrue(result["olt_owner_candidate_english_editorial_approval"])
        self.assertEqual(result["olt_display_sur_faces_to_faces_count"], 1)
        self.assertEqual(self.path.read_bytes(), source_bytes)
        root = self.base / "ches-direct-reader"
        before = (root / faithful["snapshot_id"] / "gen.1.html").read_text()
        after = (root / result["snapshot_id"] / "gen.1.html").read_text()
        self.assertIn('>and·he-shaped</span><span class="gloss">God</span>', before)
        self.assertIn('>and God — </span><span class="gloss">he-shaped</span>', after)
        self.assertNotIn("He-shaped", after)
        self.assertIn('>Worker — he-is-making the·work faces</span>', after)
        self.assertIn("sur faces", before)
        self.assertIn("NOT verify Biblical Hebrew", after)
        self.assertEqual(
            build_private_reader(
                self.folder, render=True,
                olt_owner_approved_candidates=True, olt_display_faces=True,
            )["snapshot_id"], result["snapshot_id"],
        )

    def test_ambiguous_cases_are_not_authorized_by_bulk_approval(self):
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker she-is-building Leader"
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "Without any candidate subject"
        write_private_json(doc, self.path)
        original_bytes = self.path.read_bytes()
        result = build_private_reader(
            self.folder, render=True, olt_owner_approved_candidates=True,
        )
        self.assertEqual(result["olt_owner_approved_candidate_reorders_applied"], 0)
        self.assertEqual(result["olt_owner_candidate_ambiguous_verses_unchanged"], 1)
        self.assertEqual(result["olt_owner_candidate_other_verses_unchanged"], 2)
        html_text = (self.base / "ches-direct-reader" /
                     result["snapshot_id"] / "gen.1.html").read_text()
        self.assertIn("he-is-making Worker she-is-building Leader", html_text)
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_overlapping_ylt_edit_is_left_unchanged_not_rewritten(self):
        edits = {("gen.1.1", 1): "and·he-recast"}
        stats = {
            "noun_changes": 1, "tense_changes": 0,
            "unmapped_verses_left_unchanged": 0,
            "ambiguous_verses_left_unchanged": 0,
        }
        with (
            patch("scripts.ches_015_direct_private_reader.load_private_ylt",
                  return_value=({}, "a" * 40)),
            patch("scripts.ches_015_direct_private_reader.propose_ylt_verse_overrides",
                  return_value=(edits, stats)),
        ):
            result = build_private_reader(
                self.folder, render=True, use_ylt_authority=True,
                olt_owner_approved_candidates=True,
            )
        self.assertEqual(result["olt_owner_approved_candidate_reorders_applied"], 1)
        self.assertEqual(result["olt_owner_candidate_ylt_conflicts_unchanged"], 1)
        page = (self.base / "ches-direct-reader" /
                result["snapshot_id"] / "gen.1.html").read_text()
        self.assertIn('>and·he-recast</span><span class="gloss">God</span>', page)
        self.assertIn("Worker — he-is-making", page)

    def test_owner_and_individually_reviewed_modes_cannot_be_mixed(self):
        with self.assertRaises(CHES015ReaderError):
            build_private_reader(
                self.folder, render=True,
                olt_subject_first=True,
                olt_owner_approved_candidates=True,
            )
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_owner_mode_still_has_explicit_no_grammar_certification(self):
        proposed, ambiguous = discover_candidates(
            "gen.1.1", "f" * 64, ["and·he-shaped", "God"],
        )
        self.assertEqual(len(proposed), 1)
        self.assertFalse(ambiguous)
        self.assertFalse(proposed[0]["source_syntax_reviewed"])
        rendered, reason = apply_owner_approved_candidates(
            reference="gen.1.1", chapter_sha256="f" * 64,
            original=["and·he-shaped", "God"],
            visible=["and·he-shaped", "God"],
        )
        self.assertEqual(reason, "APPLIED")
        self.assertEqual(rendered, ["and God — ", "he-shaped"])

    def test_metadata_only_cli_never_prints_private_words_and_no_files(self):
        with patch("sys.argv", [
            "reader",
            "--private-root", str(self.folder),
            "--confirm-machine-readable-use-permission",
            "--audit-only",
            "--olt-owner-approved-candidates",
            "--olt-display-faces",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["olt_owner_approved_candidate_reorders_applied"], 2)
        self.assertFalse(result["olt_owner_candidate_original_language_subject_verified"])
        self.assertNotIn("God", output.getvalue())
        self.assertNotIn("Worker", output.getvalue())
        self.assertNotIn(str(self.folder), output.getvalue())
        self.assertFalse((self.base / "ches-direct-reader").exists())


if __name__ == "__main__":
    unittest.main()
