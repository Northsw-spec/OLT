"""DANMEK-014: synthetic offline tests for standalone lowercase c marker cleanup."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_015_direct_private_reader import build_private_reader, main
from scripts.ches_import import write_private_json
from scripts.danmek_012_display import hide_isolated_c
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek014StandaloneC(unittest.TestCase):
    def test_duplicate_and_embedded_whitespace_delimited_c(self):
        samples = [
            ("c c", None, 2),
            ("cc", None, 2),
            ("ccc ", None, 3),
            ("c c and·the·king", "and·the·king", 2),
            ("and c c he walked", "and he walked", 2),
            ("and c", "and", 1),
            ("c and", "and", 1),
            ("a c b", "a b", 1),
            ("a cc b", "a b", 2),
            ("word c c then", "word then", 2),
            ("c\nc next", "next", 2),
            ("c\tword", "word", 1),
        ]
        for raw, expected, count in samples:
            with self.subTest(raw=raw):
                original = [raw]
                result, removed = hide_isolated_c(original)
                self.assertEqual(result, [expected])
                self.assertEqual(removed, count)
                self.assertEqual(original, [raw])

    def test_no_change_to_real_words_case_punctuation_and_source_markers(self):
        samples = [
            "C", "CC", "C c.", "c.", "c,", "c·", "c-", "-c",
            "c/e", "abc", "comet", "sc", "c2", "2c",
            "café", "c’s", "a·c", "c·and", "and·he-came",
            "c_x", "x_c", "", None,
        ]
        result, removed = hide_isolated_c(samples)
        self.assertEqual(result, samples)
        self.assertEqual(removed, 0)

    def test_separate_fragments_and_verse_boundaries(self):
        parts = ["c", "c", "And", "cc", " c c ", "a c b", "C"]
        result, removed = hide_isolated_c(parts)
        self.assertEqual(result, [None, None, "And", None, None, "a b", "C"])
        self.assertEqual(removed, 7)

    def test_source_preserved_html_snapshot_is_new_and_metadata_count_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / ".olt-private"
            root.mkdir(mode=0o700)
            folder = root / "ches"
            folder.mkdir(mode=0o700)
            chapter = invented_chapter("gen", 1)
            spans = chapter["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
            spans[0]["original_ches_line_text"] = "c c and·the·king"
            spans.extend([
                {"page": 1, "pdf_x": 30, "pdf_y": 5.5,
                 "original_ches_line_text": " c "},
                {"page": 1, "pdf_x": 31, "pdf_y": 5.7,
                 "original_ches_line_text": "king c city"},
                {"page": 1, "pdf_x": 32, "pdf_y": 5.8,
                 "original_ches_line_text": "C c. candle"},
            ])
            chapter["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
                "original_ches_line_text"
            ] = "cc at the beginning"
            chapter["ches_pdf_green_spans"] = 5
            source = folder / "gen.1.json"
            write_private_json(chapter, source)
            original_bytes = source.read_bytes()

            with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
                original_reader = build_private_reader(folder, render=True)
                cleaned_reader = build_private_reader(
                    folder, render=True, olt_owner_approved_candidates=True,
                )
                stable_reader = build_private_reader(
                    folder, render=True, olt_owner_approved_candidates=True,
                )

            self.assertEqual(
                cleaned_reader["snapshot_id"], stable_reader["snapshot_id"],
            )
            self.assertNotEqual(
                original_reader["snapshot_id"], cleaned_reader["snapshot_id"],
            )
            self.assertEqual(
                cleaned_reader["olt_isolated_lowercase_c_fragments_hidden"], 1,
            )
            self.assertEqual(
                cleaned_reader["olt_standalone_lowercase_c_letters_hidden"], 6,
            )
            self.assertEqual(source.read_bytes(), original_bytes)

            root_html = root / "ches-direct-reader"
            old_html = (
                root_html / original_reader["snapshot_id"] / "gen.1.html"
            ).read_text()
            new_html = (
                root_html / cleaned_reader["snapshot_id"] / "gen.1.html"
            ).read_text()

            self.assertIn("c c and·the·king", old_html)
            self.assertIn("> c </span>", old_html)
            self.assertIn("cc at the beginning", old_html)
            self.assertIn('>and·the·king</span>', new_html)
            self.assertIn('>king city</span>', new_html)
            self.assertIn('>at the beginning</span>', new_html)
            self.assertIn('>C c. candle</span>', new_html)
            self.assertNotIn('> c </span>', new_html)
            self.assertEqual(source.read_bytes(), original_bytes)

            with patch("sys.argv", [
                "reader", "--private-root", str(folder),
                "--confirm-machine-readable-use-permission",
                "--audit-only", "--olt-owner-approved-candidates",
            ]):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(), 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report["olt_standalone_lowercase_c_letters_hidden"], 6)
            self.assertEqual(report["olt_isolated_lowercase_c_fragments_hidden"], 1)
            self.assertNotIn("the·king", output.getvalue())
            self.assertNotIn(str(folder), output.getvalue())


if __name__ == "__main__":
    unittest.main()
