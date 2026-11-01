"""DANMEK-030: invented-English-only private approval and immutable reader tests."""
from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.ches_015_direct_private_reader import build_private_reader
from scripts.danmek_030_reviewed_english_subject_order import (
    SCHEMA, DanMek030Error, apply_reviewed_english_subjects,
    run_private_reviewed_subject_order, main,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek030ReviewedSubjectOrder(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name) / ".olt-private"
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
        self.before = (self.source / "gen.1.json").read_bytes()
        self.baseline = build_private_reader(
            self.source, render=False,
            olt_owner_approved_candidates=True, olt_display_faces=True,
        )
        self.assertEqual(
            self.baseline["olt_owner_candidate_ambiguous_verses_unchanged"], 1
        )

    def _build_queue(self):
        with patch("urllib.request.urlopen",
                   side_effect=AssertionError("NETWORK_FORBIDDEN")):
            report = run_private_reviewed_subject_order(
                self.source, mode="review",
            )
        self.assertEqual(report["private_review_files_written_or_verified"], 2)
        directory = self.base / "ches-subject-review"
        json_file = next(directory.glob("queue-*.json"))
        return report, json_file, json.loads(json_file.read_text())

    def _approved(self, ordinals=(1, 2)):
        _, _, doc = self._build_queue()
        for rule in doc["rules"]:
            if (rule["reference"] == "gen.1.1"
                    and rule["candidate_ordinal"] in ordinals):
                rule["english_subject_role_reviewed"] = True
                rule["review_note"] = (
                    "English-only editorial subject-role context was "
                    "personally reviewed as a postposed noun subject."
                )
        # The original queue is immutable. The operator-authored approval
        # manifest is a distinct fixed private file, with safe permissions.
        path = self.base / "ches-subject-review" / "approved.json"
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        path.chmod(0o600)
        return path, doc

    def test_queue_private_and_unapproved_by_default(self):
        report, queue_path, doc = self._build_queue()
        self.assertEqual(report["chapters_scanned"], 1)
        self.assertEqual(report["verses_scanned"], 2)
        self.assertEqual(report["historical_ambiguous_english_verses"], 1)
        self.assertEqual(report["potential_subject_role_reviews_queued"], 3)
        self.assertEqual(report["explicitly_attested_english_subject_moves"], 0)
        self.assertFalse(report["independent_grammar_certification"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertEqual(doc["schema"], SCHEMA)
        self.assertEqual(doc["source_owner_reader_snapshot"],
                         self.baseline["snapshot_id"])
        self.assertEqual(len(doc["rules"]), 3)
        self.assertTrue(all(
            r["english_subject_role_reviewed"] is False
            and r["review_note"] == ""
            for r in doc["rules"]
        ))
        self.assertEqual(queue_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(queue_path.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(list(self.base.glob("ches-reviewed-subject-reading")),
                         [])
        html_report = next(queue_path.parent.glob("queue-*.html")).read_text()
        self.assertEqual(next(queue_path.parent.glob("queue-*.html")).stat().st_mode & 0o777,
                         0o600)
        self.assertIn("he-saw Sailors and he-loved Rowan", html_report)
        self.assertIn("default-src 'none'", html_report)
        self.assertEqual(self.before, (self.source / "gen.1.json").read_bytes())

    def test_default_audit_does_not_write_any_file(self):
        with patch("urllib.request.urlopen",
                   side_effect=AssertionError("NETWORK_FORBIDDEN")):
            report = run_private_reviewed_subject_order(
                self.source, mode="audit",
            )
        self.assertEqual(report["potential_subject_role_reviews_queued"], 3)
        self.assertEqual(report["private_review_files_written_or_verified"], 0)
        self.assertFalse((self.base / "ches-subject-review").exists())
        self.assertFalse((self.base / "ches-reviewed-subject-reading").exists())
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_two_explicit_english_subject_attestations_in_one_verse(self):
        original_text = "he-saw Sailors and he-loved Rowan"
        _, _, doc = self._build_queue()
        rules = [r for r in doc["rules"] if r["reference"] == "gen.1.1"]
        for rule in rules:
            rule["english_subject_role_reviewed"] = True
            rule["review_note"] = "This English noun is reviewed in context as the subject."
        rendered, count = apply_reviewed_english_subjects(
            original_text, reference="gen.1.1",
            chapter_sha256=rules[0]["source_chapter_sha256"], rules=rules,
        )
        self.assertEqual(rendered, "Sailors - he-saw and Rowan - he-loved")
        self.assertEqual(count, 2)
        self.assertEqual(original_text, "he-saw Sailors and he-loved Rowan")

    def test_false_attestation_is_not_a_correction(self):
        _, _, doc = self._build_queue()
        rules = [r for r in doc["rules"] if r["reference"] == "gen.1.1"]
        original = "he-saw Sailors and he-loved Rowan"
        output, moved = apply_reviewed_english_subjects(
            original, reference="gen.1.1",
            chapter_sha256=rules[0]["source_chapter_sha256"], rules=rules,
        )
        self.assertEqual(output, original)
        self.assertEqual(moved, 0)

    def test_approved_reader_is_separate_versioned_and_reproducible(self):
        before_html = build_private_reader(
            self.source, render=True, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        baseline_folder = (self.base / "ches-direct-reader" /
                           before_html["snapshot_id"])
        existing = {p.name: p.read_bytes() for p in baseline_folder.iterdir()
                    if p.is_file()}
        self._approved(ordinals=(1, 2))
        with (
            patch("olt_core.sources.load_ot_book",
                  side_effect=AssertionError("NO_HEBREW_VALIDATION")),
            patch("olt_core.sources.read_provenance",
                  side_effect=AssertionError("NO_SOURCE_REGISTRY")),
            patch("urllib.request.urlopen",
                  side_effect=AssertionError("NO_NETWORK")),
        ):
            report = run_private_reviewed_subject_order(
                self.source, mode="render",
            )
        self.assertEqual(report["explicitly_attested_english_subject_moves"], 2)
        self.assertEqual(report["verses_changed_in_separate_reading"], 1)
        self.assertEqual(report["private_reading_html_files_written_or_verified"], 2)
        self.assertFalse(report["hebrew_cross_validation_performed"])
        self.assertTrue(report["prior_locked_readers_unchanged"])
        view = (self.base / "ches-reviewed-subject-reading" /
                report["new_private_snapshot_id"])
        self.assertEqual(view.stat().st_mode & 0o777, 0o700)
        chapter = view / "gen.1.html"
        self.assertEqual(chapter.stat().st_mode & 0o777, 0o600)
        self.assertIn("Sailors - he-saw and Rowan - he-loved",
                      chapter.read_text())
        self.assertIn("he-is-making Worker", chapter.read_text())
        self.assertEqual(self.before, (self.source / "gen.1.json").read_bytes())
        self.assertEqual(
            existing,
            {p.name: p.read_bytes() for p in baseline_folder.iterdir()
             if p.is_file()},
        )
        again = run_private_reviewed_subject_order(self.source, mode="render")
        self.assertEqual(again["new_private_snapshot_id"],
                         report["new_private_snapshot_id"])

    def test_single_approved_pair_preserves_other_unreviewed_pair(self):
        self._approved(ordinals=(1,))
        report = run_private_reviewed_subject_order(self.source, mode="render")
        self.assertEqual(report["explicitly_attested_english_subject_moves"], 1)
        chapter = (
            self.base / "ches-reviewed-subject-reading" /
            report["new_private_snapshot_id"] / "gen.1.html"
        ).read_text()
        self.assertIn("Sailors - he-saw and he-loved Rowan", chapter)

    def test_reject_stale_sha_wrong_ordinal_and_no_fake_certification(self):
        _, _, doc = self._build_queue()
        first = dict(doc["rules"][0])
        first.update({
            "english_subject_role_reviewed": True,
            "review_note": "English subject in this clause reviewed explicitly.",
        })
        for field, wrong in (
            ("source_chapter_sha256", "f" * 64),
            ("expected_verse_english_sha256", "f" * 64),
            ("observed_verb_gloss", "he-destroyed"),
            ("observed_adjacent_noun_phrase", "Other"),
            ("candidate_ordinal", 99),
            ("english_role_class", "BOUNDED_ENGLISH_SUBJECT_PATTERN_CANDIDATE"),
        ):
            with self.subTest(field=field):
                altered = dict(first, **{field: wrong})
                with self.assertRaises(DanMek030Error):
                    apply_reviewed_english_subjects(
                        "he-saw Sailors and he-loved Rowan",
                        reference="gen.1.1",
                        chapter_sha256=first["source_chapter_sha256"],
                        rules=[altered],
                    )
        with self.assertRaises(DanMek030Error):
            apply_reviewed_english_subjects(
                "he-saw Sailors and he-loved Rowan", reference="gen.1.1",
                chapter_sha256=first["source_chapter_sha256"],
                rules=[first, first],
            )
        with self.assertRaises(DanMek030Error):
            apply_reviewed_english_subjects(
                "he-saw Sailors and he-loved Rowan", reference="gen.1.1",
                chapter_sha256=first["source_chapter_sha256"],
                rules=[dict(first, review_note="OK")],
            )

    def test_requires_explicit_review_no_autofill(self):
        self._approved(ordinals=())
        with self.assertRaisesRegex(
            DanMek030Error, "PRIVATE_SUBJECT_APPROVAL_NO_REVIEWED_MOVES",
        ):
            run_private_reviewed_subject_order(self.source, mode="render")
        self.assertFalse((self.base / "ches-reviewed-subject-reading").exists())

    def test_manifest_permissions_symlink_and_unknown_reference_fail_closed(self):
        manifest, doc = self._approved(ordinals=(1,))
        manifest.chmod(0o644)
        with self.assertRaisesRegex(
            DanMek030Error, "PRIVATE_APPROVAL_MANIFEST_MISSING_OR_UNSAFE",
        ):
            run_private_reviewed_subject_order(self.source, mode="render")
        manifest.chmod(0o600)
        doc["rules"][0]["reference"] = "exo.99.1"
        manifest.write_text(json.dumps(doc), encoding="utf-8")
        manifest.chmod(0o600)
        with self.assertRaises(DanMek030Error):
            run_private_reviewed_subject_order(self.source, mode="render")
        manifest.unlink()
        manifest.symlink_to(self.source / "gen.1.json")
        with self.assertRaisesRegex(
            DanMek030Error, "PRIVATE_APPROVAL_MANIFEST_MISSING_OR_UNSAFE",
        ):
            run_private_reviewed_subject_order(self.source, mode="render")

    def test_owner_edited_render_is_not_overwritten(self):
        self._approved(ordinals=(1,))
        report = run_private_reviewed_subject_order(self.source, mode="render")
        page = (self.base / "ches-reviewed-subject-reading" /
                report["new_private_snapshot_id"] / "gen.1.html")
        page.write_text("OWNER'S PRIVATE NOTE", encoding="utf-8")
        page.chmod(0o600)
        with self.assertRaisesRegex(DanMek030Error, "PRIVATE_READING_NO_OVERWRITE"):
            run_private_reviewed_subject_order(self.source, mode="render")
        self.assertEqual(page.read_text(), "OWNER'S PRIVATE NOTE")

    def test_private_source_changes_block_existing_manifest(self):
        self._approved(ordinals=(1,))
        original = invented_chapter("gen", 1)
        original["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors and he-loved Rowan today"
        original["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(original, self.source / "gen.1.json")
        with self.assertRaisesRegex(
            DanMek030Error, "PRIVATE_ENGLISH_APPROVAL_SCHEMA_OR_SNAPSHOT",
        ):
            run_private_reviewed_subject_order(self.source, mode="render")

    def test_311_required_on_actual_archive_only(self):
        with self.assertRaisesRegex(
            DanMek030Error, "PRIVATE_SUBJECT_REVIEW_EXPECTED_311_CHANGED",
        ):
            run_private_reviewed_subject_order(
                self.source, mode="review", require_311=True,
            )
        self.assertFalse((self.base / "ches-subject-review").exists())

    def test_queue_html_escapes_raw_english(self):
        chapter = invented_chapter("gen", 1)
        chapter["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-saw Sailors <img src=x onerror=alert(1)>"
        chapter["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker"
        write_private_json(chapter, self.source / "gen.1.json")
        self._build_queue()
        page = next((self.base / "ches-subject-review").glob("queue-*.html"))
        data = page.read_text()
        self.assertIn("&lt;img", data)
        self.assertNotIn("<img", data)
        self.assertNotIn("<script", data)

    def test_metadata_cli_never_logs_english_or_local_paths(self):
        with patch("sys.argv", [
            "danmek-030", "--private-root", str(self.source),
            "--confirm-machine-readable-use-permission", "--audit-only",
        ]):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["potential_subject_role_reviews_queued"], 3)
        for private in ("Sailors", "Rowan", "Worker", "gen.1.1",
                        str(self.source)):
            self.assertNotIn(private, output.getvalue())
        self.assertFalse((self.base / "ches-subject-review").exists())

    def test_duplicate_json_keys_rejected_without_private_content(self):
        manifest, doc = self._approved(ordinals=(1,))
        manifest.write_text(
            '{"schema":"x","schema":"y","rules":[]}', encoding="utf-8",
        )
        manifest.chmod(0o600)
        with self.assertRaises(DanMek030Error):
            run_private_reviewed_subject_order(self.source, mode="render")


if __name__ == "__main__":
    unittest.main()
