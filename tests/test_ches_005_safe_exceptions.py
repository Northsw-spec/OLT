"""CHES-005: synthetic CHES glosses + pinned authentic Hebrew token assertions.

No licensed third-party original interlinear text or PDFs are stored here.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from olt_core.english_drafts import build_genesis_one_drafts, verified_wayyiqtol
from olt_core.sources import load_ot_book, read_provenance, ROOT
from scripts.ches_import import write_private_json
from scripts.ches_005_safe_exceptions import (
    CHESExceptionError, apply_source_anchored_english_exceptions,
)
from scripts.ches_private_alignment_review import private_file

PIN = json.loads(
    (ROOT / "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8")
)["source_reference"]


def fake_pdf_chapter() -> dict:
    rows = []
    for n in range(1, 32):
        rows.append({
            "reference": f"Gen.1.{n}",
            "publication_status": "BLOCKED",
            "source_ches_spans_NOT_OLT_TRANSLATION": [
                {
                    "page": 1 + (n-1)//8,
                    "pdf_x": 10.0 + i,
                    "pdf_y": float(n * 12),
                    "original_ches_line_text": f"FAKE-ENGLISH-{n}-{i}",
                }
                for i in range(16 if n == 1 else 17)
            ],
        })
    return {
        "book": "Gen",
        "chapter": 1,
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


def source_words() -> dict:
    original = load_ot_book("Gen", ROOT, read_provenance(ROOT))
    return {
        v["reference"]: v["words"] for v in original["verses"]
        if v["reference"].startswith("Gen.1.")
    }


def rule_for(ref: str, word: dict, *, kind: str, replacement: str,
             ordinal: int = 1) -> dict:
    n = int(ref.rsplit(".", 1)[1])
    return {
        "reference": ref,
        "original_oshb_source_token_id": word["source_id"],
        "expected_original_morphology": word["morph_raw"],
        "expected_original_lemma": word["lemma_raw"],
        "kind": kind,
        "green_span_ordinal": ordinal,
        "expected_green_span_text_private": f"FAKE-ENGLISH-{n}-{ordinal - 1}",
        "replacement_english_private": replacement,
        "operator_checked_original_pdf_hebrew": True,
        "evidence_note_private":
            "Private original Hebrew line and corresponding English source glyph reviewed; still unverified.",
        "approved": False,
    }


def rules_document(*entries: dict) -> dict:
    return {
        "source_pdf_sha256": PIN["source_pdf_sha256"],
        "chapter_reference": "Gen.1",
        "unapproved_exception_rules": list(entries),
    }


class TestCHES005EnglishExceptionPreview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = source_words()
        cls.research = build_genesis_one_drafts()
        cls.tense = next(
            (ref, word, r["english_fragment_simple_past_research"])
            for row in cls.research["verses"]
            for r in row["verified_source_wayyiqtol_simple_past_fragment_checks"]
            for ref, words in cls.words.items()
            if ref == row["reference"]
            for word in words if word["source_id"] == r["source_token_id"]
        )
        cls.lexical = next(
            (ref, word)
            for ref, words in cls.words.items() for word in words
            if "1254" in word["lemma_raw"].replace("/", " ").replace("+", " ").split()
            and not verified_wayyiqtol(word["morph_raw"])
        )

    def test_zero_rules_preserves_all_real_chapter_source_id_checks(self):
        result = apply_source_anchored_english_exceptions(fake_pdf_chapter(), None)
        self.assertEqual(result["checkpoint"], "CHES-005")
        self.assertEqual(len(result["verses"]), 31)
        self.assertEqual(result["original_hebrew_token_count"], 434)
        self.assertEqual(result["original_ches_pdf_green_span_count"], 526)
        self.assertEqual(result["source_wayyiqtol_simple_past_requirements"], 50)
        self.assertEqual(result["source_anchored_exception_previews_unapproved"], 0)
        self.assertEqual(result["original_chapter_english_stream_unchanged_verses"], 31)
        self.assertEqual(result["automatic_guess_based_word_substitutions"], 0)
        self.assertEqual(result["independently_verified_word_mappings"], 0)
        self.assertFalse(result["english_translation_owner_approved"])
        self.assertEqual(result["publication_status"], "BLOCKED")

    def test_exact_tense_exception_changes_only_selected_private_span(self):
        ref, word, replacement = self.tense
        proposed = rule_for(ref, word, kind="WAYYIQTOL_SIMPLE_PAST",
                            replacement=replacement, ordinal=2)
        doc = rules_document(proposed)
        result = apply_source_anchored_english_exceptions(fake_pdf_chapter(), doc)
        verse = next(v for v in result["verses"] if v["reference"] == ref)
        untouched = f"FAKE-ENGLISH-{ref.rsplit('.', 1)[1]}-0"
        original = f"FAKE-ENGLISH-{ref.rsplit('.', 1)[1]}-1"
        self.assertIn(untouched, verse["english_text_private_unapproved"])
        self.assertNotIn(original, verse["english_text_private_unapproved"])
        self.assertIn(replacement, verse["english_text_private_unapproved"])
        self.assertIn(original, verse["ches_raw_gloss_stream_private_unapproved"])
        self.assertEqual(result["source_anchored_exception_previews_unapproved"], 1)
        self.assertEqual(result["original_chapter_english_stream_unchanged_verses"], 30)
        self.assertEqual(verse["english_text_origin"],
                         "OPERATOR_SOURCE_ANCHORED_EXCEPTION_PREVIEW_UNAPPROVED")
        self.assertFalse(verse["word_alignment_verified"])
        self.assertFalse(verse["all_source_grammar_rules_applied"])
        self.assertFalse(verse["english_owner_approved"])
        evidence = verse["operator_exception_proofs_private_unapproved"][0]
        self.assertEqual(evidence["original_oshb_source_token_id"], word["source_id"])
        self.assertIs(evidence["semantic_mapping_independently_certified"], False)

    def test_owner_lexical_exception_uses_exact_original_lemma_not_guess(self):
        ref, word = self.lexical
        requested = rule_for(ref, word, kind="OWNER_LEXICAL_CHOICE",
                             replacement="shaped", ordinal=2)
        result = apply_source_anchored_english_exceptions(
            fake_pdf_chapter(), rules_document(requested)
        )
        row = next(v for v in result["verses"] if v["reference"] == ref)
        self.assertIn("shaped", row["english_text_private_unapproved"])
        self.assertEqual(row["english_text_origin"],
                         "OPERATOR_SOURCE_ANCHORED_EXCEPTION_PREVIEW_UNAPPROVED")
        self.assertFalse(result["word_alignment_verified"])
        self.assertFalse(result["english_translation_owner_approved"])

    def test_wrong_source_identity_license_and_rules_never_modify_a_draft(self):
        ref, word, replacement = self.tense
        good = rule_for(ref, word, kind="WAYYIQTOL_SIMPLE_PAST",
                        replacement=replacement, ordinal=1)
        bads = [
            {**good, "original_oshb_source_token_id": "not-a-real-token"},
            {**good, "reference": "Gen.2.1"},
            {**good, "expected_original_morphology": "HC/Vqp3ms"},
            {**good, "expected_original_lemma": "9999"},
            {**good, "green_span_ordinal": 9999},
            {**good, "green_span_ordinal": True},
            {**good, "expected_green_span_text_private": "wrong glossary"},
            {**good, "approved": True},
            {**good, "operator_checked_original_pdf_hebrew": False},
            {**good, "replacement_english_private": "and he has said"},
            {**good, "replacement_english_private": "and he had said"},
            {**good, "replacement_english_private": "and he said "},
            {**good, "evidence_note_private": "trust me"},
            {**good, "kind": "GUESSED_AUTOMATIC_TRANSLATION"},
        ]
        # Distinct curated Genesis 1 verbs cannot be substituted for this
        # particular authentic original word even if both are simple past.
        other_fragment = next(
            r["english_fragment_simple_past_research"]
            for v in self.research["verses"]
            for r in v["verified_source_wayyiqtol_simple_past_fragment_checks"]
            if r["english_fragment_simple_past_research"].casefold() != replacement.casefold()
        )
        bads.append({**good, "replacement_english_private": other_fragment})
        for index, candidate in enumerate(bads):
            with self.subTest(index=index), self.assertRaises(CHESExceptionError):
                apply_source_anchored_english_exceptions(
                    fake_pdf_chapter(), rules_document(candidate)
                )
        for document in [
            {**rules_document(good), "source_pdf_sha256": "f" * 64},
            {**rules_document(good), "chapter_reference": "Gen.2"},
            {**rules_document(good), "public_export_approved": True},
            rules_document(good, good),
        ]:
            with self.assertRaises(CHESExceptionError):
                apply_source_anchored_english_exceptions(fake_pdf_chapter(), document)
        for metadata, value in [
            ("source_pdf_page_count", 99),
            ("alignment_with_oshb_words_verified", True),
            ("publication_status", "PUBLIC"),
        ]:
            tampered = fake_pdf_chapter()
            tampered[metadata] = value
            with self.assertRaises(ValueError):
                apply_source_anchored_english_exceptions(tampered, rules_document(good))

    def test_morphology_rule_and_lexical_rule_cannot_be_swapped(self):
        tense_ref, tense_word, _ = self.tense
        lex_ref, lex_word = self.lexical
        wrong_tense = rule_for(lex_ref, lex_word, kind="WAYYIQTOL_SIMPLE_PAST",
                              replacement="and he said")
        wrong_lex = rule_for(tense_ref, tense_word, kind="OWNER_LEXICAL_CHOICE",
                             replacement="shaped")
        for proposal in (wrong_tense, wrong_lex):
            with self.subTest(kind=proposal["kind"]), self.assertRaises(CHESExceptionError):
                apply_source_anchored_english_exceptions(
                    fake_pdf_chapter(), rules_document(proposal)
                )

    def test_private_output_only_contains_no_public_ches_glosses(self):
        ref, word, replacement = self.tense
        payload = apply_source_anchored_english_exceptions(
            fake_pdf_chapter(),
            rules_document(rule_for(ref, word, kind="WAYYIQTOL_SIMPLE_PAST",
                                    replacement=replacement)),
        )
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            with self.assertRaises(ValueError):
                private_file(base / "public/english.json")
            path = private_file(base / ".olt-private" / "ches" / "english.json")
            write_private_json(payload, path)
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["checkpoint"], "CHES-005")
            self.assertEqual(loaded["publication_status"], "BLOCKED")
            self.assertIn("FAKE-ENGLISH", loaded["verses"][0]["ches_raw_gloss_stream_private_unapproved"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
