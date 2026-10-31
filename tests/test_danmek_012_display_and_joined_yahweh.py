"""DANMEK-012 regressions with invented source fragments only."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.ches_015_direct_private_reader import build_private_reader, main
from scripts.danmek_011_owner_order import (
    apply_owner_approved_candidates, discover_candidates,
)
from scripts.danmek_012_display import DanMek012Error, hide_isolated_c
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek012JoinedYahwehAndIsolatedC(unittest.TestCase):
    def test_narrow_joined_clause_english_presentation(self):
        # Invented location and following lexemes; no CHES passage in Git.
        source = "and·he-shall-cut-offYahwehfrom·Townfrontand·rear"
        candidates, ambiguous = discover_candidates("gen.1.1", "f" * 64, [source])
        self.assertFalse(ambiguous)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["mode"], "inline")
        self.assertFalse(candidates[0]["source_syntax_reviewed"])
        output, reason = apply_owner_approved_candidates(
            reference="gen.1.1", chapter_sha256="f" * 64,
            original=[source], visible=[source],
        )
        self.assertEqual(reason, "APPLIED")
        self.assertEqual(
            output, ["And Yahweh — he shall cut off from·Townfrontand·rear"],
        )
        self.assertNotIn("He shall", output[0])
        self.assertEqual(source, "and·he-shall-cut-offYahwehfrom·Townfrontand·rear")

    def test_clause_starts_with_capital_and_or_space_separator(self):
        for start in ("And·", "and ", "And "):
            with self.subTest(start=start):
                source = start + "he-shall-cut-offYahwehfrom·Town"
                actual, reason = apply_owner_approved_candidates(
                    reference="gen.1.1", chapter_sha256="f" * 64,
                    original=[source], visible=[source],
                )
                self.assertEqual(reason, "APPLIED")
                self.assertEqual(actual, ["And Yahweh — he shall cut off from·Town"])

    def test_name_mentioned_as_object_is_not_moved(self):
        cases = (
            "and·he-shall-seeYahwehfrom·Town",
            "and·he-shall-cut-offWorkerfrom·Town",
            "and·he-shall-cut-offYahwehand·another",
            "and·she-shall-cut-offYahwehfrom·Town",
            "and·he-invited Yahweh from Town",
        )
        for source in cases:
            with self.subTest(source=source):
                actual, reason = apply_owner_approved_candidates(
                    reference="gen.1.1", chapter_sha256="a" * 64,
                    original=[source], visible=[source],
                )
                self.assertEqual(reason, "NO_CANDIDATE")
                self.assertEqual(actual, [source])

    def test_multiple_candidate_pairs_remain_unchanged(self):
        source = ("and·he-shall-cut-offYahwehfrom·Town "
                  "she-is-building Leader")
        actual, reason = apply_owner_approved_candidates(
            reference="gen.1.1", chapter_sha256="f" * 64,
            original=[source], visible=[source],
        )
        self.assertEqual(reason, "AMBIGUOUS")
        self.assertEqual(actual, [source])

    def test_localized_ylt_conflict_is_not_moved(self):
        before = "and·he-shall-cut-offYahwehfrom·Town"
        edited = "and·he-shall-removedYahwehfrom·Town"
        actual, reason = apply_owner_approved_candidates(
            reference="gen.1.1", chapter_sha256="f" * 64,
            original=[before], visible=[edited],
        )
        self.assertEqual(reason, "YLT_OVERLAP")
        self.assertEqual(actual, [edited])

    def test_only_whole_isolated_lowercase_c_fragments_are_hidden(self):
        original = [
            "c", " c ", "c\n", "C", "c.", "clock", "a c b",
            "city", "Yahweh", "", None,
        ]
        rendered, count = hide_isolated_c(original)
        self.assertEqual(count, 3)
        self.assertEqual(rendered[:3], [None, None, None])
        self.assertEqual(rendered[3:], original[3:])
        self.assertEqual(original[0], "c")
        for invalid in ("c", [1], [False], [b"c"]):
            with self.subTest(invalid=invalid), self.assertRaises(DanMek012Error):
                hide_isolated_c(invalid)

    def test_private_reader_snapshots_and_count_only_are_isolated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / ".olt-private"
            root.mkdir(mode=0o700)
            folder = root / "ches"
            folder.mkdir(mode=0o700)
            doc = invented_chapter("gen", 1)
            first = doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
            first[0]["original_ches_line_text"] = (
                "and·he-shall-cut-offYahwehfrom·Townfrontand·rear"
            )
            first.extend([
                {"page": 1, "pdf_x": 27, "pdf_y": 6.0,
                 "original_ches_line_text": " c "},
                {"page": 1, "pdf_x": 29, "pdf_y": 6.1,
                 "original_ches_line_text": "city"},
            ])
            second = doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"]
            second[0]["original_ches_line_text"] = "sur faces"
            doc["ches_pdf_green_spans"] = 4
            source_path = folder / "gen.1.json"
            write_private_json(doc, source_path)
            original_bytes = source_path.read_bytes()

            with patch("urllib.request.urlopen",
                       side_effect=AssertionError("NETWORK")):
                faithful = build_private_reader(folder, render=True)
                overlay = build_private_reader(
                    folder, render=True, olt_owner_approved_candidates=True,
                    olt_display_faces=True,
                )
                same = build_private_reader(
                    folder, render=True, olt_owner_approved_candidates=True,
                    olt_display_faces=True,
                )
            self.assertEqual(same["snapshot_id"], overlay["snapshot_id"])
            self.assertNotEqual(faithful["snapshot_id"], overlay["snapshot_id"])
            self.assertEqual(
                overlay["olt_owner_approved_candidate_reorders_applied"], 1,
            )
            self.assertEqual(overlay["olt_isolated_lowercase_c_fragments_hidden"], 1)
            self.assertEqual(overlay["olt_display_sur_faces_to_faces_count"], 1)
            self.assertFalse(
                overlay["olt_owner_candidate_original_language_subject_verified"],
            )
            self.assertEqual(source_path.read_bytes(), original_bytes)
            faithful_html = (
                root / "ches-direct-reader" /
                faithful["snapshot_id"] / "gen.1.html"
            ).read_text()
            overlay_html = (
                root / "ches-direct-reader" /
                overlay["snapshot_id"] / "gen.1.html"
            ).read_text()
            self.assertIn("and·he-shall-cut-offYahweh", faithful_html)
            self.assertIn('<span class="gloss"> c </span>', faithful_html)
            self.assertIn(
                "And Yahweh — he shall cut off from·Townfrontand·rear",
                overlay_html,
            )
            self.assertNotIn('<span class="gloss"> c </span>', overlay_html)
            self.assertIn('<span class="gloss">city</span>', overlay_html)
            self.assertIn('<span class="gloss">faces</span>', overlay_html)

            with patch("sys.argv", [
                "reader", "--private-root", str(folder),
                "--confirm-machine-readable-use-permission",
                "--audit-only", "--olt-owner-approved-candidates",
            ]):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(), 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report["olt_isolated_lowercase_c_fragments_hidden"], 1)
            self.assertEqual(report["olt_owner_approved_candidate_reorders_applied"], 1)
            self.assertNotIn("Yahweh", output.getvalue())
            self.assertNotIn(str(folder), output.getvalue())
            self.assertEqual(source_path.read_bytes(), original_bytes)


if __name__ == "__main__":
    unittest.main()
