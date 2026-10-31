"""CHES-004: invented green English strings, genuine pinned Hebrew source records.

No licensed CHES original PDF or English fragment is committed in test fixtures.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.ches_import import write_private_json
from scripts.ches_lite_english import (
    CHESLiteError, _audit, build_private_genesis_one_english_drafts,
    _editorial_edits, _source_lemma_parts,
)
from scripts.ches_private_alignment_review import private_file

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / "data/engine/olt_ches_source_manifest.json").read_text())["source_reference"]


def synthetic_source() -> dict:
    rows = []
    for number in range(1, 32):
        count = 16 if number == 1 else 17
        rows.append({
            "reference": f"Gen.1.{number}",
            "publication_status": "BLOCKED",
            "source_ches_spans_NOT_OLT_TRANSLATION": [
                {"page": (number - 1) // 8 + 1, "pdf_x": float(10 + x),
                 "pdf_y": float(number * 10), "original_ches_line_text": f"FAKE-GLOSS-{number}-{x}"}
                for x in range(count)
            ],
        })
    return {
        "book": "Gen", "chapter": 1,
        "original_source_pdf_sha256": PIN["source_pdf_sha256"],
        "source_pdf_byte_length": PIN["source_pdf_bytes"],
        "source_pdf_page_count": PIN["source_pdf_pages"],
        "verses_extracted": 31,
        "ches_pdf_green_spans": 526,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }


def private_editorial() -> dict:
    return {
        "original_source_pdf_sha256": PIN["source_pdf_sha256"],
        "chapter_reference": "Gen.1",
        "unapproved_verse_edits": [{
            "reference": "Gen.1.1",
            "english_text_unapproved": "Editorial unapproved verse one draft.",
            "editor_note_private": "Compared verse-level interlinear and original Hebrew source.",
            "approved": False,
        }],
    }


class TestCHESLitePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_private_genesis_one_english_drafts(synthetic_source())

    def test_actual_oshb_sources_plus_synthetic_private_english_gloss_stream(self):
        result = self.report
        self.assertEqual(result["checkpoint"], "CHES-004")
        self.assertEqual(result["genesis_verse_count"], 31)
        self.assertEqual(result["original_hebrew_token_count"], 434)
        self.assertEqual(result["original_ches_pdf_green_span_count"], 526)
        self.assertEqual(result["source_wayyiqtol_simple_past_requirements"], 50)
        self.assertFalse(result["old_full_lexical_engine_required"])
        self.assertFalse(result["word_alignment_verified"])
        self.assertFalse(result["all_english_grammar_rules_applied"])
        self.assertFalse(result["english_translation_owner_approved"])
        self.assertEqual(result["publication_status"], "BLOCKED")
        self.assertEqual(result["verses"][-1]["reference"], "Gen.1.31")
        one = result["verses"][0]
        self.assertEqual(one["english_text_origin"],
                         "MECHANICAL_CHES_SOURCE_GLOSS_STREAM_NOT_OLT_TRANSLATION")
        self.assertIn("FAKE-GLOSS-1-0", one["ches_raw_gloss_stream_private_unapproved"])
        self.assertEqual(one["english_text_private_unapproved"],
                         one["ches_raw_gloss_stream_private_unapproved"])
        self.assertEqual(len(one["original_source_word_token_ids"]), 7)
        self.assertEqual(one["private_original_ches_green_span_count"], 16)
        self.assertTrue(all(not v["word_alignment_verified"] for v in result["verses"]))

    def test_wayyiqtol_and_owner_lexical_choices_are_rule_candidates_not_rewrites(self):
        verses = self.report["verses"]
        all_tense = [rule for v in verses for rule in v["source_tagged_wayyiqtol_requirements"]]
        self.assertEqual(len(all_tense), 50)
        self.assertTrue(all(r["english_rule"] == "ENGLISH_SIMPLE_PAST_REQUIRED"
                            and r["english_source_fragment_mapping"] == "NOT_VERIFIED"
                            and r["rule_applied_to_ches_gloss_stream"] is False
                            for r in all_tense))
        self.assertEqual(_source_lemma_parts("b/1254 a"), {"b", "1254", "a"})
        self.assertEqual(_source_lemma_parts("c/6213"), {"c", "6213"})
        for verse in verses:
            self.assertNotIn("ENGLISH_SIMPLE_PAST", verse["english_text_private_unapproved"])
            for c in verse["original_source_lexical_override_candidates"]:
                self.assertEqual(c["ches_gloss_span_mapping"], "NOT_VERIFIED")
                self.assertEqual(c["rule_application"],
                                 "PENDING_REVIEW_NO_AUTOMATIC_TEXT_REPLACEMENT")

    def test_explicit_private_editorial_verse_edit_is_a_draft_not_approval(self):
        source = synthetic_source()
        edited = build_private_genesis_one_english_drafts(source, private_editorial())
        self.assertEqual(edited["private_editorial_verse_edits_unapproved"], 1)
        self.assertEqual(edited["verses"][0]["english_text_private_unapproved"],
                         "Editorial unapproved verse one draft.")
        self.assertEqual(edited["verses"][0]["english_text_origin"],
                         "EXPLICIT_PRIVATE_EDITORIAL_VERSE_EDIT_UNAPPROVED")
        self.assertIn("FAKE-GLOSS", edited["verses"][0]["ches_raw_gloss_stream_private_unapproved"])
        self.assertEqual(edited["verses"][1]["english_text_origin"],
                         "MECHANICAL_CHES_SOURCE_GLOSS_STREAM_NOT_OLT_TRANSLATION")
        self.assertFalse(edited["english_translation_owner_approved"])
        self.assertFalse(edited["verses"][0]["all_source_grammar_rules_applied"])
        self.assertEqual(edited["publication_status"], "BLOCKED")

    def test_invalid_edits_fail_closed_instead_of_trusting_language_approval(self):
        source = synthetic_source()
        good = private_editorial()
        cases = [
            {**good, "original_source_pdf_sha256": "0" * 64},
            {**good, "chapter_reference": "Gen.2"},
            {**good, "english_approved": True},
            {**good, "unapproved_verse_edits": [good["unapproved_verse_edits"][0]] * 2},
            {**good, "unapproved_verse_edits": [
                {**good["unapproved_verse_edits"][0], "approved": True}]},
            {**good, "unapproved_verse_edits": [
                {**good["unapproved_verse_edits"][0], "reference": "Gen.2.1"}]},
            {**good, "unapproved_verse_edits": [
                {**good["unapproved_verse_edits"][0], "editor_note_private": "no"}]},
            {**good, "unapproved_verse_edits": [
                {**good["unapproved_verse_edits"][0], "english_text_unapproved": ""}]},
        ]
        for i, bad in enumerate(cases):
            with self.subTest(case=i), self.assertRaises(CHESLiteError):
                build_private_genesis_one_english_drafts(copy.deepcopy(source), bad)

    def test_tampered_pdf_metadata_verse_or_source_text_geometry_fails_closed(self):
        for field, value in (
            ("original_source_pdf_sha256", "f" * 64),
            ("source_pdf_page_count", 5),
            ("alignment_with_oshb_words_verified", True),
            ("full_source_text_in_public_git_permitted", True),
        ):
            with self.subTest(field=field):
                s = synthetic_source()
                s[field] = value
                with self.assertRaises(ValueError):
                    build_private_genesis_one_english_drafts(s)
        for key, bad in [
            ("page", 999), ("page", True), ("pdf_x", float("nan")),
            ("pdf_y", -4), ("original_ches_line_text", ""), ("original_ches_line_text", "x\x00y"),
        ]:
            with self.subTest(key=key):
                s = synthetic_source()
                s["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][key] = bad
                with self.assertRaises(CHESLiteError):
                    build_private_genesis_one_english_drafts(s)
        s = synthetic_source()
        s["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0]["pdf_x"] = 100
        with self.assertRaises(CHESLiteError):
            build_private_genesis_one_english_drafts(s)

    def test_audit_only_includes_counts_and_status_not_copyrighted_english(self):
        report = _audit(self.report)
        serial = json.dumps(report)
        self.assertNotIn("FAKE-GLOSS", serial)
        self.assertNotIn("verses", report)
        self.assertNotIn("source_verse_qa", report)
        self.assertEqual(report["original_ches_pdf_green_span_count"], 526)
        self.assertEqual(report["publication_status"], "BLOCKED")
        with tempfile.TemporaryDirectory() as root_str:
            root = Path(root_str)
            with self.assertRaises(ValueError):
                private_file(root / "english-draft.json")
            output = private_file(root / ".olt-private" / "ches" / "gen1-english.json")
            write_private_json(self.report, output)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("FAKE-GLOSS", data["verses"][0]["ches_raw_gloss_stream_private_unapproved"])
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
