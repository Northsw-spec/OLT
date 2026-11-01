"""Synthetic-only DANMEK-038 full-phrase subject and reporting formula tests."""
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
from scripts.danmek_037_unmarked_clause_roles import (
    build_private_unmarked_clause_reader,
)
from scripts.danmek_038_speech_subject_frames import (
    COMPOUND_RECIPIENT, THUS_SIMPLE, THUS_COMPOUND,
    DanMek038Error, discover_speech_subject_frames,
    apply_speech_subject_frames, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek038SpeechSubjectFrames(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.archive = self.base / "ches"
        self.archive.mkdir(mode=0o700)
        self.first = [
            "thus", "he-says", "Rowan-of", "hosts",
            "behold !", "the·city",
        ]
        self.second = [
            "and·he-is-saying", "Mira", "the·prophet", "to", "Natan",
        ]
        doc = invented_chapter("gen", 1)
        for verse, parts in zip(doc["verses"], (self.first, self.second)):
            verse["source_ches_spans_NOT_OLT_TRANSLATION"] = [
                {"original_ches_line_text": item, "page": 1,
                 "pdf_x": 20 + j * 12, "pdf_y": 60}
                for j, item in enumerate(parts)
            ]
        doc["ches_pdf_green_spans"] = len(self.first) + len(self.second)
        write_private_json(doc, self.archive / "gen.1.json")
        self.source_bytes = (self.archive / "gen.1.json").read_bytes()
        self.reader_before = build_private_reader(
            self.archive, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )

    def test_uses_complete_compound_phrase_not_names_as_literals(self):
        cases = (
            (["and·he-is-saying", "Mira", "the·prophet", "to", "Natan"],
             "and Mira the·prophet -·he-is-saying to Natan", COMPOUND_RECIPIENT),
            (["he-said", "Talia", "daughter-of", "Oren", "to·Rowan"],
             "Talia daughter-of Oren - he-said to·Rowan", COMPOUND_RECIPIENT),
            (["and·he-is-", "speaking", "Jorin", "the·king", "to", "Mira"],
             "and Jorin the·king -·he-is- speaking to Mira",
             COMPOUND_RECIPIENT),
            (["he-said", "Elohim-of", "Judah", "to·me", "now"],
             "Elohim-of Judah - he-said to·me now", COMPOUND_RECIPIENT),
        )
        for source, expected, reason in cases:
            with self.subTest(source=source):
                text, changes, counts = apply_speech_subject_frames(
                    source, " ".join(source),
                )
                self.assertEqual(text, expected)
                self.assertEqual(changes[0]["reason_code"], reason)
                self.assertEqual(counts["new_v8_speech_subject_moves"], 1)

    def test_thus_says_with_or_without_compound_and_with_speech_tail(self):
        cases = (
            (["thus", "he-says", "Rowan", "behold !", "the·city"],
             "thus Rowan - he-says behold ! the·city", THUS_SIMPLE),
            (["thus", "he-said", "Talia", "not", "behold·me !"],
             "thus Talia - he-said not behold·me !", THUS_SIMPLE),
            (["thus", "he-says", "Mira-of", "hosts", "behold !"],
             "thus Mira-of hosts - he-says behold !", THUS_COMPOUND),
            (["thus", "he-says", "Natan", "Elohim-of", "Oren", "not"],
             "thus Natan Elohim-of Oren - he-says not", THUS_COMPOUND),
            (["thus", "he-says", "Rowan", "Elohim", "behold !"],
             "thus Rowan Elohim - he-says behold !", THUS_COMPOUND),
        )
        for src, expected, reason in cases:
            with self.subTest(src=src):
                text, changes, _ = apply_speech_subject_frames(src, " ".join(src))
                self.assertEqual(text, expected)
                self.assertEqual([c["reason_code"] for c in changes], [reason])

    def test_negative_objects_names_and_incomplete_compounds_preserved(self):
        examples = (
            ["he-says", "Rowan", "behold !"],
            ["and·he-is-saying", "Rowan", "behold !"],
            ["thus", "he-says", "I-saw", "not"],
            ["thus", "he-says", "Rowan", "Elohim-of"],
            ["thus", "he-says", "Rowan", "the·unknown", "not"],
            ["thus", "he-says", "Rowan-of", "unknown"],
            ["thus", "he-says", "Rowan", "and·Mira", "not"],
            ["thus", "he-says", "the·vessel", "not"],
            ["and·he-is-saying", "Rowan", "daughter-of", "to", "Mira"],
            ["and·he-is-saying", "Rowan", "the·king", "to·to-build-of", "the·city"],
            ["and·he-is-seeing", "Rowan", "the·king", "to", "Mira"],
            ["and·he-is-says", "Rowan", "the·king", "to", "Mira"],
        )
        for src in examples:
            with self.subTest(src=src):
                before = " ".join(src)
                self.assertEqual(discover_speech_subject_frames(src), [])
                actual, changes, _ = apply_speech_subject_frames(src, before)
                self.assertEqual(actual, before)
                self.assertEqual(changes, [])

    def test_two_disjoint_formula_clauses_one_verse(self):
        source = [
            "thus", "he-says", "Rowan", "not",
            "thus", "he-said", "Talia-of", "hosts", "behold !",
        ]
        result, changes, stats = apply_speech_subject_frames(
            source, " ".join(source),
        )
        self.assertEqual(
            result,
            "thus Rowan - he-says not thus Talia-of hosts - he-said behold !",
        )
        self.assertEqual(stats["raw_source_speech_frames"], 2)
        self.assertEqual(len(changes), 2)

    def test_exact_unique_alignment_refuses_already_edited_or_duplicated(self):
        source = self.first
        original = " ".join(source)
        current = "thus Rowan-of hosts - he-says behold ! the·city"
        after, changes, stats = apply_speech_subject_frames(source, current)
        self.assertEqual(after, current)
        self.assertEqual(changes, [])
        self.assertEqual(stats["already_changed_or_ambiguous_source_alignment"], 1)
        repeated = original + " and " + original
        after, changes, stats = apply_speech_subject_frames(source, repeated)
        self.assertEqual(after, repeated)
        self.assertEqual(changes, [])
        self.assertEqual(stats["already_changed_or_ambiguous_source_alignment"], 1)

    def test_old_v7_mode_unchanged_by_v8_opt_in(self):
        original = build_private_unmarked_clause_reader(self.archive)
        with patch("urllib.request.urlopen",
                   side_effect=AssertionError("NETWORK_DISABLED")):
            v8 = build_private_unmarked_clause_reader(
                self.archive, include_speech_frames_v8=True,
            )
        again = build_private_unmarked_clause_reader(self.archive)
        self.assertEqual(again, original)
        self.assertEqual(original["checkpoint"],
                         "DANMEK-037-PRIVATE-ENGLISH-UNMARKED-CLAUSE-ROLES-v1")
        self.assertEqual(v8["checkpoint"],
                         "DANMEK-038-SOURCE-SPEECH-SUBJECT-FORMULA-COMPOUND-v1")
        self.assertEqual(v8["source_v8_speech_subject_frames"], 2)
        self.assertEqual(v8["new_v8_speech_subject_moves"], 2)
        self.assertEqual(v8["new_v8_moves_by_class"], {
            COMPOUND_RECIPIENT: 1, THUS_COMPOUND: 1,
        })
        self.assertEqual(v8["private_html_files_written_or_verified"], 0)
        self.assertFalse(v8["older_v7_reader_output_modified"])
        self.assertFalse((self.base / "ches-english-speech-formula-v8").exists())
        self.assertEqual(self.source_bytes,
                         (self.archive / "gen.1.json").read_bytes())

    def test_immutable_private_v8_render_does_not_change_v7_html(self):
        old = build_private_unmarked_clause_reader(
            self.archive, render=True,
        )
        old_folder = self.base / "ches-english-clause-roles" / old["private_v7_snapshot"]
        old_data = {p.name:p.read_bytes() for p in old_folder.iterdir() if p.is_file()}
        v8 = build_private_unmarked_clause_reader(
            self.archive, render=True, include_speech_frames_v8=True,
        )
        folder = self.base / "ches-english-speech-formula-v8" / v8["private_v8_snapshot"]
        self.assertEqual(v8["private_html_files_written_or_verified"], 2)
        self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        self.assertEqual(folder.parent.stat().st_mode & 0o777, 0o700)
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600 for p in folder.iterdir()))
        page = (folder / "gen.1.html").read_text()
        self.assertIn("thus Rowan-of hosts - he-says", page)
        self.assertIn("and Mira the·prophet -·he-is-saying", page)
        self.assertIn("Private v8 English", page)
        self.assertNotIn("<script", page)
        self.assertIn("default-src 'none'", page)
        rerun = build_private_unmarked_clause_reader(
            self.archive, render=True, include_speech_frames_v8=True,
        )
        self.assertEqual(rerun["private_v8_snapshot"], v8["private_v8_snapshot"])
        self.assertEqual(old_data, {p.name:p.read_bytes() for p in old_folder.iterdir()
                                    if p.is_file()})
        self.assertEqual(self.source_bytes,
                         (self.archive / "gen.1.json").read_bytes())
        self.assertFalse((self.base / "ches-subject-review" / "approved.json").exists())

    def test_no_overwrite_of_private_owner_edits(self):
        r = build_private_unmarked_clause_reader(
            self.archive, render=True, include_speech_frames_v8=True,
        )
        file = (self.base / "ches-english-speech-formula-v8" /
                r["private_v8_snapshot"] / "gen.1.html")
        file.write_text("OWNER_EDIT_MUST_STAY", encoding="utf-8")
        file.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "PRIVATE_READING_NO_OVERWRITE"):
            build_private_unmarked_clause_reader(
                self.archive, render=True, include_speech_frames_v8=True,
            )
        self.assertEqual(file.read_text(), "OWNER_EDIT_MUST_STAY")

    def test_311_and_invalid_boolean_guard(self):
        with self.assertRaisesRegex(ValueError, "REQUIRE_HISTORICAL_311"):
            build_private_unmarked_clause_reader(
                self.archive, require_311=True, include_speech_frames_v8=True,
                render=True,
            )
        self.assertFalse((self.base / "ches-english-speech-formula-v8").exists())
        with self.assertRaisesRegex(ValueError, "INVALID_PRIVATE_UNMARKED_READER_OPTIONS"):
            build_private_unmarked_clause_reader(
                self.archive, include_speech_frames_v8=1,
            )

    def test_private_cli_only_reports_aggregates(self):
        with patch("sys.argv", [
            "danmek038", "--private-root", str(self.archive),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        stats = json.loads(output.getvalue())
        self.assertEqual(stats["source_v8_speech_subject_frames"], 2)
        for token in ("Rowan-of", "Mira", "hosts", "gen.1.1", str(self.archive)):
            self.assertNotIn(token, output.getvalue())


if __name__ == "__main__":
    unittest.main()
