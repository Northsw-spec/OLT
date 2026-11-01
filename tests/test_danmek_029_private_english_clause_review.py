"""DANMEK-029 invented-English-only grammar-role and privacy regression tests."""
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
    DanMek029Error, PATTERN_SUBJECT, OBJECT_RISK, UNRESOLVED,
    classify_english_clause_pairs, review_private_english_clauses, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek029EnglishClauseReview(unittest.TestCase):
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
        ] = "and·they-are-hearing Sailors that he-was-anointed Rowan"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors"
        exo = invented_chapter("exo", 1, source_sha="f" * 64)
        exo["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker she-is-building Leader"
        exo["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "And the lantern — the merchant saw."
        write_private_json(gen, self.source / "gen.1.json")
        write_private_json(exo, self.source / "exo.1.json")
        self.source_before = {
            p.name: p.read_bytes() for p in self.source.iterdir()
        }
        self.reader_before = build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        self.assertEqual(
            self.reader_before["olt_owner_candidate_ambiguous_verses_unchanged"], 2,
        )

    def test_owner_multi_clause_two_subject_patterns_detected_without_edits(self):
        source = "and·they-are-hearing Sailors that he-was-anointed Rowan"
        found = classify_english_clause_pairs([source])
        self.assertEqual(len(found), 2)
        self.assertEqual([f["english_role_class"] for f in found],
                         [PATTERN_SUBJECT, PATTERN_SUBJECT])
        self.assertEqual([f["rule_code"] for f in found], [
            "OWNER_REPORT_HEARING_MULTI_CLAUSE",
            "POSTPOSED_PASSIVE_SUBJECT",
        ])
        self.assertEqual([f["observed_adjacent_noun_phrase"] for f in found],
                         ["Sailors", "Rowan"])
        self.assertFalse(any(x["subject_syntax_certified"] for x in found))
        self.assertFalse(any(
            x["english_word_order_change_authorized_by_this_tool"] for x in found
        ))
        self.assertEqual(source,
                         "and·they-are-hearing Sailors that he-was-anointed Rowan")

    def test_multiple_grammar_roles_are_not_collapsed_into_one_verse_flag(self):
        example = "he-saw Sailors and·he-came Rowan and he-returned Elias"
        matches = classify_english_clause_pairs([example])
        self.assertEqual(len(matches), 3)
        self.assertEqual([x["english_role_class"] for x in matches],
                         [OBJECT_RISK, PATTERN_SUBJECT, OBJECT_RISK])
        self.assertEqual([x["ordinal"] for x in matches], [1, 2, 3])
        self.assertTrue(all(
            matches[i]["source_english_position_end"] <=
            matches[i + 1]["source_english_position_start"]
            for i in (0, 1)
        ))

    def test_transitive_object_risk_is_not_a_proven_object_or_false_subject(self):
        for sentence in (
            "he-saw Sailors", "he-loved Rowan", "she-is-making a name",
            "they-were-hearing Sailors", "he-returned Elias",
            "she-was-calling Rowan", "he-built Rowan",
        ):
            # Some lowercase nouns are deliberately outside the candidate
            # shape: they are not proof of grammar correctness.
            with self.subTest(sentence=sentence):
                rows = classify_english_clause_pairs([sentence])
                self.assertTrue(
                    not rows or all(x["english_role_class"] == OBJECT_RISK
                                    for x in rows)
                )
                self.assertTrue(all(not x["object_syntax_certified"] for x in rows))

    def test_unrecognized_expression_is_unresolved_and_no_guess(self):
        rows = classify_english_clause_pairs(["he-mused Rowan"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["english_role_class"], UNRESOLVED)
        self.assertIsNone(rows[0]["rule_code"])

    def test_articles_compound_names_fragments_and_boundaries(self):
        sample = ["And·they-were-hearing", "the·Sailors", "that",
                  "she-is-anointed", "the·King Rowan"]
        rows = classify_english_clause_pairs(sample)
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["english_role_class"] for r in rows],
                         [PATTERN_SUBJECT, PATTERN_SUBJECT])
        self.assertEqual(rows[1]["observed_adjacent_noun_phrase"],
                         "the·King Rowan")
        rows = classify_english_clause_pairs(
            ["he-was-appointed King Rowan And he-came Elias"]
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["observed_adjacent_noun_phrase"] for r in rows],
                         ["King Rowan", "Elias"])

    def test_no_automatic_grammatical_certification_from_no_hits(self):
        for sentence in (
            "And the lantern — the merchant saw.",
            "And Rowan -·he-came",
            "God — He saw the light, that — good.",
            "he rests",  # unusual punctuation and non-hyphenated forms
        ):
            with self.subTest(sentence=sentence):
                self.assertEqual(classify_english_clause_pairs([sentence]), [])

    def test_scans_all_verses_and_retains_all_historic_ambiguity_cases(self):
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_SOURCE_FORBIDDEN")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("HEBREW_REGISTRY_FORBIDDEN")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NETWORK_FORBIDDEN")),
        ):
            result = review_private_english_clauses(self.source)
        self.assertEqual(result["source_chapters_scanned"], 2)
        self.assertEqual(result["source_verses_scanned"], 4)
        self.assertEqual(result["historical_311_english_ambiguities_seen"], 2)
        self.assertEqual(result["postverbal_noun_pairs_reviewed"], 5)
        self.assertEqual(result["verses_with_review_cases"], 3)
        self.assertEqual(result["verses_with_object_risk"], 2)
        self.assertEqual(result["pair_classification_counts"], {
            PATTERN_SUBJECT: 2, OBJECT_RISK: 3,
        })
        self.assertEqual(result["legacy_unverified_moves_withheld"], 1)
        self.assertEqual(result["v2_reorders_observed_in_memory"], 2)
        self.assertEqual(result["grammar_cases_certified_correct"], 0)
        self.assertEqual(result["grammar_cases_owner_approved_by_this_tool"], 0)
        self.assertFalse(result["hebrew_or_aramaic_translation_accuracy_checked"])
        self.assertFalse(result["previously_approved_reader_changed"])
        self.assertEqual(result["publication_status"], "BLOCKED")
        self.assertEqual(result["private_output_state"],
                         "AUDIT_ONLY_NO_REPORT_WRITTEN")
        self.assertFalse((self.base / "ches-clause-review").exists())
        self.assertEqual(self.source_before,
                         {p.name: p.read_bytes() for p in self.source.iterdir()})
        self.assertEqual(self.reader_before, build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ))

    def test_private_json_html_no_overwrite_and_no_private_stdout(self):
        first = review_private_english_clauses(
            self.source, write_private_report=True,
        )
        self.assertEqual(first["private_output_state"], "NEW_PRIVATE_REPORT")
        target = self.base / "ches-clause-review"
        self.assertEqual(target.stat().st_mode & 0o777, 0o700)
        files = sorted(target.iterdir())
        self.assertEqual(len(files), 2)
        self.assertEqual({f.suffix for f in files}, {".html", ".json"})
        self.assertTrue(all(f.stat().st_mode & 0o777 == 0o600 for f in files))
        document = json.loads(next(f for f in files if f.suffix == ".json").read_text())
        self.assertFalse(document["hebrew_aramaic_source_used"])
        self.assertEqual(document["english_role_proofs"], 0)
        self.assertEqual(document["legacy_regex_ambiguities_seen"], 2)
        self.assertEqual(len(document["cases"]), 3)
        self.assertIn("Sailors", json.dumps(document))
        risky = next(r for r in document["cases"] if r["reference"] == "gen.1.2")
        self.assertTrue(risky["legacy_unverified_reorder_withheld"])
        self.assertEqual(risky["original_english_fragments"],
                         risky["guarded_english_fragments"])
        self.assertEqual(risky["case_status"],
                         "OBJECT_OR_SUBJECT_REQUIRES_ENGLISH_CONTEXT")
        self.assertFalse(risky["proposed_corrections_approved_by_029"])
        html_page = next(f for f in files if f.suffix == ".html").read_text()
        self.assertIn("and·they-are-hearing Sailors", html_page)
        self.assertIn("default-src 'none'", html_page)
        self.assertNotIn("<script", html_page)
        second = review_private_english_clauses(
            self.source, write_private_report=True,
        )
        self.assertEqual(second["private_output_state"],
                         "EXISTING_IDENTICAL_PRIVATE_REPORT")
        self.assertEqual(self.source_before,
                         {p.name: p.read_bytes() for p in self.source.iterdir()})

    def test_html_source_escapes_untrusted_content(self):
        source = invented_chapter("gen", 1)
        source["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors <img src=x onerror=alert(1)>"
        source["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "Without role candidates"
        write_private_json(source, self.source / "gen.1.json")
        report = review_private_english_clauses(
            self.source, write_private_report=True,
        )
        self.assertEqual(report["source_verses_scanned"], 4)
        page = next((self.base / "ches-clause-review").glob("*.html")).read_text()
        self.assertIn("&lt;img", page)
        self.assertNotIn("<img", page)
        self.assertNotIn("<script", page)

    def test_owner_changed_private_file_is_never_overwritten(self):
        review_private_english_clauses(self.source, write_private_report=True)
        file = next((self.base / "ches-clause-review").glob("*.json"))
        file.write_text("OWNER_MANUAL_NOTE_MUST_SURVIVE", encoding="utf-8")
        file.chmod(0o600)
        with self.assertRaisesRegex(
            DanMek029Error, "PRIVATE_ENGLISH_CLAUSE_REVIEW_FAILED",
        ):
            review_private_english_clauses(self.source, write_private_report=True)
        self.assertEqual(file.read_text(), "OWNER_MANUAL_NOTE_MUST_SURVIVE")

    def test_311_guard_fail_closed_before_writing(self):
        with self.assertRaisesRegex(
            DanMek029Error, "OWNER_EXPECTED_311_ENGLISH_AMBIGUITIES_NOT_FOUND"
        ):
            review_private_english_clauses(
                self.source, require_311=True, write_private_report=True,
            )
        self.assertFalse((self.base / "ches-clause-review").exists())

    def test_reject_symlinked_report_folder_and_invalid_fragments(self):
        target = self.base / "ches-clause-review"
        target.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(DanMek029Error):
            review_private_english_clauses(self.source, write_private_report=True)
        target.unlink()
        self.assertFalse(target.exists())
        for input_fragments in (
            [], "he-saw Rowan", ["he-saw Rowan", 42],
            ["abc"] * 10001,
        ):
            with self.assertRaisesRegex(DanMek029Error,
                                        "INVALID_ENGLISH_CLAUSE_FRAGMENT_SEQUENCE"):
                classify_english_clause_pairs(input_fragments)

    def test_cli_only_reports_aggregate_non_sensitive_metadata(self):
        with patch("sys.argv", [
            "danmek-029", "--private-root", str(self.source),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["postverbal_noun_pairs_reviewed"], 5)
        for forbidden in ("Sailors", "Rowan", "Worker", "gen.1.1",
                          str(self.source)):
            self.assertNotIn(forbidden, output.getvalue())
        self.assertFalse((self.base / "ches-clause-review").exists())

    def test_multiple_pairs_in_one_verse_cannot_exhaust_unbounded_memory(self):
        text = " ".join(["he-saw Sailors"] * 81)
        with self.assertRaisesRegex(DanMek029Error,
                                    "ENGLISH_CLAUSE_REVIEW_TOO_MANY_PAIRS"):
            classify_english_clause_pairs([text])


if __name__ == "__main__":
    unittest.main()
