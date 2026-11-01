"""DANMEK-035 structural, not name-hardcoded, English role-order tests.

All person names/verse contexts in fixtures are invented English examples.
No licensed CHES verse may be uploaded to public GitHub or Actions.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.ches_015_direct_private_reader import build_private_reader
from scripts.danmek_035_structural_english_order import (
    DanMek035Error, RULE_MARKED_GENERATING,
    analyze_structural_english_order, reorder_structurally_supported_subjects,
    build_private_structural_english_reader, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek035CorpusWideEnglishStructure(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.base = Path(t.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)
        self.example = "and·he-is- generating Rowan » Micah"
        self.other = "and·he-is- seeing Sailors » Others"
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.example
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.other
        write_private_json(doc, self.source / "gen.1.json")
        self.oldbytes = (self.source / "gen.1.json").read_bytes()
        self.baseline = build_private_reader(
            self.source, render=False,
            olt_display_faces=True, olt_owner_approved_candidates=True,
        )

    def test_owner_structure_is_not_person_name_specific(self):
        for input_english, expected in (
            ("and·he-is- generating Rowan » Micah",
             "and Rowan ·he-is- generating » Micah"),
            ("and·he-is- generating Natan » Oren",
             "and Natan ·he-is- generating » Oren"),
            ("and·she-is- generating Mira » Talia",
             "and Mira ·she-is- generating » Talia"),
            ("And·he-is- generating Xander » Jorin",
             "And Xander ·he-is- generating » Jorin"),
            ("and·he-is-  generating Rowan » Micah",
             "and Rowan ·he-is-  generating » Micah"),
        ):
            with self.subTest(input=input_english):
                output, evidence, stats = reorder_structurally_supported_subjects(
                    input_english,
                )
                self.assertEqual(output, expected)
                self.assertEqual(len(evidence), 1)
                self.assertEqual(evidence[0]["rule_code"], RULE_MARKED_GENERATING)
                self.assertEqual(stats["bounded_owner_supported_generating_matches"], 1)
                self.assertEqual(output.count("Rowan"), input_english.count("Rowan"))

    def test_multiple_clauses_processed_without_interference(self):
        text = (
            "Once upon a day, and·he-is- generating Rowan » Micah "
            "and·she-is- generating Mira » Talia. After sunset."
        )
        actual, evidence, counts = reorder_structurally_supported_subjects(text)
        self.assertEqual(
            actual,
            "Once upon a day, and Rowan ·he-is- generating » Micah "
            "and Mira ·she-is- generating » Talia. After sunset.",
        )
        self.assertEqual(len(evidence), 2)
        self.assertEqual(counts["split_finite_gloss_count"], 2)
        self.assertEqual(counts["bounded_owner_supported_generating_matches"], 2)
        self.assertEqual(actual.count("Micah"), text.count("Micah"))
        self.assertEqual(actual.count("Talia"), text.count("Talia"))
        second, changes, _ = reorder_structurally_supported_subjects(actual)
        self.assertEqual(second, actual)
        self.assertEqual(changes, [])

    def test_no_blanket_transitive_object_movement(self):
        for english in (
            "and·he-is- seeing Rowan » Micah",
            "and·he-is- loving Rowan » Micah",
            "and·he-is- generating Rowan",
            "and·he-is- generating Rowan and Micah",
            "and·he-is- generating Rowan » the·child",
            "and·he-is- generating Rowan with Micah",
            "he-is- generating Rowan » Micah",
            "and·he-is- generating to·Rowan » Micah",
            "and·he-is- generating Rowan »",
            "and·he-is- generating Rowan",
            "and·they-are- generating Rowan » Micah",
            "and·he-was- generating Rowan » Micah",
        ):
            with self.subTest(english=english):
                actual, evidence, _ = reorder_structurally_supported_subjects(
                    english,
                )
                self.assertEqual(actual, english)
                self.assertEqual(evidence, [])

    def test_corpus_wide_shape_audit_separates_unresolved(self):
        english = (
            "and·he-is- generating Rowan » Micah and·he-is- seeing Sailors » Others "
            "and·he-is- making a vessel and·she-is- generating Mira » Talia"
        )
        stats = analyze_structural_english_order(english)
        self.assertEqual(stats["split_finite_gloss_count"], 4)
        self.assertEqual(stats["split_finite_gloss_with_name_count"], 3)
        self.assertEqual(stats["split_finite_gloss_with_marker_count"], 3)
        self.assertEqual(stats["bounded_owner_supported_generating_matches"], 2)
        self.assertEqual(stats["split_finite_gloss_with_name_left_unresolved"], 1)
        self.assertEqual(stats["split_finite_gloss_without_adjacent_name"], 1)
        edited, evidence, again = reorder_structurally_supported_subjects(
            english,
        )
        self.assertEqual(again, stats)
        self.assertEqual(len(evidence), 2)
        self.assertIn("and·he-is- seeing Sailors » Others", edited)

    def test_audit_is_english_only_and_writes_nothing(self):
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_NOT_ALLOWED")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("NO_ORIGINAL_LANGUAGE_REGISTRY")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NETWORK_NOT_ALLOWED")),
        ):
            r = build_private_structural_english_reader(self.source)
        self.assertEqual(r["source_chapters_scanned"], 1)
        self.assertEqual(r["source_verses_scanned"], 2)
        self.assertEqual(r["new_private_html_pages"], 0)
        self.assertFalse(r["source_ches_modified"])
        self.assertFalse(r["old_readers_modified"])
        self.assertFalse(r["owner_approval_manifest_modified"])
        self.assertFalse(r["hebrew_cross_validation_performed"])
        self.assertFalse(r["grammar_error_count_established"])
        self.assertTrue(r["remaining_english_grammar_review_required"])
        self.assertFalse(r["generic_postverb_name_movement_performed"])
        self.assertEqual(r["publication_status"], "BLOCKED")
        self.assertEqual(
            r["structural_split_verb_diagnostics"][
                "bounded_owner_supported_generating_matches"], 1,
        )
        self.assertEqual(
            r["structural_split_verb_diagnostics"]["new_bounded_structural_moves"],
            1,
        )
        self.assertEqual(
            r["structural_split_verb_diagnostics"][
                "split_finite_gloss_with_name_left_unresolved"], 1,
        )
        self.assertFalse(
            (self.base / "ches-structural-english-reading").exists(),
        )
        self.assertEqual(self.oldbytes, (self.source / "gen.1.json").read_bytes())

    def test_creates_new_private_v5_without_overwriting_any_existing_reader(self):
        old = build_private_reader(
            self.source, render=True, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        old_dir = self.base / "ches-direct-reader" / old["snapshot_id"]
        preserved = {
            p.name: p.read_bytes() for p in old_dir.iterdir()
            if p.is_file()
        }
        r = build_private_structural_english_reader(self.source, render=True)
        root = self.base / "ches-structural-english-reading"
        folder = root / r["new_private_structural_snapshot_id"]
        self.assertEqual(r["new_private_html_pages"], 2)
        self.assertEqual(root.stat().st_mode & 0o777, 0o700)
        self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        self.assertEqual({p.name for p in folder.iterdir()},
                         {"index.html", "gen.1.html"})
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600
                            for p in folder.iterdir()))
        page = (folder / "gen.1.html").read_text()
        self.assertIn("and Rowan ·he-is- generating » Micah", page)
        self.assertIn("and·he-is- seeing Sailors » Others", page)
        self.assertIn("default-src 'none'", page)
        self.assertNotIn("<script", page)
        again = build_private_structural_english_reader(
            self.source, render=True,
        )
        self.assertEqual(again["new_private_structural_snapshot_id"],
                         r["new_private_structural_snapshot_id"])
        self.assertEqual(self.oldbytes, (self.source / "gen.1.json").read_bytes())
        self.assertEqual(preserved, {
            p.name: p.read_bytes() for p in old_dir.iterdir() if p.is_file()
        })
        self.assertFalse((self.base / "ches-subject-review" / "approved.json").exists())

    def test_retains_existing_owner_cross_clause_rules_in_same_new_v5_view(self):
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = (
            "and·he-is-becoming as·which David - he-sits "
            "in·house-of·him and·he-is-saying David "
            "to Ezra the·prophet afterward "
            "and·he-is- generating Rowan » Micah"
        )
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "that in·them he-chose Yahweh to·to-carry-of some vessels"
        write_private_json(doc, self.source / "gen.1.json")
        report = build_private_structural_english_reader(
            self.source, render=True,
        )
        page = (
            self.base / "ches-structural-english-reading" /
            report["new_private_structural_snapshot_id"] / "gen.1.html"
        ).read_text()
        self.assertIn("and David - ·he-is-becoming", page)
        self.assertIn("and David -·he-is-saying", page)
        self.assertIn("that in·them Yahweh - he-chose", page)
        self.assertIn("and Rowan ·he-is- generating » Micah", page)

    def test_edited_output_not_overwritten(self):
        r = build_private_structural_english_reader(self.source, render=True)
        page = (
            self.base / "ches-structural-english-reading" /
            r["new_private_structural_snapshot_id"] / "gen.1.html"
        )
        page.write_text("OWNER_PRIVATE_EDIT", encoding="utf-8")
        page.chmod(0o600)
        with self.assertRaisesRegex(
            DanMek035Error, "PRIVATE_READING_NO_OVERWRITE",
        ):
            build_private_structural_english_reader(
                self.source, render=True,
            )
        self.assertEqual(page.read_text(), "OWNER_PRIVATE_EDIT")

    def test_require_311_blocks_incomplete_synthetic_source(self):
        with self.assertRaisesRegex(
            DanMek035Error, "STRUCTURAL_REQUIRED_311_MISMATCH",
        ):
            build_private_structural_english_reader(
                self.source, render=True, require_311=True,
            )
        self.assertFalse(
            (self.base / "ches-structural-english-reading").exists(),
        )

    def test_injection_escapes_html(self):
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.example + " <img src=x onerror=alert(1)>"
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.other
        write_private_json(doc, self.source / "gen.1.json")
        r = build_private_structural_english_reader(self.source, render=True)
        html = (
            self.base / "ches-structural-english-reading" /
            r["new_private_structural_snapshot_id"] / "gen.1.html"
        ).read_text()
        self.assertIn("&lt;img", html)
        self.assertNotIn("<img", html)

    def test_cli_stdout_contains_only_aggregate_counts(self):
        with patch("sys.argv", [
            "danmek-035", "--private-root", str(self.source),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            stream = io.StringIO()
            with redirect_stdout(stream):
                self.assertEqual(main(), 0)
        obj = json.loads(stream.getvalue())
        self.assertEqual(obj["source_verses_scanned"], 2)
        for private in ("Rowan", "Micah", "Sailors", "gen.1.1",
                        str(self.source)):
            self.assertNotIn(private, stream.getvalue())
        self.assertFalse(
            (self.base / "ches-structural-english-reading").exists(),
        )


if __name__ == "__main__":
    unittest.main()
