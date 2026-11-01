"""DANMEK-031 tests: private 311-first triage with invented English only."""
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
from scripts.danmek_029_private_english_clause_review import (
    OBJECT_RISK, UNRESOLVED,
)
from scripts.danmek_031_private_english_priority_triage import (
    DanMek031Error, HISTORICAL_WITH_PAIRS, HISTORICAL_NO_PAIRS,
    OTHER_OBJECT_RISK, OTHER_UNRESOLVED, classify_private_priority,
    triage_private_english_roles, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek031PrivatePriorityTriage(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.folder = self.base / "ches"
        self.folder.mkdir(mode=0o700)
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(gen, self.folder / "gen.1.json")
        self.original = (self.folder / "gen.1.json").read_bytes()
        self.baseline = build_private_reader(
            self.folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        self.assertEqual(
            self.baseline["olt_owner_candidate_ambiguous_verses_unchanged"], 1
        )

    def test_priority_classes_and_none_do_not_approve_subjects(self):
        self.assertEqual(classify_private_priority(
            historical=True, candidate_classes=[OBJECT_RISK, UNRESOLVED],
        ), HISTORICAL_WITH_PAIRS)
        self.assertEqual(classify_private_priority(
            historical=True, candidate_classes=[],
        ), HISTORICAL_NO_PAIRS)
        self.assertEqual(classify_private_priority(
            historical=False, candidate_classes=[OBJECT_RISK],
        ), OTHER_OBJECT_RISK)
        self.assertEqual(classify_private_priority(
            historical=False, candidate_classes=[UNRESOLVED],
        ), OTHER_UNRESOLVED)
        self.assertIsNone(classify_private_priority(
            historical=False, candidate_classes=[],
        ))
        for wrong in ("CERTIFIED_SUBJECT", "CERTIFIED_OBJECT"):
            with self.assertRaises(DanMek031Error):
                classify_private_priority(
                    historical=False, candidate_classes=[wrong],
                )

    def test_aggregate_reports_historical_overlap_without_mutating_sources(self):
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_NOT_ALLOWED")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("HEBREW_REGISTRY_NOT_ALLOWED")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NETWORK_NOT_ALLOWED")),
        ):
            report = triage_private_english_roles(self.folder)
        self.assertEqual(report["source_chapters_scanned"], 1)
        self.assertEqual(report["source_verses_scanned"], 2)
        self.assertEqual(report["historical_english_ambiguities_seen"], 1)
        self.assertEqual(report["all_role_candidates"], 3)
        self.assertEqual(report["historical_verses_with_role_candidates"], 1)
        self.assertEqual(report["historical_verses_without_role_candidates"], 0)
        self.assertEqual(report["historical_role_candidates"], 2)
        self.assertEqual(report["additional_nonhistorical_role_candidates"], 1)
        self.assertEqual(report["review_verses_queued"], 2)
        self.assertEqual(report["priority_verse_counts"], {
            HISTORICAL_WITH_PAIRS: 1,
            HISTORICAL_NO_PAIRS: 0,
            OTHER_OBJECT_RISK: 1,
            OTHER_UNRESOLVED: 0,
        })
        self.assertEqual(report["role_candidate_counts"], {OBJECT_RISK: 3})
        self.assertEqual(report["approved_grammar_corrections"], 0)
        self.assertFalse(report["hebrew_translation_crosscheck_performed"])
        self.assertFalse(report["source_ches_edited"])
        self.assertFalse(report["locked_readers_edited"])
        self.assertEqual(report["mode"], "AGGREGATE_ONLY_NO_FILES")
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertFalse((self.base / "ches-subject-triage").exists())
        self.assertEqual(self.original, (self.folder / "gen.1.json").read_bytes())
        self.assertEqual(self.baseline, build_private_reader(
            self.folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ))

    def test_private_report_orders_historical_first_and_contains_no_approvals(self):
        result = triage_private_english_roles(
            self.folder, write_private_report=True,
        )
        self.assertEqual(result["mode"], "PRIVATE_PRIORITY_REPORT_UNAPPROVED")
        self.assertEqual(result["private_report_files_written_or_verified"], 2)
        dest = self.base / "ches-subject-triage"
        files = sorted(dest.iterdir())
        self.assertEqual(len(files), 2)
        self.assertEqual(dest.stat().st_mode & 0o777, 0o700)
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600 for p in files))
        json_doc = json.loads(
            next(p for p in files if p.suffix == ".json").read_text()
        )
        self.assertTrue(json_doc["all_cases_unapproved"])
        self.assertEqual(
            json_doc["source_owner_reader_snapshot"],
            self.baseline["snapshot_id"],
        )
        self.assertEqual([c["review_priority"] for c in json_doc["cases"]],
                         [HISTORICAL_WITH_PAIRS, OTHER_OBJECT_RISK])
        self.assertEqual([c["candidate_count"] for c in json_doc["cases"]],
                         [2, 1])
        self.assertTrue(all(
            c["all_candidates_unapproved"] and
            not c["correction_automatically_applied"] and
            all(not item["english_subject_role_reviewed"] for item in c["candidates"])
            for c in json_doc["cases"]
        ))
        html_doc = next(p for p in files if p.suffix == ".html").read_text()
        self.assertIn("he-saw Sailors", html_doc)
        self.assertLess(html_doc.index(HISTORICAL_WITH_PAIRS),
                        html_doc.index(OTHER_OBJECT_RISK))
        self.assertIn("default-src 'none'", html_doc)
        self.assertNotIn("<script", html_doc)
        again = triage_private_english_roles(
            self.folder, write_private_report=True,
        )
        self.assertEqual(again["private_report_files_written_or_verified"], 2)
        self.assertEqual(len(list(dest.iterdir())), 2)
        self.assertEqual(self.original, (self.folder / "gen.1.json").read_bytes())

    def test_reject_311_mismatch_before_creating_private_files(self):
        with self.assertRaisesRegex(
            DanMek031Error, "HISTORICAL_311_ENGLISH_CASE_COUNT_CHANGED",
        ):
            triage_private_english_roles(
                self.folder, require_311=True, write_private_report=True,
            )
        self.assertFalse((self.base / "ches-subject-triage").exists())

    def test_reject_symlink_and_preserve_owner_edited_report(self):
        parent = self.base / "ches-subject-triage"
        parent.symlink_to(self.folder, target_is_directory=True)
        with self.assertRaises(DanMek031Error):
            triage_private_english_roles(
                self.folder, write_private_report=True,
            )
        parent.unlink()
        triage_private_english_roles(self.folder, write_private_report=True)
        target = next(parent.glob("*.json"))
        target.write_text("PRIVATE_OWNER_CHANGE_MUST_SURVIVE")
        target.chmod(0o600)
        with self.assertRaises(DanMek031Error):
            triage_private_english_roles(
                self.folder, write_private_report=True,
            )
        self.assertEqual(target.read_text(), "PRIVATE_OWNER_CHANGE_MUST_SURVIVE")

    def test_html_escapes_untrusted_private_english(self):
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan <img src=x onerror=alert(1)>"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(gen, self.folder / "gen.1.json")
        triage_private_english_roles(
            self.folder, write_private_report=True,
        )
        page = next((self.base / "ches-subject-triage").glob("*.html")).read_text()
        self.assertIn("&lt;img", page)
        self.assertNotIn("<img", page)

    def test_cli_stdout_aggregate_only_and_no_private_paths(self):
        with patch("sys.argv", [
            "danmek-031", "--private-root", str(self.folder),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            stream = io.StringIO()
            with redirect_stdout(stream):
                self.assertEqual(main(), 0)
        report = json.loads(stream.getvalue())
        self.assertEqual(report["all_role_candidates"], 3)
        for forbidden in ("Sailors", "Rowan", "gen.1.1", str(self.folder)):
            self.assertNotIn(forbidden, stream.getvalue())
        self.assertFalse((self.base / "ches-subject-triage").exists())


if __name__ == "__main__":
    unittest.main()
