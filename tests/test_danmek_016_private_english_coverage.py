"""DANMEK-016: metadata-only private OT reader coverage tests, invented text."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.danmek_016_private_english_coverage import (
    DanMek016Error, audit_private_english_coverage, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek016PrivateEnglishCoverage(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)
        first = invented_chapter("gen", 1)
        spans = first["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
        spans[0]["original_ches_line_text"] = (
            "and·he-cameDavidfrom·Town sur faces c c"
        )
        spans.append({
            "page": 1, "pdf_x": 19.0, "pdf_y": 6.5,
            "original_ches_line_text": "cc",
        })
        first["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "c city c. C"
        first["ches_pdf_green_spans"] = 3
        write_private_json(first, self.source / "gen.1.json")
        write_private_json(
            invented_chapter("gen", 3), self.source / "gen.3.json",
        )
        write_private_json(
            invented_chapter("exo", 1, source_sha="f" * 64),
            self.source / "exo.1.json",
        )
        self.source_bytes = {
            p.name: p.read_bytes() for p in self.source.iterdir()
        }

    def test_per_prefix_counts_and_reader_crosscheck_no_private_writes(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            report = audit_private_english_coverage(self.source)
            repeated = audit_private_english_coverage(self.source)
        self.assertEqual(report, repeated)
        self.assertEqual(report["checkpoint"], "DANMEK-016-PRIVATE-OT-ENGLISH-COVERAGE-v1")
        self.assertEqual(report["mode"], "OFFLINE_METADATA_ONLY_READ_ONLY")
        self.assertEqual(report["observed_chapters"], 3)
        self.assertEqual(report["observed_source_prefixes_not_verified_book_ids"], 2)
        self.assertEqual(report["observed_verses"], 6)
        self.assertEqual(report["observed_source_english_fragments"], 7)
        self.assertFalse(report["all_929_39_present_by_count_only"])
        self.assertFalse(report["source_index_membership_independently_verified"])
        self.assertFalse(report["source_prefixes_verified_as_canonical_book_ids"])
        self.assertFalse(report["private_english_corpus_fully_visually_reviewed"])
        self.assertFalse(report["hebrew_english_word_alignment_or_syntax_verified"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertEqual(report["source_or_private_html_files_created"], 0)
        self.assertEqual(report["original_private_chapter_json_files_modified"], 0)
        self.assertFalse(report["private_source_words_in_output"])
        self.assertEqual(set(report["per_source_filename_prefix"]), {"gen", "exo"})

        gen = report["per_source_filename_prefix"]["gen"]
        self.assertEqual(gen["chapters_observed"], 2)
        self.assertEqual(gen["first_chapter_number_observed"], 1)
        self.assertEqual(gen["last_chapter_number_observed"], 3)
        self.assertEqual(gen["internal_chapter_number_gaps_observed"], 1)
        self.assertEqual(gen["verses_observed"], 4)
        self.assertEqual(gen["ches_english_source_fragments_observed"], 5)
        self.assertEqual(gen["owner_order_candidates_applied"], 1)
        self.assertEqual(gen["ambiguous_order_verses_unchanged"], 0)
        self.assertEqual(gen["ylt_order_overlap_verses_unchanged"], 0)
        self.assertEqual(gen["verses_without_order_candidate"], 3)
        self.assertEqual(gen["faces_display_simplifications"], 1)
        self.assertEqual(gen["lowercase_c_letters_hidden"], 5)
        self.assertEqual(gen["whole_lowercase_c_fragments_hidden"], 1)
        self.assertEqual(gen["verses_with_at_least_one_visible_edit"], 2)
        self.assertEqual(gen["verses_without_a_visible_edit"], 2)
        exo = report["per_source_filename_prefix"]["exo"]
        self.assertEqual(exo["verses_observed"], 2)
        self.assertEqual(exo["owner_order_candidates_applied"], 0)
        self.assertEqual(exo["verses_without_a_visible_edit"], 2)

        self.assertFalse((self.base / "ches-direct-reader").exists())
        self.assertEqual(self.source_bytes, {
            p.name: p.read_bytes() for p in self.source.iterdir()
        })
        raw_report = json.dumps(report)
        for forbidden in ("David", "Town", "faces", "city", str(self.source)):
            # The boolean/key 'faces_display_simplifications' is allowed;
            # only the real example phrase must not be reported.
            if forbidden == "faces":
                continue
            self.assertNotIn(forbidden, raw_report)
        self.assertNotIn("and·he-came", raw_report)

    def test_cli_stdout_only_aggregate_metadata_and_no_html(self):
        with patch("sys.argv", [
            "audit", "--private-root", str(self.source),
            "--confirm-machine-readable-use-permission",
        ]), patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            printed = io.StringIO()
            with redirect_stdout(printed):
                self.assertEqual(main(), 0)
        actual = json.loads(printed.getvalue())
        self.assertEqual(actual["observed_chapters"], 3)
        self.assertEqual(actual["per_source_filename_prefix"]["gen"][
            "owner_order_candidates_applied"
        ], 1)
        self.assertNotIn("and·he-cameDavid", printed.getvalue())
        self.assertNotIn("city", printed.getvalue())
        self.assertNotIn(str(self.source), printed.getvalue())
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_expected_full_corpus_gate_fails_closed_on_partial_archive(self):
        with self.assertRaisesRegex(DanMek016Error, "FULL_929_39_COUNT_NOT_REACHED"):
            audit_private_english_coverage(
                self.source, require_929=True,
            )
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_ylt_overlap_is_separate_from_english_order_approval(self):
        original = (
            "and·he-cameDavidfrom·Town sur faces c c"
        )
        proposed = "and·he-cameDavidfrom·Village sur faces c c"
        def mock_ylt_verses(source, *, prefix, chapter, ylt):
            if prefix == "gen" and chapter == 1:
                return (
                    {("gen.1.1", 1): proposed},
                    {
                        "noun_changes": 1, "tense_changes": 0,
                        "unmapped_verses_left_unchanged": 0,
                        "ambiguous_verses_left_unchanged": 0,
                    },
                )
            return ({}, {
                "noun_changes": 0, "tense_changes": 0,
                "unmapped_verses_left_unchanged": 0,
                "ambiguous_verses_left_unchanged": 0,
            })
        self.assertNotEqual(original, proposed)
        with (
            patch("scripts.ches_015_direct_private_reader.load_private_ylt",
                  return_value=({}, "a" * 40)),
            patch("scripts.danmek_016_private_english_coverage.load_private_ylt",
                  return_value=({}, "a" * 40)),
            patch("scripts.ches_015_direct_private_reader.propose_ylt_verse_overrides",
                  side_effect=mock_ylt_verses),
            patch("scripts.danmek_016_private_english_coverage.propose_ylt_verse_overrides",
                  side_effect=mock_ylt_verses),
        ):
            report = audit_private_english_coverage(
                self.source, use_ylt_authority=True,
            )
        self.assertTrue(report["ylt_authority_used"])
        gen = report["per_source_filename_prefix"]["gen"]
        self.assertEqual(gen["owner_order_candidates_applied"], 0)
        self.assertEqual(gen["ylt_order_overlap_verses_unchanged"], 1)
        self.assertEqual(gen["ylt_noun_edits"], 1)
        self.assertEqual(gen["verses_with_at_least_one_visible_edit"], 2)
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_rejects_corruption_and_invalid_audit_flags_without_exposing_text(self):
        with self.assertRaises(DanMek016Error):
            audit_private_english_coverage(
                self.source, use_ylt_authority="true",
            )
        first = self.source / "gen.1.json"
        first.write_text("not JSON and no private words", encoding="utf-8")
        with self.assertRaisesRegex(DanMek016Error, "PRIVATE_COVERAGE_AUDIT_FAILED"):
            audit_private_english_coverage(self.source)
        self.assertFalse((self.base / "ches-direct-reader").exists())


if __name__ == "__main__":
    unittest.main()
