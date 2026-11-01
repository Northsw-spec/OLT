"""DANMEK-036: synthetic English-only source-fragment grammar regression."""
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
from scripts.danmek_036_fragment_role_grammar import (
    DanMek036Error, COMPACT, SPLIT_ONE, SPLIT_TWO,
    detect_source_nominal_roles, apply_source_nominal_roles,
    build_private_fragment_role_reader, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek036FragmentRoles(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.root = self.base / "ches"
        self.root.mkdir(mode=0o700)
        self.first = ["and·he-is-taking", "Rowan", "»", "the·vessel"]
        self.second = [
            "and·he-is-", "smiting", "Sailors", "»", "the·fort",
        ]
        chapter = invented_chapter("gen", 1)
        chapter["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"] = [
            {"original_ches_line_text": x, "page": 1, "pdf_x": 20+i*15,
             "pdf_y": 75} for i,x in enumerate(self.first)
        ]
        chapter["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"] = [
            {"original_ches_line_text": x, "page": 1, "pdf_x": 20+i*15,
             "pdf_y": 90} for i,x in enumerate(self.second)
        ]
        chapter["ches_pdf_green_spans"] = 9
        write_private_json(chapter, self.root / "gen.1.json")
        self.original = (self.root / "gen.1.json").read_bytes()
        self.old = build_private_reader(
            self.root, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )

    def test_fragment_parser_handles_entire_and_split_finite_verbs(self):
        cases = (
            (["and·he-is-taking", "Rowan", "»", "the·vessel"], COMPACT),
            (["and·he-is-", "smiting", "Sailors", "»", "the·fort"], SPLIT_ONE),
            (["and·she-is-", "mak", "ing-king", "Mira", "»", "Micah"],
             SPLIT_TWO),
            (["he-took", "Natan", "»", "box"], COMPACT),
            (["and·he-is-", "generating", "Abraham", "»", "Isaac"], SPLIT_ONE),
        )
        for words, group in cases:
            with self.subTest(group=group, words=words):
                found = detect_source_nominal_roles(words)
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0]["class"], group)
                self.assertEqual(words[found[0]["marker"]], "»")

    def test_generic_grammar_moves_any_subject_not_named_people_only(self):
        cases = (
            ("and·he-is-taking Rowan » the·vessel",
             "and Rowan -·he-is-taking » the·vessel", self.first),
            ("and·he-is- smiting Sailors » the·fort",
             "and Sailors -·he-is- smiting » the·fort", self.second),
            ("and·she-is- mak ing-king Mira » Micah",
             "and Mira -·she-is- mak ing-king » Micah",
             ["and·she-is-", "mak", "ing-king", "Mira", "»", "Micah"]),
            ("he-took Natan » box", "Natan - he-took » box",
             ["he-took", "Natan", "»", "box"]),
            ("and·he-is- generating Oren » Micah",
             "and Oren ·he-is- generating » Micah",
             ["and·he-is-", "generating", "Oren", "»", "Micah"]),
        )
        for original, expected, fragments in cases:
            with self.subTest(original=original):
                actual, events, metrics = apply_source_nominal_roles(
                    fragments, original,
                )
                self.assertEqual(actual, expected)
                self.assertEqual(len(events), 1)
                self.assertTrue(events[0][
                    "finite_nominal_and_standalone_object_mark_confirmed"
                ])
                self.assertEqual(metrics["source_structural_candidates"], 1)
                self.assertEqual(metrics["new_v6_fragment_moves"], 1)

    def test_negative_objects_and_source_false_positives_are_preserved(self):
        cases = (
            ["and·he-is-saying", "I-saw", "»", "a·city"],
            ["and·he-is-taking", "the·vessel", "»", "another"],
            ["and·he-is-taking", "Rowan", "the·vessel"],
            ["and·he-is-taking", "Rowan", "»·him"],
            ["and·he-is-taking", "to·Rowan", "»", "the·vessel"],
            ["and·he-is-", "making", "the·king", "Rowan", "»", "the·vessel"],
            ["and·he-is-", "making", "king-of", "Egypt", "»", "Natan"],
            ["and·he-is-taking", "Rowan", "and·»", "the·vessel"],
            ["and·he-is-taking", "Rowan", "from·", "»", "the·vessel"],
            ["and·he-is-", "making", "Rowan", "the·vessel"],
        )
        for original in cases:
            with self.subTest(original=original):
                self.assertEqual(detect_source_nominal_roles(original), [])
                flat = " ".join(original)
                new, events, _ = apply_source_nominal_roles(original, flat)
                self.assertEqual(new, flat)
                self.assertEqual(events, [])

    def test_two_disjoint_structures_in_one_verse(self):
        fragments = (self.first + ["and·he-is-", "smiting",
                                  "Sailors", "»", "the·fort"])
        original = " ".join(fragments)
        actual, events, metrics = apply_source_nominal_roles(
            fragments, original,
        )
        self.assertEqual(len(events), 2)
        self.assertEqual(metrics["source_structural_candidates"], 2)
        self.assertIn("and Rowan -·he-is-taking » the·vessel", actual)
        self.assertIn("and Sailors -·he-is- smiting » the·fort", actual)
        self.assertEqual(actual.count("Rowan"), 1)
        self.assertEqual(actual.count("Sailors"), 1)

    def test_ambiguous_alignment_is_skipped_not_guessed(self):
        single = " ".join(self.first)
        repeated = single + " then " + single
        actual, events, stats = apply_source_nominal_roles(
            self.first, repeated,
        )
        self.assertEqual(actual, repeated)
        self.assertEqual(events, [])
        self.assertEqual(stats["source_matches_already_changed_or_not_unique"], 1)
        previous = "and Rowan -·he-is-taking » the·vessel"
        actual, events, stats = apply_source_nominal_roles(
            self.first, previous,
        )
        self.assertEqual(actual, previous)
        self.assertEqual(events, [])
        self.assertEqual(stats["source_matches_already_changed_or_not_unique"], 1)

    def test_audit_full_private_source_no_hebrew_network_or_writes(self):
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_SOURCE_FORBIDDEN")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("HEBREW_REGISTRY_FORBIDDEN")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NETWORK_FORBIDDEN")),
        ):
            stats = build_private_fragment_role_reader(self.root)
        self.assertEqual(stats["chapters_scanned"], 1)
        self.assertEqual(stats["verses_scanned"], 2)
        self.assertEqual(stats["source_structural_candidates"], 2)
        self.assertEqual(stats["new_v6_fragment_moves"], 2)
        self.assertEqual(stats["private_html_files_written_or_verified"], 0)
        self.assertFalse(stats["english_grammar_fully_certified"])
        self.assertTrue(stats["unknown_subject_object_cases_still_require_review"])
        self.assertFalse(stats["source_ches_modified"])
        self.assertFalse(stats["previous_readers_modified"])
        self.assertFalse(stats["approval_manifest_modified"])
        self.assertFalse(stats["hebrew_cross_validation_performed"])
        self.assertEqual(stats["publication_status"], "BLOCKED")
        self.assertFalse((self.base / "ches-english-fragment-roles").exists())
        self.assertEqual(self.original, (self.root / "gen.1.json").read_bytes())
        self.assertEqual(self.old, build_private_reader(
            self.root, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ))

    def test_v6_separate_immutable_private_html_keeps_old_versions(self):
        old_report = build_private_reader(
            self.root, render=True, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        old_dir = self.base / "ches-direct-reader" / old_report["snapshot_id"]
        old_bytes = {p.name: p.read_bytes() for p in old_dir.iterdir()
                     if p.is_file()}
        r = build_private_fragment_role_reader(self.root, render=True)
        base = self.base / "ches-english-fragment-roles"
        target = base / r["new_private_v6_snapshot"]
        self.assertEqual(r["private_html_files_written_or_verified"], 2)
        self.assertEqual(base.stat().st_mode & 0o777, 0o700)
        self.assertEqual(target.stat().st_mode & 0o777, 0o700)
        self.assertEqual({p.name for p in target.iterdir()},
                         {"index.html", "gen.1.html"})
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600
                            for p in target.iterdir()))
        page = (target / "gen.1.html").read_text()
        self.assertIn("and Rowan -·he-is-taking » the·vessel", page)
        self.assertIn("and Sailors -·he-is- smiting » the·fort", page)
        self.assertIn("default-src 'none'", page)
        self.assertNotIn("<script", page)
        same = build_private_fragment_role_reader(self.root, render=True)
        self.assertEqual(same["new_private_v6_snapshot"],
                         r["new_private_v6_snapshot"])
        self.assertEqual(self.original, (self.root / "gen.1.json").read_bytes())
        self.assertEqual(old_bytes, {p.name: p.read_bytes()
                                    for p in old_dir.iterdir() if p.is_file()})
        self.assertFalse((self.base / "ches-subject-review" / "approved.json").exists())

    def test_edited_private_html_not_overwritten(self):
        r = build_private_fragment_role_reader(self.root, render=True)
        target = (self.base / "ches-english-fragment-roles" /
                  r["new_private_v6_snapshot"] / "gen.1.html")
        target.write_text("OWNER_LOCAL_NOTE", encoding="utf-8")
        target.chmod(0o600)
        with self.assertRaisesRegex(DanMek036Error, "PRIVATE_READING_NO_OVERWRITE"):
            build_private_fragment_role_reader(self.root, render=True)
        self.assertEqual(target.read_text(), "OWNER_LOCAL_NOTE")

    def test_reject_incomplete_311_synthetic_source(self):
        with self.assertRaisesRegex(
            DanMek036Error, "HISTORICAL_311_REQUIRED",
        ):
            build_private_fragment_role_reader(
                self.root, render=True, require_311=True,
            )
        self.assertFalse((self.base / "ches-english-fragment-roles").exists())

    def test_private_source_is_escaped_in_offline_html(self):
        doc = invented_chapter("gen", 1)
        first = self.first + ["<img src=x onerror=alert(1)>"]
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"] = [
            {"original_ches_line_text": x, "page": 1, "pdf_x": 20 + i*15,
             "pdf_y": 80} for i,x in enumerate(first)
        ]
        doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"] = [
            {"original_ches_line_text": x, "page": 1, "pdf_x": 20 + i*15,
             "pdf_y": 90} for i,x in enumerate(self.second)
        ]
        doc["ches_pdf_green_spans"] = len(first) + len(self.second)
        write_private_json(doc, self.root / "gen.1.json")
        r = build_private_fragment_role_reader(self.root, render=True)
        page = (self.base / "ches-english-fragment-roles" /
                r["new_private_v6_snapshot"] / "gen.1.html").read_text()
        self.assertIn("&lt;img", page)
        self.assertNotIn("<img", page)

    def test_stdout_metadata_never_shows_source_words(self):
        with patch("sys.argv", [
            "danmek-036", "--private-root", str(self.root),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        obj = json.loads(out.getvalue())
        self.assertEqual(obj["source_structural_candidates"], 2)
        for secret in ("Rowan", "Sailors", "the·vessel", "gen.1.1",
                       str(self.root)):
            self.assertNotIn(secret, out.getvalue())


if __name__ == "__main__":
    unittest.main()
