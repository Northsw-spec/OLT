"""DANMEK-009 regressions: invented data only, no licensed CHES text."""
from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_015_direct_private_reader import (
    CHES015ReaderError, build_private_reader, main,
)
from scripts.ches_import import write_private_json
from scripts.danmek_009_english_order import (
    DanMek009Error, SCHEMA, apply_reviewed_order, load_private_order_rules,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek009PrivateOrder(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / ".olt-private"
        self.root.mkdir(mode=0o700)
        self.chapters = self.root / "ches"
        self.chapters.mkdir(mode=0o700)
        self.rules = self.root / "olt-english-order"
        self.rules.mkdir(mode=0o700)

        # Only invented, non-biblical grammar fragments are used in public CI.
        doc = invented_chapter("gen", 1)
        first = doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
        first[0]["original_ches_line_text"] = "and·he-shaped"
        first.append({
            "page": 1, "pdf_x": 28.0, "pdf_y": 6.0,
            "original_ches_line_text": "Leader",
        })
        second = doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"]
        second[0]["original_ches_line_text"] = "he-is-making Worker the·work"
        doc["ches_pdf_green_spans"] = 3
        self.source = self.chapters / "gen.1.json"
        write_private_json(doc, self.source)
        self.sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.rules_data = {
            "schema": SCHEMA,
            "rules": [
                {
                    "reference": "gen.1.1",
                    "chapter_json_sha256": self.sha,
                    "mode": "adjacent",
                    "source_syntax_reviewed": True,
                    "review_note": "Synthetic clause roles reviewed for the test",
                    "verb_fragment_index": 1,
                    "subject_fragment_index": 2,
                    "original_verb": "and·he-shaped",
                    "original_subject": "Leader",
                },
                {
                    "reference": "gen.1.2",
                    "chapter_json_sha256": self.sha,
                    "mode": "inline",
                    "source_syntax_reviewed": True,
                    "review_note": "Synthetic clause roles reviewed for the test",
                    "verb_fragment_index": 1,
                    "original_verb": "he-is-making",
                    "original_subject": "Worker",
                    "original_fragment": "he-is-making Worker the·work",
                },
            ],
        }

    def save_rules(self):
        path = self.rules / "approved.json"
        path.write_text(json.dumps(self.rules_data), encoding="utf-8")
        path.chmod(0o600)
        return path

    def test_separate_reading_snapshot_reorders_two_verified_synthetic_cases(self):
        original_bytes = self.source.read_bytes()
        self.save_rules()
        with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            faithful = build_private_reader(self.chapters, render=True)
            reordered = build_private_reader(
                self.chapters, render=True, olt_subject_first=True,
            )
        self.assertNotEqual(faithful["snapshot_id"], reordered["snapshot_id"])
        self.assertEqual(reordered["mode"], "PRIVATE_OLT_ENGLISH_DISPLAY")
        self.assertEqual(reordered["olt_subject_first_reviewed_rules_applied"], 2)
        self.assertEqual(reordered["olt_subject_first_other_verses_left_unchanged"], 0)
        self.assertFalse(reordered["olt_subject_first_original_language_alignment_independently_verified"])
        self.assertFalse(reordered["independent_english_olt_translation_produced"])
        self.assertEqual(reordered["publication_status"], "BLOCKED")
        self.assertEqual(original_bytes, self.source.read_bytes())
        root = self.root / "ches-direct-reader"
        old = (root / faithful["snapshot_id"] / "gen.1.html").read_text()
        new = (root / reordered["snapshot_id"] / "gen.1.html").read_text()
        self.assertIn('>and·he-shaped</span><span class="gloss">Leader</span>', old)
        self.assertIn('>and Leader — </span><span class="gloss">he-shaped</span>', new)
        self.assertIn('>Worker — he-is-making the·work</span>', new)
        self.assertIn("he-is-making Worker the·work", old)
        self.assertEqual(
            build_private_reader(
                self.chapters, render=True, olt_subject_first=True,
            )["snapshot_id"], reordered["snapshot_id"],
        )

    def test_no_rules_does_not_guess_or_reorder(self):
        faithful = build_private_reader(self.chapters, render=True)
        self.assertEqual(faithful["olt_subject_first_reviewed_rules_applied"], 0)
        self.assertFalse(faithful["olt_subject_first_enabled"])
        self.assertIn(
            ">and·he-shaped</span><span class=\"gloss\">Leader</span>",
            (self.root / "ches-direct-reader" / faithful["snapshot_id"] /
             "gen.1.html").read_text(),
        )
        with self.assertRaises(CHES015ReaderError):
            build_private_reader(self.chapters, render=True, olt_subject_first=True)

    def test_case_of_religious_referent_is_not_changed(self):
        rule = {
            "chapter_json_sha256": self.sha, "mode": "adjacent",
            "verb_fragment_index": 1, "subject_fragment_index": 2,
            "original_verb": "and·he-works", "original_subject": "God",
        }
        result, count = apply_reviewed_order(
            reference="gen.1.1", chapter_sha256=self.sha,
            original=["and·he-works", "God"],
            visible=["and·he-works", "God"], rules={"gen.1.1": rule},
        )
        self.assertEqual((result, count), (["and God — ", "he-works"], 1))
        self.assertNotIn("He-works", "".join(result))

    def test_ambiguous_or_changed_anchors_fail_closed(self):
        self.save_rules()
        rules, _ = load_private_order_rules(self.chapters)
        for case in (
            ["and·he-shapED", "Leader"],
            ["and·he-shaped", "Another"],
        ):
            with self.subTest(case=case), self.assertRaises(DanMek009Error):
                apply_reviewed_order(
                    reference="gen.1.1", chapter_sha256=self.sha,
                    original=case, visible=case, rules=rules,
                )
        with self.assertRaises(DanMek009Error):
            apply_reviewed_order(
                reference="gen.1.1", chapter_sha256="a" * 64,
                original=["and·he-shaped", "Leader"],
                visible=["and·he-shaped", "Leader"], rules=rules,
            )
        with self.assertRaises(DanMek009Error):
            apply_reviewed_order(
                reference="gen.1.1", chapter_sha256=self.sha,
                original=["and·he-shaped", "Leader"],
                visible=["YLT-updated", "Leader"], rules=rules,
            )
        self.assertEqual(
            apply_reviewed_order(
                reference="gen.1.999", chapter_sha256=self.sha,
                original=["nothing"], visible=["nothing"], rules=rules,
            ), (["nothing"], 0),
        )

    def test_invalid_manifest_fails_before_writing_a_derived_snapshot(self):
        def verify_bad():
            self.save_rules()
            with self.assertRaises(CHES015ReaderError):
                build_private_reader(
                    self.chapters, render=True, olt_subject_first=True,
                )
            self.assertFalse((self.root / "ches-direct-reader").exists())
        self.rules_data["rules"][0]["chapter_json_sha256"] = "f" * 64
        verify_bad()
        self.rules_data["rules"][0]["chapter_json_sha256"] = self.sha
        self.rules_data["rules"][0]["original_subject"] = "Unknown"
        verify_bad()
        self.rules_data["rules"][0]["original_subject"] = "Leader"
        self.rules_data["rules"][1]["reference"] = "gen.1.999"
        verify_bad()

    def test_duplicate_reference_boolean_index_and_missing_review_are_rejected(self):
        for mutate in ("duplicate", "bool_index", "not_reviewed", "not_adjacent",
                       "blank_note", "extra_field"):
            self.setUp()
            if mutate == "duplicate":
                self.rules_data["rules"][1]["reference"] = "gen.1.1"
            elif mutate == "bool_index":
                self.rules_data["rules"][0]["verb_fragment_index"] = True
            elif mutate == "not_reviewed":
                self.rules_data["rules"][0]["source_syntax_reviewed"] = False
            elif mutate == "not_adjacent":
                self.rules_data["rules"][0]["subject_fragment_index"] = 3
            elif mutate == "blank_note":
                self.rules_data["rules"][0]["review_note"] = " "
            else:
                self.rules_data["rules"][0]["unverified"] = "guess"
            self.save_rules()
            with self.subTest(mutate=mutate), self.assertRaises(DanMek009Error):
                load_private_order_rules(self.chapters)

    def test_symlink_and_unsafe_manifest_perms_rejected(self):
        path = self.save_rules()
        path.chmod(0o644)
        with self.assertRaises(DanMek009Error):
            load_private_order_rules(self.chapters)
        path.chmod(0o600)
        path.unlink()
        outside = self.root / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        path.symlink_to(outside)
        with self.assertRaises(DanMek009Error):
            load_private_order_rules(self.chapters)

    def test_combined_faces_and_order_snapshot_and_private_cli_counts(self):
        self.save_rules()
        argv = [
            "reader", "--private-root", str(self.chapters),
            "--confirm-machine-readable-use-permission",
            "--audit-only", "--olt-subject-first", "--olt-display-faces",
        ]
        with patch("sys.argv", argv):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["olt_subject_first_reviewed_rules_applied"], 2)
        self.assertEqual(report["olt_display_sur_faces_to_faces_count"], 0)
        self.assertNotIn("Worker", out.getvalue())
        self.assertNotIn("Leader", out.getvalue())
        self.assertNotIn(str(self.chapters), out.getvalue())
        self.assertFalse((self.root / "ches-direct-reader").exists())


if __name__ == "__main__":
    unittest.main()
