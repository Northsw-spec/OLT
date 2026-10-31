"""CHES-007: invented English PDF fragments, authentic pinned OSHB source IDs.

No provider-licensed English text, source PDF or copyright-sensitive private
editorial material is included in this public test fixture.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.ches_007_multichapter_english import (
    CHES007Error, _count_only_audit, build_private_pinned_english_chapter,
)
from scripts.ches_import import write_private_json
from scripts.ches_private_alignment_review import private_file

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "data/engine/olt_ches_source_manifest.json").read_text())
CASES = (
    ("Gen", 2, 25, 328, 377, "additional_chapter_layout_source_reference"),
    ("Gen", 3, 24, 347, 415, "third_chapter_layout_source_reference"),
    ("Exod", 1, 22, 240, 350, "cross_book_layout_source_reference"),
)


def fake_chapter(case: tuple) -> dict:
    book, chapter, verse_count, _words, total_spans, key = case
    pinned = MANIFEST[key]
    per_verse, remainder = divmod(total_spans, verse_count)
    rows = []
    for number in range(1, verse_count + 1):
        spans = [
            {
                "page": min(pinned["source_pdf_pages"], 1 + (number - 1)//9),
                "pdf_x": float(10 + i),
                "pdf_y": float(number * 12),
                "original_ches_line_text": f"FAKE-GLOSS-{book}-{chapter}-{number}-{i}",
            }
            for i in range(per_verse + int(number <= remainder))
        ]
        rows.append({
            "reference": f"{book}.{chapter}.{number}",
            "source_ches_spans_NOT_OLT_TRANSLATION": spans,
            "publication_status": "BLOCKED",
        })
    return {
        "book": book, "chapter": chapter,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "independent_grammar_or_sense_approved": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "source_pdf_byte_length": pinned["source_pdf_bytes"],
        "source_pdf_page_count": pinned["source_pdf_pages"],
        "original_source_pdf_sha256": pinned["source_pdf_sha256"],
        "verses_extracted": verse_count,
        "ches_pdf_green_spans": total_spans,
        "verses": rows,
    }


def example_edit(case: tuple) -> dict:
    book, chapter, _, _, _, pin_name = case
    return {
        "original_source_pdf_sha256": MANIFEST[pin_name]["source_pdf_sha256"],
        "chapter_reference": f"{book}.{chapter}",
        "unapproved_verse_edits": [{
            "reference": f"{book}.{chapter}.2",
            "english_text_unapproved": "Example private reviewed English verse, still unapproved.",
            "editor_note_private": "Inspected original Hebrew against private interlinear verse evidence.",
            "approved": False,
        }],
    }


class TestCHES007MultichapterEnglishDraft(unittest.TestCase):
    def test_all_three_new_chapters_produce_real_oshb_anchored_private_glosses(self):
        for case in CASES:
            with self.subTest(chapter=f"{case[0]}.{case[1]}"):
                book, chapter, expected_verses, expected_words, expected_green, _ = case
                report = build_private_pinned_english_chapter(fake_chapter(case))
                self.assertEqual(report["checkpoint"], "CHES-007")
                self.assertEqual(report["scope"], f"{book}.{chapter}")
                self.assertEqual(report["verse_count"], expected_verses)
                self.assertEqual(report["original_hebrew_token_count"], expected_words)
                self.assertEqual(report["original_ches_pdf_green_span_count"], expected_green)
                self.assertEqual(report["source_verse_qa_count_only"]["source_pin_status"],
                                 "ORIGINAL_PDF_PINNED_EXACT")
                self.assertFalse(report["original_pdf_bytes_reparsed_in_this_function"])
                self.assertFalse(report["old_full_lexical_engine_required"])
                self.assertFalse(report["word_alignment_verified"])
                self.assertFalse(report["all_english_grammar_rules_applied"])
                self.assertFalse(report["english_translation_owner_approved"])
                self.assertFalse(report["complete_english_bible_owner_approved"])
                self.assertEqual(report["publication_status"], "BLOCKED")
                self.assertEqual(len(report["verses"]), expected_verses)
                self.assertEqual(report["verses"][-1]["reference"],
                                 f"{book}.{chapter}.{expected_verses}")
                total_tenses = sum(len(v["source_tagged_wayyiqtol_requirements"])
                                   for v in report["verses"])
                self.assertEqual(report["source_wayyiqtol_simple_past_requirements"], total_tenses)
                self.assertGreater(total_tenses, 0)
                for verse in report["verses"]:
                    self.assertEqual(verse["english_text_private_unapproved"],
                                     verse["ches_raw_gloss_stream_private_unapproved"])
                    self.assertEqual(verse["english_text_origin"],
                                     "MECHANICAL_CHES_SOURCE_GLOSS_STREAM_NOT_OLT_TRANSLATION")
                    self.assertFalse(verse["oshb_to_ches_word_alignment_verified"])
                    self.assertFalse(verse["all_source_grammar_rules_applied"])
                    self.assertEqual(verse["english_draft_status"],
                                     "UNREVIEWED_PRIVATE_ENGLISH_WORKING_DRAFT")
                    self.assertEqual(verse["publication_status"], "BLOCKED")
                    self.assertEqual(
                        len(verse["original_source_word_token_ids"]),
                        verse["original_source_word_count"],
                    )
                    self.assertTrue(all(
                        x["english_rule"] == "ENGLISH_SIMPLE_PAST_REQUIRED"
                        and x["corresponding_ches_gloss_span"] == "NOT_VERIFIED"
                        and x["rule_applied_to_english_text"] is False
                        for x in verse["source_tagged_wayyiqtol_requirements"]
                    ))
                    self.assertTrue(all(
                        x["ches_gloss_span_mapping"] == "NOT_VERIFIED"
                        and x["rule_applied_to_english_text"] is False
                        for x in verse["original_source_lexical_override_candidates"]
                    ))
                audit = _count_only_audit(report)
                self.assertNotIn("FAKE-GLOSS", json.dumps(audit))
                self.assertNotIn("verses", audit)
                self.assertNotIn("source_verse_qa_count_only", audit)

    def test_private_editorial_verse_level_changes_never_publish_or_approve(self):
        for case in CASES:
            with self.subTest(chapter=f"{case[0]}.{case[1]}"):
                source = fake_chapter(case)
                edited = build_private_pinned_english_chapter(source, example_edit(case))
                self.assertEqual(edited["private_editorial_verse_edits_unapproved"], 1)
                self.assertEqual(edited["verses"][1]["english_text_private_unapproved"],
                                 "Example private reviewed English verse, still unapproved.")
                self.assertEqual(edited["verses"][1]["english_text_origin"],
                                 "EXPLICIT_PRIVATE_EDITORIAL_VERSE_EDIT_UNAPPROVED")
                self.assertIn("FAKE-GLOSS",
                              edited["verses"][1]["ches_raw_gloss_stream_private_unapproved"])
                self.assertNotEqual(
                    edited["verses"][1]["ches_raw_gloss_stream_private_unapproved"],
                    edited["verses"][1]["english_text_private_unapproved"],
                )
                self.assertFalse(edited["english_translation_owner_approved"])
                with tempfile.TemporaryDirectory() as folder:
                    parent = Path(folder)
                    with self.assertRaises(ValueError):
                        private_file(parent / "not-private" / "output.json")
                    target = private_file(parent / ".olt-private" / "ches" / "draft.json")
                    write_private_json(edited, target)
                    payload = json.loads(target.read_text(encoding="utf-8"))
                    self.assertEqual(payload["publication_status"], "BLOCKED")
                    self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_bad_original_source_ids_rights_or_geometry_fail_closed(self):
        source = fake_chapter(CASES[0])
        changes = [
            ("original_source_pdf_sha256", "0"*64),
            ("source_pdf_byte_length", 9999),
            ("source_pdf_page_count", 100),
            ("ches_pdf_green_spans", 1000),
            ("verses_extracted", 24),
            ("original_source_pdf_sha256", True),
            ("source_book_identifier_is_not_verified_oshb_book_mapping", False),
            ("alignment_with_oshb_words_verified", True),
            ("full_source_text_in_public_git_permitted", True),
            ("independent_grammar_or_sense_approved", True),
            ("olt_english_translation_approved", True),
            ("publication_status", "PUBLIC"),
        ]
        for key, value in changes:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                modified = copy.deepcopy(source)
                modified[key] = value
                build_private_pinned_english_chapter(modified)
        invalid_verse = copy.deepcopy(source)
        invalid_verse["verses"][4]["reference"] = "Gen.2.4"
        with self.assertRaises(ValueError):
            build_private_pinned_english_chapter(invalid_verse)
        bad_span = copy.deepcopy(source)
        bad_span["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0]["pdf_x"] = -100
        with self.assertRaises(ValueError):
            build_private_pinned_english_chapter(bad_span)
        bad_text = copy.deepcopy(source)
        bad_text["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"] = ""
        # The shared CHES-006 layout verifier rejects an empty original
        # green span before the new draft builder's own text check.
        with self.assertRaises(ValueError):
            build_private_pinned_english_chapter(bad_text)
        wrong_scope = copy.deepcopy(source)
        wrong_scope["chapter"] = 1
        with self.assertRaises(CHES007Error):
            build_private_pinned_english_chapter(wrong_scope)

    def test_editorial_approval_duplicate_cross_chapter_and_wrong_pdf_are_rejected(self):
        case = CASES[0]
        real = fake_chapter(case)
        good = example_edit(case)
        original = good["unapproved_verse_edits"][0]
        for invalid in [
            {**good, "original_source_pdf_sha256": "f"*64},
            {**good, "chapter_reference": "Gen.3"},
            {**good, "unapproved_verse_edits": [original, original]},
            {**good, "unapproved_verse_edits": [{**original, "approved": True}]},
            {**good, "unapproved_verse_edits": [
                {**original, "reference": "Gen.3.2"}]},
            {**good, "unapproved_verse_edits": [
                {**original, "reference": "Gen.2.26"}]},
            {**good, "unapproved_verse_edits": [
                {**original, "editor_note_private": "none"}]},
            {**good, "unapproved_verse_edits": [
                {**original, "english_text_unapproved": ""}]},
            {**good, "unapproved_verse_edits": [
                {**original, "english_text_unapproved": "x" * 3001}]},
            {**good, "unapproved_verse_edits": [
                {**original, "editor_note_private": "A" * 4001}]},
            {**good, "unapproved_verse_edits": "not an array"},
            {**good, "public_release": True},
        ]:
            with self.subTest(invalid=str(invalid)[:150]), self.assertRaises(CHES007Error):
                build_private_pinned_english_chapter(real, invalid)

    def test_no_public_raw_source_in_numerical_audit_even_with_private_editor_edits(self):
        case = CASES[2]
        report = build_private_pinned_english_chapter(fake_chapter(case), example_edit(case))
        serial = json.dumps(_count_only_audit(report))
        self.assertNotIn("FAKE-GLOSS", serial)
        self.assertNotIn("Example private reviewed", serial)
        self.assertIn('"publication_status": "BLOCKED"', serial)


if __name__ == "__main__":
    unittest.main()
