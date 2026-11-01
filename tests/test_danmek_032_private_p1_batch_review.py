"""DANMEK-032 synthetic-only regressions for private historical P1 review."""
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
from scripts.danmek_030_reviewed_english_subject_order import SCHEMA
from scripts.danmek_031_private_english_priority_triage import (
    triage_private_english_roles,
)
from scripts.danmek_032_private_p1_batch_review import (
    DanMek032Error, build_private_p1_batches, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek032PrivateP1Review(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.base = Path(self._temporary.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)
        chapter = invented_chapter("gen", 1)
        chapter["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan"
        chapter["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(chapter, self.source / "gen.1.json")
        self.old_source = (self.source / "gen.1.json").read_bytes()
        self.old_reader = build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )

    def _make_priority(self):
        report = triage_private_english_roles(
            self.source, write_private_report=True,
        )
        self.assertEqual(report["historical_english_ambiguities_seen"], 1)
        return report

    def test_requires_real_private_031_priority_report(self):
        with self.assertRaisesRegex(
            DanMek032Error, "PRIVATE_PRIORITY_REPORT_DIRECTORY_MISSING_OR_UNSAFE",
        ):
            build_private_p1_batches(self.source)
        self.assertFalse((self.base / "ches-subject-batches").exists())

    def test_aggregate_only_reports_group_and_no_grammar_approvals(self):
        self._make_priority()
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_SOURCE_FORBIDDEN")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("HEBREW_REGISTRY_FORBIDDEN")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NETWORK_FORBIDDEN")),
        ):
            report = build_private_p1_batches(self.source)
        self.assertEqual(report["source_chapters_scanned"], 1)
        self.assertEqual(report["source_verses_scanned"], 2)
        self.assertEqual(report["historical_english_ambiguities"], 1)
        self.assertEqual(report["historical_p1_verses"], 1)
        self.assertEqual(report["historical_p2_unmatched_verses"], 0)
        self.assertEqual(report["historical_p1_candidate_pairs"], 2)
        self.assertEqual(report["additional_nonhistorical_candidate_pairs"], 1)
        self.assertEqual(report["total_candidate_pairs"], 3)
        self.assertEqual(report["number_of_private_p1_batches"], 1)
        self.assertEqual(report["new_private_files_written_or_verified"], 0)
        self.assertEqual(report["subject_corrections_approved_by_this_tool"], 0)
        self.assertFalse(report["hebrew_cross_validation_performed"])
        self.assertFalse(report["locked_readers_modified"])
        self.assertFalse(report["original_ches_modified"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertFalse((self.base / "ches-subject-batches").exists())
        self.assertEqual(
            self.old_source, (self.source / "gen.1.json").read_bytes(),
        )
        self.assertEqual(
            self.old_reader,
            build_private_reader(
                self.source, render=False, olt_display_faces=True,
                olt_owner_approved_candidates=True,
            ),
        )

    def test_private_batched_html_and_seed_are_immutable_and_unapproved(self):
        self._make_priority()
        report = build_private_p1_batches(
            self.source, write_private_batches=True,
        )
        self.assertEqual(report["new_private_files_written_or_verified"], 3)
        parent = self.base / "ches-subject-batches"
        folder = parent / report["new_private_batch_snapshot_id"]
        self.assertEqual(parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        files = sorted(folder.iterdir())
        self.assertEqual(len(files), 3)
        self.assertEqual({p.name for p in files}, {
            "index.html", "batch-001.html", "UNAPPROVED-review-starter.json",
        })
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600 for p in files))
        starter = json.loads(
            (folder / "UNAPPROVED-review-starter.json").read_text()
        )
        self.assertEqual(starter["schema"], SCHEMA)
        self.assertEqual(starter["source_owner_reader_snapshot"],
                         self.old_reader["snapshot_id"])
        self.assertEqual(len(starter["rules"]), 2)
        self.assertTrue(all(
            rule["english_subject_role_reviewed"] is False
            and rule["review_note"] == "" for rule in starter["rules"]
        ))
        self.assertFalse((self.base / "ches-subject-review" / "approved.json").exists())
        html_page = (folder / "batch-001.html").read_text()
        self.assertIn("he-saw Sailors and he-loved Rowan", html_page)
        self.assertNotIn("he-is-making Worker", html_page)
        self.assertIn("default-src 'none'", html_page)
        self.assertNotIn("<script", html_page)
        self.assertIn("batch-001.html", (folder / "index.html").read_text())
        again = build_private_p1_batches(
            self.source, write_private_batches=True,
        )
        self.assertEqual(again["new_private_batch_snapshot_id"],
                         report["new_private_batch_snapshot_id"])
        self.assertEqual(len(list(folder.iterdir())), 3)
        self.assertEqual(
            self.old_source, (self.source / "gen.1.json").read_bytes(),
        )

    def test_two_historical_cases_can_be_split_into_small_batches(self):
        additional = invented_chapter("exo", 1, source_sha="f" * 64)
        additional["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan"
        additional["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "The light shone."
        write_private_json(additional, self.source / "exo.1.json")
        original_before = {
            p.name: p.read_bytes() for p in self.source.iterdir()
        }
        actual = triage_private_english_roles(
            self.source, write_private_report=True,
        )
        self.assertEqual(actual["historical_english_ambiguities_seen"], 2)
        r = build_private_p1_batches(
            self.source, batch_size=1, write_private_batches=True,
        )
        self.assertEqual(r["historical_p1_verses"], 2)
        self.assertEqual(r["historical_p1_candidate_pairs"], 4)
        self.assertEqual(r["number_of_private_p1_batches"], 2)
        self.assertEqual(r["new_private_files_written_or_verified"], 4)
        directory = (self.base / "ches-subject-batches" /
                     r["new_private_batch_snapshot_id"])
        self.assertTrue((directory / "batch-001.html").exists())
        self.assertTrue((directory / "batch-002.html").exists())
        self.assertEqual(len(json.loads(
            (directory / "UNAPPROVED-review-starter.json").read_text()
        )["rules"]), 4)
        self.assertEqual(original_before, {
            p.name: p.read_bytes() for p in self.source.iterdir()
        })

    def test_stale_or_edited_priority_report_fails_before_writing(self):
        self._make_priority()
        file = next((self.base / "ches-subject-triage").glob("*.json"))
        source_text = file.read_text()
        file.write_text(source_text.replace("Sailors", "Intruders"))
        file.chmod(0o600)
        with self.assertRaisesRegex(
            DanMek032Error, "PRIVATE_PRIORITY_JSON_CONTENT_CHANGED",
        ):
            build_private_p1_batches(self.source, write_private_batches=True)
        self.assertFalse((self.base / "ches-subject-batches").exists())

    def test_source_drift_blocks_old_report_even_with_same_verse_count(self):
        self._make_priority()
        chapter = invented_chapter("gen", 1)
        chapter["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan today"
        chapter["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(chapter, self.source / "gen.1.json")
        with self.assertRaisesRegex(
            DanMek032Error, "PRIVATE_PRIORITY_REPORT_STALE_OR_INCOMPLETE",
        ):
            build_private_p1_batches(self.source, write_private_batches=True)
        self.assertFalse((self.base / "ches-subject-batches").exists())

    def test_private_output_not_overwritten_if_edited_by_owner(self):
        self._make_priority()
        report = build_private_p1_batches(
            self.source, write_private_batches=True,
        )
        output = (self.base / "ches-subject-batches" /
                  report["new_private_batch_snapshot_id"] / "batch-001.html")
        output.write_text("OWNER_CUSTOM_HTML")
        output.chmod(0o600)
        with self.assertRaisesRegex(
            DanMek032Error, "PRIVATE_READING_NO_OVERWRITE",
        ):
            build_private_p1_batches(self.source, write_private_batches=True)
        self.assertEqual(output.read_text(), "OWNER_CUSTOM_HTML")

    def test_symlinked_private_report_parent_rejected(self):
        root = self.base / "ches-subject-triage"
        root.symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(
            DanMek032Error, "PRIVATE_PRIORITY_REPORT_DIRECTORY_MISSING_OR_UNSAFE",
        ):
            build_private_p1_batches(self.source)

    def test_reject_311_guard_and_unsafe_batch_size(self):
        self._make_priority()
        with self.assertRaisesRegex(
            DanMek032Error, "HISTORICAL_311",
        ):
            build_private_p1_batches(
                self.source, require_311=True, write_private_batches=True,
            )
        for count in (0, -1, 51, 1.0, True):
            with self.subTest(count=count), self.assertRaisesRegex(
                DanMek032Error, "INVALID_P1_BATCH_PARAMETERS",
            ):
                build_private_p1_batches(self.source, batch_size=count)

    def test_untrusted_english_escaped_without_scripts(self):
        chapter = invented_chapter("gen", 1)
        chapter["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan <img src=x onerror=alert(1)>"
        chapter["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(chapter, self.source / "gen.1.json")
        self._make_priority()
        report = build_private_p1_batches(
            self.source, write_private_batches=True,
        )
        text = (
            self.base / "ches-subject-batches" /
            report["new_private_batch_snapshot_id"] / "batch-001.html"
        ).read_text()
        self.assertIn("&lt;img", text)
        self.assertNotIn("<img", text)

    def test_cli_metadata_only_never_displays_private_verse_text(self):
        self._make_priority()
        with patch("sys.argv", [
            "danmek-032", "--private-root", str(self.source),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        result = json.loads(out.getvalue())
        self.assertEqual(result["historical_p1_candidate_pairs"], 2)
        self.assertEqual(result["subject_corrections_approved_by_this_tool"], 0)
        for value in ("Sailors", "Rowan", "Worker", "gen.1.1",
                      str(self.source)):
            self.assertNotIn(value, out.getvalue())


if __name__ == "__main__":
    unittest.main()
