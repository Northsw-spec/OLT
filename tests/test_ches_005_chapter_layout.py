"""Synthetic second-chapter PDF geometry, authentic pinned OSHB/WLC source."""
from __future__ import annotations

import copy
import unittest

from scripts.ches_005_chapter_layout_qa import (
    CHESChapterLayoutError, verify_genesis_two_layout,
)


def synthetic_genesis_two_layout() -> dict:
    rows = [
        {
            "reference": f"Gen.2.{n}",
            "publication_status": "BLOCKED",
            "source_ches_spans_NOT_OLT_TRANSLATION": [
                {
                    "page": (n-1)//7 + 1,
                    "pdf_x": 10.0 + i,
                    "pdf_y": float(n * 20),
                    "original_ches_line_text": f"FAKE-{n}-{i}",
                } for i in range(4)
            ],
        } for n in range(1, 26)
    ]
    return {
        "book": "Gen",
        "chapter": 2,
        "original_source_pdf_sha256": "a" * 64,
        "source_pdf_byte_length": 55000,
        "source_pdf_page_count": 4,
        "verses_extracted": 25,
        "ches_pdf_green_spans": 100,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }


class TestCHES005SecondChapterLayout(unittest.TestCase):
    def test_authentic_oshb_genesis_two_25_verses_and_unaligned_spans(self):
        summary = verify_genesis_two_layout(synthetic_genesis_two_layout())
        self.assertEqual(summary["printed_verse_markers_checked"], 25)
        self.assertEqual(summary["authentic_oshb_verse_references_checked"], 25)
        self.assertGreater(summary["authentic_oshb_word_tokens_observed_not_ches_aligned"], 25)
        self.assertEqual(summary["private_green_pdf_spans_observed_not_oshb_word_aligned"], 100)
        self.assertFalse(summary["word_alignment_verified"])
        self.assertFalse(summary["original_pdf_book_prefix_vs_oshb_mapping_independently_verified"])
        self.assertEqual(summary["publication_status"], "BLOCKED")

    def test_wrong_chapter_missing_or_reordered_verse_and_false_rights_are_rejected(self):
        cases = [
            ("chapter", 1), ("book", "ex"), ("verses_extracted", 24),
            ("original_source_pdf_sha256", "not-sha256"),
            ("source_pdf_page_count", True),
            ("source_pdf_byte_length", 1),
            ("full_source_text_in_public_git_permitted", True),
            ("alignment_with_oshb_words_verified", True),
            ("publication_status", "PUBLIC"),
            ("ches_pdf_green_spans", 99),
        ]
        for key, value in cases:
            with self.subTest(key=key), self.assertRaises(CHESChapterLayoutError):
                modified = synthetic_genesis_two_layout()
                modified[key] = value
                verify_genesis_two_layout(modified)
        modified = synthetic_genesis_two_layout()
        modified["verses"][8]["reference"] = "Gen.2.8"
        with self.assertRaises(CHESChapterLayoutError):
            verify_genesis_two_layout(modified)
        modified = synthetic_genesis_two_layout()
        modified["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"] = []
        with self.assertRaises(CHESChapterLayoutError):
            verify_genesis_two_layout(modified)


if __name__ == "__main__":
    unittest.main()
