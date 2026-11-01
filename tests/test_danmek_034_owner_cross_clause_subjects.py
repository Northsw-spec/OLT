"""DANMEK-034 synthetic regression checks for two owner-identified English cases.

Only invented surrounding text is committed, never copyrighted CHES verses.
No automatic grammar inference from adjacent nouns or transitive objects.
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
from scripts.danmek_034_owner_cross_clause_subjects import (
    DanMek034Error, RULE_DAVID, RULE_YAHWEH,
    apply_owner_cross_clause_subjects, build_private_owner_cross_clause_reader,
    main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek034OwnerCrossClause(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.base = Path(t.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)
        self.nested = (
            "and·he-is-becoming as·which David - he-sits "
            "in·house-of·him and·he-is-saying David "
            "to Ezra the·prophet afterward"
        )
        self.chooser = (
            "then David - he-said a word that in·them "
            "he-chose Yahweh to·to-carry-of some vessels"
        )
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.nested
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.chooser
        write_private_json(doc, self.source / "gen.1.json")
        self.original = (self.source / "gen.1.json").read_bytes()
        self.baseline = build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )

    def test_owner_example_one_distant_david_keeps_other_words(self):
        new, changes = apply_owner_cross_clause_subjects(self.nested)
        self.assertEqual(
            new,
            "and David - ·he-is-becoming as·which - he-sits "
            "in·house-of·him and David -·he-is-saying "
            "to Ezra the·prophet afterward",
        )
        self.assertEqual(
            [x["rule_code"] for x in changes], [RULE_DAVID],
        )
        self.assertEqual(changes[0]["owner_authorized_subject_moves"], 2)
        self.assertEqual(new.count("David"), self.nested.count("David"))
        self.assertIn("he-sits in·house-of·him", new)
        self.assertIn("to Ezra the·prophet afterward", new)

    def test_owner_example_two_yahweh_is_subject_only_with_context(self):
        new, changes = apply_owner_cross_clause_subjects(self.chooser)
        self.assertEqual(
            new,
            "then David - he-said a word that in·them "
            "Yahweh - he-chose to·to-carry-of some vessels",
        )
        self.assertEqual([x["rule_code"] for x in changes], [RULE_YAHWEH])
        self.assertEqual(changes[0]["owner_authorized_subject_moves"], 1)
        self.assertEqual(new.count("Yahweh"), self.chooser.count("Yahweh"))
        self.assertIn("then David - he-said", new)

    def test_both_rules_one_verse_keep_per_clause_independence(self):
        english = self.nested + " and " + self.chooser
        new, changes = apply_owner_cross_clause_subjects(english)
        self.assertEqual([x["rule_code"] for x in changes],
                         [RULE_DAVID, RULE_YAHWEH])
        self.assertEqual(sum(x["owner_authorized_subject_moves"]
                             for x in changes), 3)
        self.assertEqual(new.count("David"), english.count("David"))
        self.assertEqual(new.count("Yahweh"), english.count("Yahweh"))
        self.assertIn("and David - ·he-is-becoming", new)
        self.assertIn("that in·them Yahweh - he-chose", new)
        same, none = apply_owner_cross_clause_subjects(new)
        self.assertEqual(same, new)
        self.assertEqual(none, [])

    def test_non_owner_patterns_and_transitive_objects_never_moved(self):
        negatives = [
            "he-chose Yahweh",
            "and·he-chose Yahweh to·to-carry-of an object",
            "that in·them he-chose Rowan to·to-carry-of vessels",
            "that in·them he-chose Yahweh to open a gate",
            "that in·them he-saw Yahweh to·to-carry-of the bag",
            "and·he-is-becoming as·which Rowan - he-sits "
            "in·house-of·him and·he-is-saying Rowan "
            "to Ezra the·prophet afterward",
            "and·he-is-becoming as·which David - he-sits "
            "in·house-of·him and·he-is-saying Rowan "
            "to Ezra the·prophet afterward",
            "and·he-is-becoming as·which David - he-sits "
            "in·house-of·him and·he-is-saying David "
            "to Ezra the·king afterward",
            "and·he-is-becoming as·which David - he-sits "
            "in·house-of·him and·he-is-saying David "
            "to Ezra afterward",
            "he-saw Sailors and he-loved Rowan",
        ]
        for example in negatives:
            with self.subTest(example=example):
                result, changes = apply_owner_cross_clause_subjects(example)
                self.assertEqual(result, example)
                self.assertEqual(changes, [])

    def test_preserves_punctuation_and_multiple_unrelated_names(self):
        sentence = (
            "at sunset, " + self.nested +
            "; later, " + self.chooser +
            " and he-chose Rowan to open a gate."
        )
        after, evidence = apply_owner_cross_clause_subjects(sentence)
        self.assertEqual(len(evidence), 2)
        self.assertTrue(after.startswith("at sunset, and David - "))
        self.assertTrue(after.endswith("and he-chose Rowan to open a gate."))
        self.assertEqual(after.count("David"), sentence.count("David"))
        self.assertEqual(after.count("Yahweh"), sentence.count("Yahweh"))

    def test_validates_source_and_records_only_aggregate_counts(self):
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("NO_HEBREW_VALIDATION")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("NO_ORIGINAL_SOURCE_LOOKUP")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NO_NETWORK")),
        ):
            report = build_private_owner_cross_clause_reader(self.source)
        self.assertEqual(report["source_chapters_scanned"], 1)
        self.assertEqual(report["source_verses_scanned"], 2)
        self.assertEqual(report["verses_with_new_owner_cross_clause_changes"], 2)
        self.assertEqual(report["owner_approved_exact_context_instances"], 2)
        self.assertEqual(report["owner_authorized_individual_subject_moves"], 3)
        self.assertEqual(report["owner_cross_clause_rule_counts"], {
            RULE_DAVID: 1, RULE_YAHWEH: 1,
        })
        self.assertEqual(report["private_html_files_written_or_verified"], 0)
        self.assertFalse(report["automatic_unbounded_subject_inference_performed"])
        self.assertFalse(report["original_ches_modified"])
        self.assertFalse(report["prior_locked_readers_modified"])
        self.assertFalse(report["hebrew_cross_validation_performed"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertFalse((self.base / "ches-cross-clause-reading").exists())
        self.assertEqual((self.source / "gen.1.json").read_bytes(), self.original)
        self.assertEqual(self.baseline, build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ))

    def test_renders_new_private_v4_immutable_and_separate_from_old(self):
        old = build_private_reader(
            self.source, render=True, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        original_folder = self.base / "ches-direct-reader" / old["snapshot_id"]
        original_files = {
            f.name: f.read_bytes() for f in original_folder.iterdir()
            if f.is_file()
        }
        report = build_private_owner_cross_clause_reader(
            self.source, render=True,
        )
        self.assertEqual(report["private_html_files_written_or_verified"], 2)
        newdir = (self.base / "ches-cross-clause-reading" /
                  report["new_private_v4_snapshot_id"])
        self.assertEqual(newdir.stat().st_mode & 0o777, 0o700)
        self.assertEqual(newdir.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual({p.name for p in newdir.iterdir()},
                         {"index.html", "gen.1.html"})
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600
                            for p in newdir.iterdir()))
        rendered = (newdir / "gen.1.html").read_text()
        self.assertIn("and David - ·he-is-becoming", rendered)
        self.assertIn("and David -·he-is-saying", rendered)
        self.assertIn("that in·them Yahweh - he-chose", rendered)
        self.assertIn("default-src 'none'", rendered)
        self.assertNotIn("<script", rendered)
        again = build_private_owner_cross_clause_reader(
            self.source, render=True,
        )
        self.assertEqual(again["new_private_v4_snapshot_id"],
                         report["new_private_v4_snapshot_id"])
        self.assertEqual((self.source / "gen.1.json").read_bytes(), self.original)
        self.assertEqual(
            original_files,
            {p.name: p.read_bytes() for p in original_folder.iterdir()
             if p.is_file()},
        )
        self.assertFalse((self.base / "ches-subject-review" / "approved.json").exists())

    def test_modified_private_v4_output_not_overwritten(self):
        report = build_private_owner_cross_clause_reader(
            self.source, render=True,
        )
        target = (self.base / "ches-cross-clause-reading" /
                  report["new_private_v4_snapshot_id"] / "gen.1.html")
        target.write_text("OWNER_NOTE_MUST_NOT_OVERWRITE", encoding="utf-8")
        target.chmod(0o600)
        with self.assertRaisesRegex(
            DanMek034Error, "PRIVATE_READING_NO_OVERWRITE",
        ):
            build_private_owner_cross_clause_reader(
                self.source, render=True,
            )
        self.assertEqual(target.read_text(), "OWNER_NOTE_MUST_NOT_OVERWRITE")

    def test_311_guard_fails_before_creating_any_v4_file(self):
        with self.assertRaisesRegex(
            DanMek034Error, "OWNER_CROSS_CLAUSE_EXPECTED_311_CHANGED",
        ):
            build_private_owner_cross_clause_reader(
                self.source, render=True, require_311=True,
            )
        self.assertFalse((self.base / "ches-cross-clause-reading").exists())

    def test_html_escapes_private_text_and_no_execution(self):
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.nested + " <img src=x onerror=alert(1)>"
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = self.chooser
        write_private_json(doc, self.source / "gen.1.json")
        result = build_private_owner_cross_clause_reader(
            self.source, render=True,
        )
        page = (self.base / "ches-cross-clause-reading" /
                result["new_private_v4_snapshot_id"] / "gen.1.html").read_text()
        self.assertIn("&lt;img", page)
        self.assertNotIn("<img", page)

    def test_invalid_input_and_metadata_only_stdout(self):
        with self.assertRaises(DanMek034Error):
            apply_owner_cross_clause_subjects(None)
        with self.assertRaises(DanMek034Error):
            apply_owner_cross_clause_subjects("A" * 50001)
        with patch("sys.argv", [
            "danmek-034", "--private-root", str(self.source),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        obj = json.loads(output.getvalue())
        self.assertEqual(obj["owner_authorized_individual_subject_moves"], 3)
        for private in ("David", "Yahweh", "Ezra", "gen.1.1", str(self.source)):
            self.assertNotIn(private, output.getvalue())


if __name__ == "__main__":
    unittest.main()
