"""DANMEK-025 synthetic-only regression and security tests.

No real CHES English or imported Hebrew/Aramaic corpus is used in CI.
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
from scripts.danmek_025_private_english_grammar import (
    DanMek025Error, inspect_english_fragments,
    review_private_english_grammar, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek025GrammarReview(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "He are making a lantern."
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "And the lantern — the worker saw."
        exo = invented_chapter("exo", 1, source_sha="f" * 64)
        exo["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker she-is-building Leader"
        exo["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "Thou art resting; they are singing."
        write_private_json(gen, self.source / "gen.1.json")
        write_private_json(exo, self.source / "exo.1.json")
        self.original_bytes = {
            p.name: p.read_bytes() for p in self.source.iterdir()
        }
        self.baseline = build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        self.assertEqual(
            self.baseline["olt_owner_candidate_ambiguous_verses_unchanged"], 1
        )

    def test_tiny_english_agreement_rules_propose_only_verbs(self):
        tests = [
            (["He are here."], ["He is here."], 1),
            (["She am here."], ["She is here."], 1),
            (["I is here."], ["I am here."], 1),
            (["We is here."], ["We are here."], 1),
            (["They is here."], ["They are here."], 1),
            (["You is here."], ["You are here."], 1),
            (["Thou is here."], ["Thou art here."], 1),
            (["He", "are here."], ["He", "is here."], 1),
            (["And God — He are here."], ["And God — He is here."], 1),
            (["He are", " and they is here."],
             ["He is", " and they are here."], 2),
            (["And the lantern — the worker saw."],
             ["And the lantern — the worker saw."], 0),
            (["He is here; thou art here; they are here."],
             ["He is here; thou art here; they are here."], 0),
            (["If he were here."], ["If he were here."], 0),
            (["and·he-is-making"], ["and·he-is-making"], 0),
            (["he-is-making Worker she-is-building Leader"],
             ["he-is-making Worker she-is-building Leader"], 0),
        ]
        for before, expected, count in tests:
            with self.subTest(before=before):
                proposed, findings = inspect_english_fragments(before)
                self.assertEqual(proposed, expected)
                self.assertEqual(len(findings), count)
                self.assertEqual(before, before)  # original not mutated
                for item in findings:
                    self.assertFalse(item["reorder_proposed"])
                    self.assertFalse(item["hebrew_crosscheck_performed"])
                    self.assertEqual(
                        item["editorial_status"],
                        "PROPOSED_UNVERIFIED_NEEDS_OWNER_REVIEW",
                    )

    def test_read_only_scan_311_are_english_candidates_not_hebrew_errors(self):
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_SOURCE_FORBIDDEN")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("HEBREW_REGISTRY_FORBIDDEN")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NETWORK_FORBIDDEN")),
        ):
            result = review_private_english_grammar(self.source)
        self.assertEqual(result["verses_scanned"], 4)
        self.assertEqual(result["historic_311_regex_ambiguities_seen"], 1)
        self.assertEqual(result["ambiguities_without_bounded_grammar_candidate"], 1)
        self.assertEqual(result["english_grammar_candidates_unverified"], 1)
        self.assertEqual(result["review_case_records"], 2)
        self.assertEqual(
            result["candidate_reason_counts"],
            {"ENGLISH_FINITE_BE_PRONOUN_AGREEMENT_CANDIDATE": 1},
        )
        self.assertFalse(result["ches_vs_hebrew_revalidation_performed"])
        self.assertFalse(result["owner_verified_english_reader_modified"])
        self.assertFalse(result["unflagged_verses_grammar_certified"])
        self.assertEqual(result["automatically_applied_edits"], 0)
        self.assertEqual(result["publication_status"], "BLOCKED")
        self.assertEqual(
            result["private_output_status"],
            "AUDIT_ONLY_NO_PRIVATE_REPORT_WRITTEN",
        )
        self.assertFalse((self.base / "ches-grammar-review").exists())
        self.assertEqual(self.original_bytes, {
            p.name: p.read_bytes() for p in self.source.iterdir()
        })
        self.assertEqual(
            self.baseline,
            build_private_reader(
                self.source, render=False, olt_display_faces=True,
                olt_owner_approved_candidates=True,
            ),
        )

    def test_private_json_html_proposals_are_immutable_and_escaped(self):
        report = review_private_english_grammar(
            self.source, write_private_report=True,
        )
        self.assertEqual(report["private_output_status"], "NEW_PRIVATE_REPORT")
        folder = self.base / "ches-grammar-review"
        self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        files = sorted(folder.iterdir())
        self.assertEqual(len(files), 2)
        self.assertEqual({f.suffix for f in files}, {".json", ".html"})
        self.assertTrue(all(f.stat().st_mode & 0o777 == 0o600 for f in files))
        body = json.loads(next(f for f in files if f.suffix == ".json").read_text())
        self.assertEqual(body["scope"], "PRIVATE_ENGLISH_GRAMMAR_ONLY")
        self.assertFalse(body["hebrew_or_aramaic_accuracy_comparison_performed"])
        self.assertFalse(body["grammar_certification_of_complete_corpus"])
        self.assertEqual(len(body["cases"]), 2)
        found = next(r for r in body["cases"] if r["reference"] == "gen.1.1")
        self.assertEqual(found["before_fragments"], ["He are making a lantern."])
        self.assertEqual(found["proposed_fragments"], ["He is making a lantern."])
        self.assertFalse(found["changes_applied_to_reader"])
        self.assertFalse(found["owner_approved"])
        ambiguous = next(r for r in body["cases"] if r["reference"] == "exo.1.1")
        self.assertEqual(ambiguous["status"], "GRAMMAR_UNRESOLVED_NO_REORDER")
        self.assertEqual(ambiguous["before_fragments"],
                         ambiguous["proposed_fragments"])
        page = next(f for f in files if f.suffix == ".html").read_text()
        self.assertIn("He are making a lantern.", page)
        self.assertIn("He is making a lantern.", page)
        self.assertIn("default-src 'none'", page)
        self.assertNotIn("<script", page)
        self.assertNotIn("<form", page)
        again = review_private_english_grammar(
            self.source, write_private_report=True,
        )
        self.assertEqual(again["private_output_status"],
                         "EXISTING_IDENTICAL_PRIVATE_REPORT")
        self.assertEqual(self.original_bytes, {
            p.name: p.read_bytes() for p in self.source.iterdir()
        })

    def test_xss_escaped_in_private_html(self):
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "He are <img src=x onerror=alert(1)> here."
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "Normal invented text"
        write_private_json(gen, self.source / "gen.1.json")
        review_private_english_grammar(self.source, write_private_report=True)
        page = next((self.base / "ches-grammar-review").glob("*.html")).read_text()
        self.assertIn("&lt;img", page)
        self.assertNotIn("<img", page)
        self.assertNotIn("<script", page)

    def test_refuses_require_311_with_no_side_effects(self):
        with self.assertRaisesRegex(DanMek025Error,
                                    "ENGLISH_GRAMMAR_EXPECTED_311_MISMATCH"):
            review_private_english_grammar(
                self.source, require_311=True, write_private_report=True,
            )
        self.assertFalse((self.base / "ches-grammar-review").exists())

    def test_existing_owner_edited_private_report_not_overwritten(self):
        review_private_english_grammar(self.source, write_private_report=True)
        file = next((self.base / "ches-grammar-review").glob("*.json"))
        file.write_text("OWNER_EDIT_DO_NOT_OVERWRITE", encoding="utf-8")
        with self.assertRaisesRegex(DanMek025Error,
                                    "PRIVATE_GRAMMAR_REPORT_NO_OVERWRITE"):
            review_private_english_grammar(self.source, write_private_report=True)
        self.assertEqual(file.read_text(), "OWNER_EDIT_DO_NOT_OVERWRITE")

    def test_reject_unsafe_report_folder_and_source_symlink(self):
        target = self.base / "ches-grammar-review"
        target.mkdir(mode=0o700)
        target.chmod(0o755)
        with self.assertRaisesRegex(DanMek025Error,
                                    "PRIVATE_GRAMMAR_DIRECTORY_UNSAFE"):
            review_private_english_grammar(self.source, write_private_report=True)
        target.chmod(0o700)
        target.rmdir()
        source_file = self.source / "gen.1.json"
        original = source_file.read_bytes()
        source_file.unlink()
        source_file.symlink_to(self.source / "exo.1.json")
        with self.assertRaises(DanMek025Error):
            review_private_english_grammar(self.source, write_private_report=True)
        self.assertFalse(target.exists())
        source_file.unlink()
        source_file.write_bytes(original)
        source_file.chmod(0o600)

    def test_cli_outputs_aggregate_metadata_only(self):
        with (
            patch("sys.argv", [
                "danmek-025", "--private-root", str(self.source),
                "--confirm-machine-readable-use-permission",
            ]),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NO_NETWORK")),
        ):
            sink = io.StringIO()
            with redirect_stdout(sink):
                self.assertEqual(main(), 0)
        report = json.loads(sink.getvalue())
        self.assertEqual(report["english_grammar_candidates_unverified"], 1)
        for forbidden in ("He are", "lantern", "gen.1.1", str(self.source)):
            self.assertNotIn(forbidden, sink.getvalue())
        self.assertFalse((self.base / "ches-grammar-review").exists())

    def test_invalid_fragment_input_rejected_without_echo(self):
        for value in ([], ["ok", 123], "He are here"):
            with self.assertRaisesRegex(DanMek025Error, "INVALID_ENGLISH_FRAGMENT"):
                inspect_english_fragments(value)


if __name__ == "__main__":
    unittest.main()
