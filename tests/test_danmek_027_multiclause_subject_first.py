"""DANMEK-027 isolated synthetic tests; no real CHES text is committed."""
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
from scripts.danmek_027_multiclause_subject_first import (
    DanMek027Error, reorder_postverbal_subjects, build_subject_first_reader,
    _legacy_candidate_guard, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek027MulticlauseSubjects(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.chapters = self.base / "ches"
        self.chapters.mkdir(mode=0o700)
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "and·they-are-hearing Sailors that he-was-anointed Rowan"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and the lantern — the merchant saw."
        write_private_json(gen, self.chapters / "gen.1.json")
        self.original = (self.chapters / "gen.1.json").read_bytes()
        self.before = build_private_reader(
            self.chapters, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        self.assertEqual(self.before["olt_owner_candidate_ambiguous_verses_unchanged"], 1)

    def test_multiple_clauses_reordered_exact_owner_requested_shape(self):
        source = "and·they-are-hearing Sailors that he-was-anointed Rowan"
        original = [source]
        after, evidence, unresolved = reorder_postverbal_subjects(original)
        self.assertEqual(
            after, ["and Sailors -·they-are-hearing that Rowan - he-was-anointed"]
        )
        self.assertEqual([e["reason_code"] for e in evidence], [
            "OWNER_REPORT_HEARING_MULTI_CLAUSE", "POSTPOSED_PASSIVE_SUBJECT"
        ])
        self.assertEqual(unresolved, 0)
        self.assertEqual(original, [source])
        self.assertFalse(any(e["hebrew_word_alignment_performed"] for e in evidence))

    def test_same_rules_work_across_separate_chapter_fragments(self):
        pieces = ["and·they-are-hearing", "Sailors", "that",
                  "he-was-anointed", "Rowan"]
        after, evidence, unresolved = reorder_postverbal_subjects(pieces)
        self.assertEqual(after, [
            "and Sailors -·they-are-hearing that Rowan - he-was-anointed"
        ])
        self.assertEqual(len(evidence), 2)
        self.assertEqual(unresolved, 0)

    def test_multiple_passive_and_intransitive_clause_subjects(self):
        before = ["and·he-came Rowan and he-was-appointed Elias"]
        after, evidence, unresolved = reorder_postverbal_subjects(before)
        self.assertEqual(after, [
            "and Rowan -·he-came and Elias - he-was-appointed"
        ])
        self.assertEqual(len(evidence), 2)
        self.assertEqual(unresolved, 0)

    def test_ambiguous_possible_objects_and_valid_poetic_syntax_do_not_move(self):
        for before in (
            "he-saw Sailors",
            "he-loved Rowan",
            "they-are-hearing Sailors",
            "and the lantern — the merchant saw.",
            "and Rowan -·he-came",
            "he-was-calling Rowan",
        ):
            with self.subTest(before=before):
                after, evidence, _ = reorder_postverbal_subjects([before])
                self.assertEqual(after, [before])
                self.assertEqual(evidence, [])

    def test_expanded_hearing_and_compound_title_subjects(self):
        before = [
            "And·they-were-hearing the·Sailors that "
            "she-is-anointed the·King Rowan"
        ]
        output, evidence, uncertain = reorder_postverbal_subjects(before)
        self.assertEqual(output, [
            "And the·Sailors -·they-were-hearing that "
            "the·King Rowan - she-is-anointed"
        ])
        self.assertEqual(len(evidence), 2)
        self.assertEqual(uncertain, 0)
        self.assertEqual(before[0].count("the·"), 2)

    def test_compound_names_and_capitalized_clause_boundaries(self):
        sample = ["he-was-appointed King Rowan And he-came Elias"]
        after, found, missing = reorder_postverbal_subjects(sample)
        self.assertEqual(
            after, ["King Rowan - he-was-appointed And Elias - he-came"]
        )
        self.assertEqual(len(found), 2)
        self.assertEqual(missing, 0)

    def test_unqualified_transitives_and_returned_not_reordered(self):
        for candidate in (
            "he-saw Sailors",
            "he-returned Rowan",
            "he-loved Rowan",
            "he-is-making Worker the·work",
            "they-were-hearing Sailors",
            "and the prophet — he saw."
        ):
            with self.subTest(candidate=candidate):
                after, evidence, _ = reorder_postverbal_subjects([candidate])
                self.assertEqual(after, [candidate])
                self.assertEqual(evidence, [])

    def test_guard_prevents_inherited_object_as_subject(self):
        original = ["he-saw Sailors"]
        visible, reason, skipped = _legacy_candidate_guard(
            reference="gen.1.1", chapter_sha256="a" * 64,
            original=original,
        )
        self.assertEqual(visible, original)
        self.assertEqual(reason, "LEGACY_UNVERIFIED_SUBJECT_UNCHANGED")
        self.assertTrue(skipped)

        maker = ["he-is-making Worker the·work"]
        visible, reason, skipped = _legacy_candidate_guard(
            reference="gen.1.1", chapter_sha256="a" * 64,
            original=maker,
        )
        self.assertEqual(visible, maker)
        self.assertTrue(skipped)

    def test_guard_retains_explicit_old_owner_and_clear_intransitive(self):
        for original, expected in (
            (["and·he-shaped", "God"], ["and God — ", "he-shaped"]),
            (["and·he-came", "Rowan"], ["and Rowan — ", "he-came"]),
        ):
            with self.subTest(original=original):
                visible, reason, skipped = _legacy_candidate_guard(
                    reference="gen.1.1", chapter_sha256="a" * 64,
                    original=original,
                )
                self.assertEqual(reason, "APPLIED")
                self.assertFalse(skipped)
                self.assertEqual(visible, expected)

    def test_reader_generates_separate_immutable_private_snapshot(self):
        before_result = build_private_reader(
            self.chapters, render=True, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        owner_snapshot = self.base / "ches-direct-reader" / before_result["snapshot_id"]
        owner_bytes = {
            f.name: f.read_bytes() for f in owner_snapshot.iterdir() if f.is_file()
        }
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("NO HEBREW LOOKUP")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("NO SOURCE REGISTRY")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NO INTERNET")),
        ):
            report = build_subject_first_reader(self.chapters, render=True)
        self.assertEqual(report["source_chapters_scanned"], 1)
        self.assertEqual(report["source_verses_scanned"], 2)
        self.assertEqual(report["historical_ambiguous_english_verses"], 1)
        self.assertEqual(report["new_postverbal_subject_pairs_reordered"], 2)
        self.assertEqual(report["legacy_unverified_subject_moves_not_inherited"], 1)
        self.assertTrue(report["locked_legacy_html_remains_available_unchanged"])
        self.assertEqual(report["verses_with_new_reorders"], 1)
        self.assertEqual(report["new_private_html_pages"], 2)
        self.assertFalse(report["hebrew_cross_validation_performed"])
        self.assertFalse(report["original_ches_source_modified"])
        self.assertFalse(report["locked_danmek_reader_modified"])
        self.assertEqual(report["publication_status"], "BLOCKED")

        page_root = self.base / "ches-subject-reading" / report["new_private_snapshot_id"]
        self.assertEqual(page_root.stat().st_mode & 0o777, 0o700)
        chapter_file = page_root / "gen.1.html"
        self.assertEqual(chapter_file.stat().st_mode & 0o777, 0o600)
        self.assertEqual((page_root / "index.html").stat().st_mode & 0o777, 0o600)
        chapter = chapter_file.read_text(encoding="utf-8")
        self.assertIn(
            "and Sailors -·they-are-hearing that Rowan - he-was-anointed", chapter
        )
        self.assertIn("he-saw Sailors", chapter)
        self.assertIn("default-src 'none'", chapter)
        self.assertEqual(self.original, (self.chapters / "gen.1.json").read_bytes())
        self.assertEqual(
            owner_bytes,
            {f.name: f.read_bytes() for f in owner_snapshot.iterdir() if f.is_file()},
        )
        again = build_subject_first_reader(self.chapters, render=True)
        self.assertEqual(again["new_private_snapshot_id"], report["new_private_snapshot_id"])

    def test_audit_only_does_not_write_any_files(self):
        with patch("urllib.request.urlopen",
                   side_effect=AssertionError("NETWORK FORBIDDEN")):
            metadata = build_subject_first_reader(self.chapters)
        self.assertEqual(metadata["new_private_html_pages"], 0)
        self.assertEqual(metadata["new_postverbal_subject_pairs_reordered"], 2)
        self.assertFalse((self.base / "ches-subject-reading").exists())
        self.assertFalse((self.base / "ches-direct-reader").exists())
        self.assertEqual((self.chapters / "gen.1.json").read_bytes(), self.original)

    def test_synthetic_archive_fails_require_311_without_writing(self):
        with self.assertRaisesRegex(DanMek027Error,
                                    "OWNER_REPORTED_311_AMBIGUITIES_CHANGED"):
            build_subject_first_reader(
                self.chapters, render=True, require_311=True,
            )
        self.assertFalse((self.base / "ches-subject-reading").exists())

    def test_no_overwrite_of_private_owner_edited_html(self):
        report = build_subject_first_reader(self.chapters, render=True)
        target = (self.base / "ches-subject-reading" /
                  report["new_private_snapshot_id"] / "gen.1.html")
        target.write_text("OWNER CUSTOM EDIT - NO OVERWRITE", encoding="utf-8")
        target.chmod(0o600)
        with self.assertRaisesRegex(DanMek027Error, "PRIVATE_READING_NO_OVERWRITE"):
            build_subject_first_reader(self.chapters, render=True)
        self.assertEqual(target.read_text(encoding="utf-8"), "OWNER CUSTOM EDIT - NO OVERWRITE")

    def test_rejects_symlinked_output_and_invalid_fragments(self):
        parent = self.base / "ches-subject-reading"
        parent.symlink_to(self.chapters, target_is_directory=True)
        with self.assertRaisesRegex(DanMek027Error, "PRIVATE_READING_DIRECTORY_SYMLINK"):
            build_subject_first_reader(self.chapters, render=True)
        parent.unlink()
        for fragments in ([], ["fine", 42], "he-was-appointed Rowan"):
            with self.assertRaisesRegex(DanMek027Error, "INVALID_PRIVATE_ENGLISH"):
                reorder_postverbal_subjects(fragments)

    def test_html_escape_and_cli_aggregate_privacy(self):
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-was-anointed Rowan and he-was-appointed Elias <img src=x onerror=alert(1)>"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "No synthetic change"
        write_private_json(gen, self.chapters / "gen.1.json")
        with patch("sys.argv", [
            "danmek-027", "--private-root", str(self.chapters),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        self.assertNotIn("Rowan", output.getvalue())
        self.assertNotIn(str(self.chapters), output.getvalue())
        self.assertEqual(json.loads(output.getvalue())[
            "new_postverbal_subject_pairs_reordered"], 2)
        report = build_subject_first_reader(self.chapters, render=True)
        html_data = (self.base / "ches-subject-reading" /
                     report["new_private_snapshot_id"] / "gen.1.html").read_text()
        self.assertIn("&lt;img", html_data)
        self.assertNotIn("<img", html_data)
        self.assertNotIn("<script", html_data)


if __name__ == "__main__":
    unittest.main()
