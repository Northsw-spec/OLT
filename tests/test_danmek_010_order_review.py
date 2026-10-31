"""DANMEK-010: private scan/review tests use INVENTED English only."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_015_direct_private_reader import build_private_reader
from scripts.ches_import import write_private_json
from scripts.danmek_009_english_order import load_private_order_rules
from scripts.danmek_010_order_review import (
    DanMek010Error, approve_private_candidate,
    discover_candidates, main, scan_private_order_candidates,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek010PrivateCandidateReview(unittest.TestCase):
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
            "page": 1, "pdf_x": 26, "pdf_y": 6,
            "original_ches_line_text": "Leader",
        })
        second = doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"]
        second[0]["original_ches_line_text"] = "he-is-making Worker the·work"
        doc["ches_pdf_green_spans"] = 3
        self.path = self.folder / "gen.1.json"
        write_private_json(doc, self.path)

    def test_detects_candidates_but_never_attests_automatically(self):
        sha = hashlib.sha256(self.path.read_bytes()).hexdigest()
        adjacent, multiple = discover_candidates(
            "gen.1.1", sha, ["and·he-shaped", "Leader"],
        )
        self.assertFalse(multiple)
        self.assertEqual(len(adjacent), 1)
        self.assertEqual(adjacent[0]["mode"], "adjacent")
        self.assertFalse(adjacent[0]["source_syntax_reviewed"])
        inline, multiple = discover_candidates(
            "gen.1.2", sha, ["he-is-making Worker the·work"],
        )
        self.assertFalse(multiple)
        self.assertEqual(len(inline), 1)
        self.assertEqual(inline[0]["mode"], "inline")
        self.assertEqual(inline[0]["original_subject"], "Worker")
        glued, ambiguous = discover_candidates(
            "gen.1.4", sha, ["and·he-is-buildingLeader»the·house"],
        )
        self.assertFalse(ambiguous)
        self.assertEqual(len(glued), 1)
        self.assertEqual(glued[0]["original_verb"], "and·he-is-building")
        self.assertEqual(glued[0]["original_subject"], "Leader")
        self.assertEqual(
            discover_candidates("gen.1.3", sha, ["door", "wall"]),
            ([], False),
        )
        self.assertEqual(
            discover_candidates("gen.1.3", sha,
                                ["he-is-making Worker", "she-is-making Leader"]),
            ([], True),
        )

    def test_audit_only_does_not_create_any_output_or_leak_words(self):
        original = self.path.read_bytes()
        with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            report = scan_private_order_candidates(self.folder)
        self.assertEqual(report["chapters_scanned"], 1)
        self.assertEqual(report["verses_scanned"], 2)
        self.assertEqual(report["eligible_single_candidate_verses"], 2)
        self.assertEqual(report["candidates_saved"], 2)
        self.assertEqual(report["candidates_automatically_approved"], 0)
        self.assertEqual(report["private_review_files_written_or_verified"], 0)
        self.assertFalse(report["source_syntax_independently_verified"])
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse((self.base / "olt-english-order").exists())
        report_text = json.dumps(report)
        self.assertNotIn("Leader", report_text)
        self.assertNotIn(str(self.folder), report_text)

    def test_private_html_preview_is_immutable_and_escapes_markup(self):
        original = self.path.read_bytes()
        with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            report = scan_private_order_candidates(self.folder, build_review=True)
        review = self.base / "olt-english-order" / report["review_id"]
        html_text = (review / "review.html").read_text()
        data = json.loads((review / "candidates.json").read_text())
        self.assertIn("and Leader —", html_text)
        self.assertIn("he-is-making Worker", html_text)
        self.assertIn("Worker — he-is-making", html_text)
        self.assertEqual(len(data["candidates"]), 2)
        self.assertFalse(data["candidates"][0]["source_syntax_reviewed"])
        self.assertFalse((self.base / "olt-english-order" / "approved.json").exists())
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(review.stat().st_mode & 0o777, 0o700)
        self.assertEqual((review / "review.html").stat().st_mode & 0o777, 0o600)
        self.assertEqual(
            scan_private_order_candidates(
                self.folder, build_review=True,
            )["review_id"], report["review_id"],
        )
        (review / "review.html").write_text("OWNER NOTE KEEP", encoding="utf-8")
        with self.assertRaises(DanMek010Error):
            scan_private_order_candidates(self.folder, build_review=True)
        self.assertEqual((review / "review.html").read_text(), "OWNER NOTE KEEP")

    def test_approval_requires_explicit_attestation_and_creates_usable_rule(self):
        raw_source = self.path.read_bytes()
        report = scan_private_order_candidates(self.folder, build_review=True)
        review_id = report["review_id"]
        with self.assertRaises(DanMek010Error):
            approve_private_candidate(
                self.folder, review_id=review_id,
                reference="gen.1.1", review_note="Source grammar reviewed",
            )
        self.assertFalse((self.base / "olt-english-order" / "approved.json").exists())
        approved = approve_private_candidate(
            self.folder, review_id=review_id, reference="gen.1.1",
            review_note="Synthetic Hebrew syntax attestation test only",
            original_language_review_attested=True,
        )
        self.assertEqual(approved["approved_rule_count"], 1)
        self.assertFalse(approved["source_syntax_independently_machine_verified"])
        self.assertEqual(raw_source, self.path.read_bytes())
        rules, _ = load_private_order_rules(self.folder)
        self.assertEqual(list(rules), ["gen.1.1"])
        self.assertTrue(rules["gen.1.1"]["source_syntax_reviewed"])
        rendered = build_private_reader(
            self.folder, render=True, olt_subject_first=True,
        )
        self.assertEqual(rendered["olt_subject_first_reviewed_rules_applied"], 1)
        self.assertEqual(rendered["olt_subject_first_other_verses_left_unchanged"], 1)
        html_text = (self.base / "ches-direct-reader" /
                     rendered["snapshot_id"] / "gen.1.html").read_text()
        self.assertIn("and Leader —", html_text)
        self.assertIn("he-is-making Worker", html_text)
        self.assertNotIn("He-shaped", html_text)
        self.assertEqual(raw_source, self.path.read_bytes())
        with self.assertRaises(DanMek010Error):
            approve_private_candidate(
                self.folder, review_id=review_id, reference="gen.1.1",
                review_note="Duplicate review attestation again",
                original_language_review_attested=True,
            )

    def test_approval_preserves_prior_approved_as_immutable_backup(self):
        review_id = scan_private_order_candidates(
            self.folder, build_review=True,
        )["review_id"]
        approve_private_candidate(
            self.folder, review_id=review_id, reference="gen.1.1",
            review_note="Synthetic original-language evidence for first entry",
            original_language_review_attested=True,
        )
        path = self.base / "olt-english-order" / "approved.json"
        original_approval = path.read_bytes()
        approve_private_candidate(
            self.folder, review_id=review_id, reference="gen.1.2",
            review_note="Synthetic original-language evidence for second entry",
            original_language_review_attested=True,
        )
        rules, _ = load_private_order_rules(self.folder)
        self.assertEqual(len(rules), 2)
        backups = list(path.parent.glob("approved-backup-*.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original_approval)
        self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)

    def test_changed_source_rejected_at_approval(self):
        review_id = scan_private_order_candidates(
            self.folder, build_review=True,
        )["review_id"]
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "a totally different synthetic phrase"
        write_private_json(doc, self.path)
        with self.assertRaises(DanMek010Error):
            approve_private_candidate(
                self.folder, review_id=review_id,
                reference="gen.1.1",
                review_note="This old candidate must not get approved",
                original_language_review_attested=True,
            )
        self.assertFalse(
            (self.base / "olt-english-order" / "approved.json").exists(),
        )

    def test_ambiguous_verse_and_limit_are_explicit(self):
        doc = invented_chapter("gen", 1)
        first = doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
        first[0]["original_ches_line_text"] = "he-is-building Leader"
        first.append({
            "page": 1, "pdf_x": 17, "pdf_y": 6,
            "original_ches_line_text": "she-is-building Worker",
        })
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-building Leader"
        doc["ches_pdf_green_spans"] = 3
        write_private_json(doc, self.path)
        report = scan_private_order_candidates(self.folder, max_saved=1)
        self.assertEqual(report["ambiguous_candidate_verses_left_unchanged"], 1)
        self.assertEqual(report["eligible_single_candidate_verses"], 1)
        self.assertEqual(report["candidates_saved"], 1)
        # Snapshot identity depends on the cap and cannot collide with
        # a different queue length on the same chapter source.
        a = scan_private_order_candidates(self.folder, max_saved=1)
        b = scan_private_order_candidates(self.folder, max_saved=2)
        self.assertNotEqual(a["review_id"], b["review_id"])

    def test_cli_count_only_privacy_and_validation(self):
        with patch("sys.argv", [
            "order-review", "--private-root", str(self.folder),
            "--confirm-machine-readable-use-permission", "--build-review",
            "--book-prefix", "gen", "--chapter", "1",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["candidates_saved"], 2)
        self.assertNotIn("Leader", output.getvalue())
        self.assertNotIn("he-is", output.getvalue())
        self.assertNotIn(str(self.folder), output.getvalue())
        with patch("sys.argv", [
            "order-review", "--private-root", str(self.folder),
            "--confirm-machine-readable-use-permission",
            "--approve-reference", "gen.1.1",
            "--review-id", report["review_id"],
            "--review-note", "Reviewed original-language syntax evidence",
            "--attest-original-language-syntax-reviewed",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        self.assertEqual(
            json.loads(output.getvalue())["approved_rule_count"], 1,
        )
        with self.assertRaises(DanMek010Error):
            scan_private_order_candidates(self.folder, chapter_filter=1)
        with self.assertRaises(DanMek010Error):
            scan_private_order_candidates(self.folder, max_saved=20_000)

    def test_symlinked_review_file_rejected_before_approval(self):
        report = scan_private_order_candidates(self.folder, build_review=True)
        review = self.base / "olt-english-order" / report["review_id"]
        data = review / "candidates.json"
        target = self.base / "copy.json"
        target.write_bytes(data.read_bytes())
        data.unlink()
        data.symlink_to(target)
        with self.assertRaises(DanMek010Error):
            approve_private_candidate(
                self.folder, review_id=report["review_id"],
                reference="gen.1.1",
                review_note="Original-language syntax thoroughly reviewed",
                original_language_review_attested=True,
            )
        self.assertFalse(
            (self.base / "olt-english-order" / "approved.json").exists(),
        )

    def test_html_escape_no_raw_markup_in_review(self):
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-shaping Leader <script>alert(1)</script>"
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "No candidate"
        write_private_json(doc, self.path)
        report = scan_private_order_candidates(self.folder, build_review=True)
        html_text = (self.base / "olt-english-order" / report["review_id"] /
                     "review.html").read_text()
        self.assertIn("&lt;script&gt;", html_text)
        self.assertNotIn("<script>", html_text)


if __name__ == "__main__":
    unittest.main()
