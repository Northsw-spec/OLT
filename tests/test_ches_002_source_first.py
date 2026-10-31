"""CHES-002: original-language, private third-party source and English pilot gates."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from olt_core.english_drafts import (
    EnglishDraftContractError, build_genesis_one_drafts,
    validate_research_token, verified_wayyiqtol,
)
from scripts.ches_oshb_verse_qa import (
    CHESVerseQAError, verify_genesis_1_verse_locators,
)

ROOT = Path(__file__).resolve().parents[1]


def synthetic_private_genesis_one():
    """Only fake spans. Never embed real copyrighted CHES PDF text in unit tests."""
    manifest = json.loads((ROOT / "data/engine/olt_ches_source_manifest.json").read_text())
    info = manifest["source_reference"]
    rows = []
    for n in range(1, 32):
        # One original chapter had 526 PDF green spans; distribution here is
        # deliberately synthetic, NOT an asserted actual per-verse mapping.
        spans = [{}] * (16 if n == 1 else 17)
        rows.append({
            "reference": f"Gen.1.{n}",
            "source_ches_spans_NOT_OLT_TRANSLATION": spans,
            "publication_status": "BLOCKED",
        })
    return {
        "book": "Gen",
        "chapter": 1,
        "original_source_pdf_sha256": info["source_pdf_sha256"],
        "source_pdf_byte_length": info["source_pdf_bytes"],
        "source_pdf_page_count": info["source_pdf_pages"],
        "verses_extracted": 31,
        "ches_pdf_green_spans": 526,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }


class TestCHES002SourceFirstPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.drafts = build_genesis_one_drafts()

    def test_real_pinned_oshb_research_31_verses_434_words_50_wayyiqtol(self):
        d = self.drafts
        self.assertEqual((d["original_verse_count_verified"],
                          d["original_word_count_verified"],
                          d["wayyiqtol_simple_past_token_fragment_checks"]), (31, 434, 50))
        self.assertEqual(len(d["verses"]), 31)
        self.assertEqual(d["verses"][0]["reference"], "Gen.1.1")
        self.assertEqual(d["verses"][-1]["reference"], "Gen.1.31")
        self.assertIn("He shaped", d["verses"][0]["english_text_unapproved"])
        self.assertFalse(d["english_translation_owner_approved"])
        self.assertFalse(d["complete_english_bible_owner_approved"])
        self.assertEqual(d["publication_status"], "BLOCKED")
        self.assertEqual(d["ches_word_level_correspondence"], "NOT_DONE")
        self.assertTrue(all(v["english_status"] == "UNREVIEWED_ENGLISH_DRAFT"
                            for v in d["verses"]))

    def test_non_qal_wayyiqtol_stems_recognized_from_actual_morphology(self):
        for raw in ("HC/Vqw3ms", "HC/Vhw3fs", "HC/Vpw3ms"):
            self.assertTrue(verified_wayyiqtol(raw))
        for raw in ("HVqp3ms", "HC/Vhp3ms", "HNcmpa"):
            self.assertFalse(verified_wayyiqtol(raw))

    def test_mismatched_source_id_approval_and_perfect_tense_all_fail_closed(self):
        source = {"source_id": "real", "hebrew": "example", "lemma_raw": "1254 a",
                  "morph_raw": "HC/Vhw3ms"}
        draft = {"source_ordinal": 1, "source_token_id": "real",
                 "original_hebrew": "example", "original_lemma": "1254 a",
                 "original_morphology": "HC/Vhw3ms",
                 "english_approved": False, "source_wayyiqtol": True,
                 "english_fragment_research_only": "And He separated"}
        self.assertTrue(validate_research_token(source, draft, "Gen.1.4", 1))
        for key, bad in (("source_token_id", "wrong"),
                         ("english_approved", True),
                         ("source_wayyiqtol", False),
                         ("english_fragment_research_only", "And He has separated")):
            with self.subTest(key=key):
                tampered = {**draft, key: bad}
                with self.assertRaises(EnglishDraftContractError):
                    validate_research_token(source, tampered, "Gen.1.4", 1)

    def test_private_chapter_verse_locator_qa_not_word_level_alignment(self):
        d = verify_genesis_1_verse_locators(synthetic_private_genesis_one())
        self.assertTrue(d["source_pdf_sha256_verified"])
        self.assertEqual(d["original_oshb_verses_checked"], 31)
        self.assertEqual(d["original_oshb_word_tokens_observed_not_ches_aligned"], 434)
        self.assertEqual(d["private_pdf_green_spans_observed_not_oshb_word_aligned"], 526)
        self.assertFalse(d["ches_to_oshb_word_level_alignment_verified"])
        self.assertFalse(d["whole_ot_verified"])
        self.assertFalse(d["public_ches_payload_exported"])

    def test_private_verse_locator_rejects_wrong_source_or_verse(self):
        source = synthetic_private_genesis_one()
        for field, value in (("chapter", 2),
                             ("original_source_pdf_sha256", "0"*64),
                             ("alignment_with_oshb_words_verified", True),
                             ("full_source_text_in_public_git_permitted", True)):
            with self.subTest(field=field):
                changed = {**source, field: value}
                with self.assertRaises(CHESVerseQAError):
                    verify_genesis_1_verse_locators(changed)
        changed = copy.deepcopy(source)
        changed["verses"][5]["reference"] = "Gen.1.5"
        with self.assertRaises(CHESVerseQAError):
            verify_genesis_1_verse_locators(changed)


if __name__ == "__main__":
    unittest.main()
