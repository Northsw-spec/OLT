"""Synthetic-only DANMEK-033 private P1 alternative-reading regressions."""
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
from scripts.danmek_030_reviewed_english_subject_order import _candidate_rules
from scripts.danmek_031_private_english_priority_triage import (
    triage_private_english_roles,
)
from scripts.danmek_033_private_p1_hypothesis_previews import (
    DanMek033Error, generate_private_p1_hypothesis_previews,
    preview_one_unapproved_subject_hypothesis, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek033PrivateP1HypothesisPreviews(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.base = Path(folder.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(gen, self.source / "gen.1.json")
        self.original = (self.source / "gen.1.json").read_bytes()
        self.old_reader = build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )

    def _priority(self):
        return triage_private_english_roles(
            self.source, write_private_report=True,
        )

    def test_hypothetical_two_independent_pairs_do_not_rewrite_or_approve(self):
        original = "he-saw Sailors and he-loved Rowan"
        rules = _candidate_rules(
            reference="gen.1.1", chapter_sha256="a" * 64, verse=original,
        )
        self.assertEqual(len(rules), 2)
        self.assertEqual(
            preview_one_unapproved_subject_hypothesis(
                verse_english=original, rule=rules[0],
                trusted_reference="gen.1.1",
                trusted_chapter_sha256="a" * 64,
            ),
            "Sailors - he-saw and he-loved Rowan",
        )
        self.assertEqual(
            preview_one_unapproved_subject_hypothesis(
                verse_english=original, rule=rules[1],
                trusted_reference="gen.1.1",
                trusted_chapter_sha256="a" * 64,
            ),
            "he-saw Sailors and Rowan - he-loved",
        )
        self.assertEqual(original, "he-saw Sailors and he-loved Rowan")
        self.assertTrue(all(
            x["english_subject_role_reviewed"] is False for x in rules
        ))

    def test_conjunction_form_and_unresolved_role_generate_conditional_only(self):
        english = "And·he-mused Rowan"
        rows = _candidate_rules(
            reference="gen.1.1", chapter_sha256="a" * 64, verse=english,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["english_role_class"], UNRESOLVED)
        alternate = preview_one_unapproved_subject_hypothesis(
            verse_english=english, rule=rows[0],
            trusted_reference="gen.1.1",
            trusted_chapter_sha256="a" * 64,
        )
        self.assertEqual(alternate, "And Rowan -·he-mused")
        self.assertEqual(english, "And·he-mused Rowan")

    def test_stale_or_pretend_approved_rules_fail_closed(self):
        english = "he-saw Sailors and he-loved Rowan"
        row = _candidate_rules(
            reference="gen.1.1", chapter_sha256="a" * 64, verse=english,
        )[0]
        for name, value in (
            ("reference", "gen.1.2"),
            ("source_chapter_sha256", "f" * 64),
            ("expected_verse_english_sha256", "f" * 64),
            ("candidate_ordinal", 2),
            ("observed_verb_gloss", "he-wrote"),
            ("observed_adjacent_noun_phrase", "Another"),
            ("english_subject_role_reviewed", True),
            ("review_note", "Previously reviewed by editor"),
        ):
            with self.subTest(name=name):
                altered = dict(row, **{name: value})
                with self.assertRaises(DanMek033Error):
                    preview_one_unapproved_subject_hypothesis(
                        verse_english=english, rule=altered,
                        trusted_reference="gen.1.1",
                        trusted_chapter_sha256="a" * 64,
                    )
        with self.assertRaises(DanMek033Error):
            preview_one_unapproved_subject_hypothesis(
                verse_english="he-saw Other and he-loved Rowan",
                rule=row,
                trusted_reference="gen.1.1",
                trusted_chapter_sha256="a" * 64,
            )

    def test_requires_existing_031_private_report(self):
        with self.assertRaises(DanMek033Error):
            generate_private_p1_hypothesis_previews(self.source)
        self.assertFalse((self.base / "ches-subject-previews").exists())

    def test_metadata_scan_never_changes_any_original_or_old_reader(self):
        self._priority()
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("HEBREW_LOOKUP_FORBIDDEN")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("SOURCE_REGISTRY_FORBIDDEN")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NETWORK_FORBIDDEN")),
        ):
            result = generate_private_p1_hypothesis_previews(self.source)
        self.assertEqual(result["historical_p1_verses"], 1)
        self.assertEqual(result["historical_p1_pair_hypotheses"], 2)
        self.assertEqual(result["unreviewed_alternative_pair_presentations"], 2)
        self.assertEqual(result["private_html_batches"], 1)
        self.assertEqual(result["private_files_written_or_verified"], 0)
        self.assertEqual(result["hypotheses_by_english_role"], {
            OBJECT_RISK: 2, UNRESOLVED: 0,
        })
        self.assertEqual(result["confirmed_grammar_errors"], 0)
        self.assertEqual(result["approved_english_corrections"], 0)
        self.assertFalse(result["prior_readers_modified"])
        self.assertFalse(result["hebrew_source_crosschecked"])
        self.assertEqual(result["publication_status"], "BLOCKED")
        self.assertFalse((self.base / "ches-subject-previews").exists())
        self.assertEqual(self.original, (self.source / "gen.1.json").read_bytes())
        self.assertEqual(self.old_reader, build_private_reader(
            self.source, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ))

    def test_private_html_and_json_show_competing_readings_unapproved(self):
        self._priority()
        result = generate_private_p1_hypothesis_previews(
            self.source, write_private_previews=True,
        )
        self.assertEqual(result["private_files_written_or_verified"], 3)
        parent = self.base / "ches-subject-previews"
        dest = parent / result["new_private_preview_snapshot"]
        self.assertEqual(parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(dest.stat().st_mode & 0o777, 0o700)
        self.assertEqual({p.name for p in dest.iterdir()}, {
            "index.html", "batch-001.html",
            "UNAPPROVED-hypothetical-previews.json",
        })
        self.assertTrue(all(
            p.stat().st_mode & 0o777 == 0o600 for p in dest.iterdir()
        ))
        page = (dest / "batch-001.html").read_text()
        self.assertIn("he-saw Sailors and he-loved Rowan", page)
        self.assertIn("Sailors - he-saw and he-loved Rowan", page)
        self.assertIn("he-saw Sailors and Rowan - he-loved", page)
        self.assertIn("Interpretation A", page)
        self.assertIn("Interpretation B", page)
        self.assertIn("UNAPPROVED", page)
        self.assertNotIn("<script", page)
        self.assertIn("default-src 'none'", page)
        self.assertNotIn("he-is-making Worker", page)
        document = json.loads(
            (dest / "UNAPPROVED-hypothetical-previews.json").read_text()
        )
        self.assertTrue(document["all_candidates_unapproved"])
        self.assertEqual(document["grammar_subject_roles_proven"], 0)
        self.assertEqual(len(document["hypotheses"]), 2)
        self.assertTrue(all(
            x["hypothesis_only"] is True
            and x["grammar_subject_proven"] is False
            and x["grammar_object_proven"] is False
            and x["actual_reading_modified"] is False
            and x["reviewer_approval"] == "UNAPPROVED"
            and x["if_noun_is_object_or_role_unresolved_english"] ==
                x["original_displayed_english"]
            for x in document["hypotheses"]
        ))
        self.assertFalse((self.base / "ches-subject-review" / "approved.json").exists())
        same = generate_private_p1_hypothesis_previews(
            self.source, write_private_previews=True,
        )
        self.assertEqual(same["new_private_preview_snapshot"],
                         result["new_private_preview_snapshot"])
        self.assertEqual(len(list(dest.iterdir())), 3)
        self.assertEqual(self.original, (self.source / "gen.1.json").read_bytes())

    def test_two_verses_and_batch_size_one_create_two_private_html_pages(self):
        extra = invented_chapter("exo", 1, source_sha="f" * 64)
        extra["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan"
        extra["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "No candidate present."
        write_private_json(extra, self.source / "exo.1.json")
        self._priority()
        result = generate_private_p1_hypothesis_previews(
            self.source, write_private_previews=True, batch_size=1,
        )
        self.assertEqual(result["historical_p1_verses"], 2)
        self.assertEqual(result["historical_p1_pair_hypotheses"], 4)
        self.assertEqual(result["private_html_batches"], 2)
        self.assertEqual(result["private_files_written_or_verified"], 4)
        folder = (self.base / "ches-subject-previews" /
                  result["new_private_preview_snapshot"])
        self.assertEqual(
            len(json.loads(
                (folder / "UNAPPROVED-hypothetical-previews.json").read_text()
            )["hypotheses"]), 4,
        )
        self.assertTrue((folder / "batch-002.html").exists())

    def test_modified_preview_files_not_overwritten(self):
        self._priority()
        r = generate_private_p1_hypothesis_previews(
            self.source, write_private_previews=True,
        )
        file = (self.base / "ches-subject-previews" /
                r["new_private_preview_snapshot"] / "batch-001.html")
        file.write_text("OWNER_LOCAL_NOTE", encoding="utf-8")
        file.chmod(0o600)
        with self.assertRaisesRegex(
            DanMek033Error, "PRIVATE_READING_NO_OVERWRITE",
        ):
            generate_private_p1_hypothesis_previews(
                self.source, write_private_previews=True,
            )
        self.assertEqual(file.read_text(), "OWNER_LOCAL_NOTE")

    def test_invalid_source_guard_and_batch_sizes(self):
        self._priority()
        with self.assertRaisesRegex(
            DanMek033Error, "HISTORICAL_311_ENGLISH_CASE_COUNT_CHANGED",
        ):
            generate_private_p1_hypothesis_previews(
                self.source, require_311=True, write_private_previews=True,
            )
        for size in (0, -1, 51, 1.5, True):
            with self.subTest(size=size), self.assertRaisesRegex(
                DanMek033Error, "INVALID_PRIVATE_HYPOTHESIS_OPTIONS",
            ):
                generate_private_p1_hypothesis_previews(
                    self.source, batch_size=size,
                )
        self.assertFalse((self.base / "ches-subject-previews").exists())

    def test_html_escapes_untrusted_english(self):
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan <img src=x onerror=alert(1)>"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(gen, self.source / "gen.1.json")
        self._priority()
        report = generate_private_p1_hypothesis_previews(
            self.source, write_private_previews=True,
        )
        page = (self.base / "ches-subject-previews" /
                report["new_private_preview_snapshot"] /
                "batch-001.html").read_text()
        self.assertIn("&lt;img", page)
        self.assertNotIn("<img", page)

    def test_cli_prints_only_aggregates_no_verse_or_private_paths(self):
        self._priority()
        with patch("sys.argv", [
            "danmek-033", "--private-root", str(self.source),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        obj = json.loads(output.getvalue())
        self.assertEqual(obj["historical_p1_pair_hypotheses"], 2)
        for word in ("Sailors", "Rowan", "Worker", "gen.1.1",
                     str(self.source)):
            self.assertNotIn(word, output.getvalue())


if __name__ == "__main__":
    unittest.main()
