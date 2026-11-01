"""DANMEK-037 synthetic-only private clause-grammar regression tests."""
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
    DanMek037Error, SPEAKER_TO_RECIPIENT, INTRANSITIVE_SUBJECT,
    identify_unmarked_english_roles, apply_unmarked_english_roles,
    build_private_unmarked_clause_reader, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek037UnmarkedClauseRoles(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.root = self.base / "ches"
        self.root.mkdir(mode=0o700)
        self.speech = ["and·he-is-saying", "Rowan", "to", "Mira"]
        self.dying = [
            "and·she-is-dying", "Mira", "and·he-is-reigning",
        ]
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"] = [
            {"original_ches_line_text": v, "page": 1, "pdf_x": 20+i*15,
             "pdf_y": 80} for i, v in enumerate(self.speech)
        ]
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"] = [
            {"original_ches_line_text": v, "page": 1, "pdf_x": 20+i*15,
             "pdf_y": 95} for i, v in enumerate(self.dying)
        ]
        doc["ches_pdf_green_spans"] = 7
        write_private_json(doc, self.root / "gen.1.json")
        self.bytes = (self.root / "gen.1.json").read_bytes()
        self.old = build_private_reader(
            self.root, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )

    def test_named_speaker_with_explicit_recipient_not_named_person_specific(self):
        for src, expected in (
            (["and·he-is-saying", "Rowan", "to", "Mira"],
             "and Rowan -·he-is-saying to Mira"),
            (["he-said", "Natan", "to·Mira"],
             "Natan - he-said to·Mira"),
            (["and·she-is-", "speaking", "Talia", "to·listeners"],
             "and Talia -·she-is- speaking to·listeners"),
            (["and·he-is-says", "Rowan", "to", "Mira"], None),
        ):
            with self.subTest(src=src):
                after, evidence, counts = apply_unmarked_english_roles(
                    src, " ".join(src),
                )
                if expected is None:
                    self.assertEqual(evidence, [])
                    self.assertEqual(after, " ".join(src))
                else:
                    self.assertTrue(evidence)
                    self.assertEqual(evidence[0]["rule_code"],
                                     SPEAKER_TO_RECIPIENT)
                    self.assertEqual(after, expected)
                    self.assertEqual(counts["new_unmarked_grammar_moves"], 1)

    def test_bounded_intransitive_with_preposition_or_new_clause(self):
        for src, expected in (
            (["and·she-is-dying", "Mira", "and·he-is-reigning"],
             "and Mira -·she-is-dying and·he-is-reigning"),
            (["he-sits", "Natan", "in·his-house"],
             "Natan - he-sits in·his-house"),
            (["and·he-is-dwelling", "Rowan", "in·fort"],
             "and Rowan -·he-is-dwelling in·fort"),
            (["and·they-are-coming", "Sailors", "to·shore"],
             "and Sailors -·they-are-coming to·shore"),
        ):
            with self.subTest(src=src):
                new, evidence, _ = apply_unmarked_english_roles(
                    src, " ".join(src),
                )
                self.assertEqual(new, expected)
                self.assertEqual(len(evidence), 1)
                self.assertEqual(evidence[0]["rule_code"],
                                 INTRANSITIVE_SUBJECT)

    def test_excludes_infinitive_to_direct_object_and_compound_subjects(self):
        for source in (
            ["and·he-is-saying", "Rowan", "to·to-build-of", "»", "a·vessel"],
            ["and·he-is-taking", "Rowan", "to", "Mira"],
            ["and·he-is-seeing", "Natan", "to", "Mira"],
            ["and·he-is-dying", "Mira", "and·sons-of·her"],
            ["and·he-is-going", "Natan", "and·Mira"],
            ["and·he-is-saying", "I-saw", "to", "Rowan"],
            ["and·he-is-saying", "the·king", "to", "Rowan"],
            ["and·he-is-saying", "Rowan", "Elohim-of·him", "to·people"],
            ["and·he-is-", "making", "Natan", "to", "Mira"],
            ["and·he-is-", "saying", "Natan", "»", "the·city"],
        ):
            with self.subTest(source=source):
                self.assertEqual(identify_unmarked_english_roles(source), [])
                before = " ".join(source)
                after, moves, _ = apply_unmarked_english_roles(source, before)
                self.assertEqual(after, before)
                self.assertEqual(moves, [])

    def test_two_distinct_clause_moves_do_not_conflict(self):
        seq = (
            ["and·he-is-saying", "Rowan", "to", "Mira"] +
            ["and·she-is-dying", "Talia", "and·he-is-coming"]
        )
        new, moves, totals = apply_unmarked_english_roles(seq, " ".join(seq))
        self.assertEqual(len(moves), 2)
        self.assertEqual(totals["new_unmarked_grammar_candidates"], 2)
        self.assertIn("and Rowan -·he-is-saying to Mira", new)
        self.assertIn("and Talia -·she-is-dying and·he-is-coming", new)

    def test_adjacent_finite_clauses_each_with_subject_do_not_overlap(self):
        fragments = [
            "and·he-is-dying", "Mira",
            "and·he-is-reigning", "Rowan",
        ]
        actual, changes, counts = apply_unmarked_english_roles(
            fragments, " ".join(fragments),
        )
        self.assertEqual(counts["new_unmarked_grammar_candidates"], 2)
        self.assertEqual(counts["new_unmarked_grammar_moves"], 2)
        self.assertEqual(counts["unmarked_clause_overlap_conflicts"], 0)
        self.assertEqual(
            actual,
            "and Mira -·he-is-dying and Rowan -·he-is-reigning",
        )

    def test_duplicate_source_alignment_skips_no_guess(self):
        one = " ".join(self.speech)
        actual, evidence, counts = apply_unmarked_english_roles(
            self.speech, one + " and " + one,
        )
        self.assertEqual(evidence, [])
        self.assertEqual(counts[
            "unmarked_candidates_not_exact_or_previously_changed"], 1)
        self.assertEqual(actual, one + " and " + one)
        already = "and Rowan -·he-is-saying to Mira"
        actual, evidence, counts = apply_unmarked_english_roles(
            self.speech, already,
        )
        self.assertEqual(actual, already)
        self.assertEqual(evidence, [])
        self.assertEqual(counts[
            "unmarked_candidates_not_exact_or_previously_changed"], 1)

    def test_private_reader_audit_and_immutable_prior(self):
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_NOT_ALLOWED")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("NO_HEBREW_REGISTRY")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NO_NETWORK")),
        ):
            report = build_private_unmarked_clause_reader(self.root)
        self.assertEqual(report["chapters_scanned"], 1)
        self.assertEqual(report["verses_scanned"], 2)
        self.assertEqual(report["new_unmarked_grammar_candidates"], 2)
        self.assertEqual(report["new_unmarked_grammar_moves"], 2)
        self.assertEqual(report["new_unmarked_moves_by_structure"], {
            SPEAKER_TO_RECIPIENT: 1,
            INTRANSITIVE_SUBJECT: 1,
        })
        self.assertEqual(report["private_html_files_written_or_verified"], 0)
        self.assertFalse(report["all_english_syntax_certified"])
        self.assertTrue(report["other_unmarked_nominal_roles_still_unresolved"])
        self.assertFalse(report["source_ches_modified"])
        self.assertFalse(report["prior_readers_modified"])
        self.assertFalse(report["approval_manifest_modified"])
        self.assertFalse(report["hebrew_cross_validation_performed"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertFalse((self.base / "ches-english-clause-roles").exists())
        self.assertEqual((self.root / "gen.1.json").read_bytes(), self.bytes)
        self.assertEqual(self.old, build_private_reader(
            self.root, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ))

    def test_separate_v7_immutable_html_and_prior_reader_preserved(self):
        old = build_private_reader(
            self.root, render=True, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        prior = self.base / "ches-direct-reader" / old["snapshot_id"]
        old_files = {p.name: p.read_bytes() for p in prior.iterdir()
                     if p.is_file()}
        report = build_private_unmarked_clause_reader(
            self.root, render=True,
        )
        path = self.base / "ches-english-clause-roles" / report["private_v7_snapshot"]
        self.assertEqual(report["private_html_files_written_or_verified"], 2)
        self.assertEqual(path.stat().st_mode & 0o777, 0o700)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual({p.name for p in path.iterdir()},
                         {"index.html", "gen.1.html"})
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600
                            for p in path.iterdir()))
        page = (path / "gen.1.html").read_text()
        self.assertIn("and Rowan -·he-is-saying to Mira", page)
        self.assertIn("and Mira -·she-is-dying", page)
        self.assertNotIn("<script", page)
        same = build_private_unmarked_clause_reader(
            self.root, render=True,
        )
        self.assertEqual(same["private_v7_snapshot"], report["private_v7_snapshot"])
        self.assertEqual(old_files, {p.name: p.read_bytes()
                                     for p in prior.iterdir() if p.is_file()})
        self.assertEqual((self.root / "gen.1.json").read_bytes(), self.bytes)
        self.assertFalse((self.base / "ches-subject-review" / "approved.json").exists())

    def test_changed_private_output_not_overwritten(self):
        r = build_private_unmarked_clause_reader(self.root, render=True)
        page = (self.base / "ches-english-clause-roles" /
                r["private_v7_snapshot"] / "gen.1.html")
        page.write_text("OWNER_EDIT", encoding="utf-8")
        page.chmod(0o600)
        with self.assertRaisesRegex(
            DanMek037Error, "PRIVATE_READING_NO_OVERWRITE",
        ):
            build_private_unmarked_clause_reader(self.root, render=True)
        self.assertEqual(page.read_text(), "OWNER_EDIT")

    def test_311_guard_prevents_synthetic_corpus_output(self):
        with self.assertRaisesRegex(
            DanMek037Error, "REQUIRE_HISTORICAL_311",
        ):
            build_private_unmarked_clause_reader(
                self.root, render=True, require_311=True,
            )
        self.assertFalse((self.base / "ches-english-clause-roles").exists())

    def test_cli_only_aggregates_never_private_source_english(self):
        with patch("sys.argv", [
            "danmek-037", "--private-root", str(self.root),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        result = json.loads(out.getvalue())
        self.assertEqual(result["new_unmarked_grammar_candidates"], 2)
        for private in ("Rowan", "Mira", "gen.1.1", str(self.root)):
            self.assertNotIn(private, out.getvalue())


if __name__ == "__main__":
    unittest.main()
