"""CHES-006: synthetic geometry, real pinned original Hebrew/Aramaic source.

Tests never include licensed source text. Metadata-only results and explicit
uncertainty flags keep false PDF-span ↔ Hebrew-word alignment impossible.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.ches_006_layout_metrics import (
    CHESLayoutMetricsError, measure_private_chapter_layout,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "data/engine/olt_ches_source_manifest.json").read_text())


def dummy(book="Gen", chapter=1):
    known = {
        ("Gen", 1): (31, "source_reference", 4),
        ("Gen", 2): (25, "additional_chapter_layout_source_reference", 3),
        ("Gen", 3): (24, "third_chapter_layout_source_reference", 3),
        ("Exod", 1): (22, "cross_book_layout_source_reference", 3),
    }
    count, manifest_key, pages = known[(book, chapter)]
    pin = MANIFEST[manifest_key] if manifest_key else {}
    rows = []
    raw = []
    for i in range(1, count + 1):
        page = 1 + (i - 1) // (8 if count == 31 else 9)
        if count == 31:
            green_count = 16 if i == 1 else 17
        elif count == 25:
            green_count = 16 if i <= 2 else 15
        elif count == 24:
            green_count = 18 if i <= 7 else 17
        else:
            green_count = 16 if i <= 20 else 15
        gray_marker = {"page": page, "x": 5.0, "y": float(i*20 - 1),
                       "color": 0x888888, "text": f"{chapter}:{i}"}
        raw.append(gray_marker)
        spans = []
        for ordinal in range(green_count):
            text = f"INVENTED-{book}-{chapter}-{i}-{ordinal}"
            span = {"page": page, "pdf_x": float(12+ordinal),
                    "pdf_y": float(i*20), "original_ches_line_text": text}
            spans.append(span)
            raw.append({
                "page": page, "x": span["pdf_x"], "y": span["pdf_y"],
                "color": 0x008000, "text": text,
            })
        rows.append({
            "reference": f"{book}.{chapter}.{i}",
            "publication_status": "BLOCKED",
            "source_ches_spans_NOT_OLT_TRANSLATION": spans,
        })
    ches_total = sum(len(r["source_ches_spans_NOT_OLT_TRANSLATION"]) for r in rows)
    source = {
        "book": book, "chapter": chapter,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "olt_english_translation_approved": False,
        "independent_grammar_or_sense_approved": False,
        "publication_status": "BLOCKED",
        "verses_extracted": count,
        "original_source_pdf_sha256": pin.get("source_pdf_sha256", "a"*64),
        "source_pdf_byte_length": pin.get("source_pdf_bytes", 20000),
        "source_pdf_page_count": pin.get("source_pdf_pages", pages),
        "ches_pdf_green_spans": ches_total,
        "verses": rows,
    }
    return source, raw


class TestCHES006GeometryAndSourceMetrics(unittest.TestCase):
    def test_both_pinned_chapters_original_word_identity_and_telemetry(self):
        counts = {
            1: {"verses": 31, "words": 434, "green": 526, "pages": 4},
            2: {"verses": 25, "words": 328, "green": 377, "pages": 3},
        }
        for chapter, expected in counts.items():
            with self.subTest(chapter=chapter):
                source, raw = dummy("Gen", chapter)
                report = measure_private_chapter_layout(source, full_pdf_spans=raw)
                self.assertEqual(report["source_pin_status"], "ORIGINAL_PDF_PINNED_EXACT")
                self.assertEqual(report["authentic_oshb_verse_references_checked"],
                                 expected["verses"])
                self.assertEqual(report["authentic_oshb_word_tokens_observed_not_ches_aligned"],
                                 expected["words"])
                self.assertEqual(report["private_pdf_green_spans_observed_not_oshb_word_aligned"],
                                 expected["green"])
                self.assertEqual(report["source_pdf_page_count"], expected["pages"])
                self.assertEqual(report["printed_verse_markers_checked"], expected["verses"])
                self.assertEqual(report["raw_original_pdf_green_span_count"], expected["green"])
                self.assertEqual(report["unassigned_original_green_spans"], 0)
                self.assertEqual(report["raw_original_green_spans_before_first_printed_verse"], 0)
                self.assertFalse(report["source_pdf_book_prefix_vs_oshb_mapping_independently_verified"])
                self.assertFalse(report["oshb_to_pdf_word_alignment_verified"])
                self.assertFalse(report["english_grammar_rules_automatically_applied"])
                self.assertFalse(report["full_old_testament_processed"])
                self.assertEqual(report["publication_status"], "BLOCKED")
                self.assertNotIn("INVENTED-", json.dumps(report))

    def test_unassigned_source_ink_cannot_bypass_exact_pinned_zero_loss_baseline(self):
        # The genuine hash-pinned source has exactly ZERO unassigned green
        # spans. A synthetic green span injected before the first verse must
        # fail rather than weaken the published engineering evidence.
        source, raw = dummy("Gen", 1)
        raw.append({"page": 1, "x": 5.0, "y": 0.0, "color": 0x008000,
                    "text": "SYNTHETIC-UNASSIGNED-INK"})
        with self.assertRaises(CHESLayoutMetricsError):
            measure_private_chapter_layout(source, full_pdf_spans=raw)
        # An extra fragment elsewhere is also unexplained data and fails.
        other_source, other_raw = dummy("Gen", 2)
        other_raw.append({"page": 2, "x": 100.0, "y": 200.0,
                          "color": 0x008000, "text": "SYNTHETIC-LOST"})
        with self.assertRaises(CHESLayoutMetricsError):
            measure_private_chapter_layout(other_source, full_pdf_spans=other_raw)

    def test_new_chapters_are_pinned_and_do_not_accept_changed_original_files(self):
        for book, chapter, expected_spans, expected_words in (
            ("Gen", 3, 415, 347), ("Exod", 1, 350, 240)
        ):
            with self.subTest(book=book, chapter=chapter):
                source, raw = dummy(book, chapter)
                result = measure_private_chapter_layout(source, full_pdf_spans=raw)
                self.assertEqual(result["source_pin_status"], "ORIGINAL_PDF_PINNED_EXACT")
                self.assertEqual(result["private_pdf_green_spans_observed_not_oshb_word_aligned"],
                                 expected_spans)
                self.assertEqual(result["authentic_oshb_word_tokens_observed_not_ches_aligned"],
                                 expected_words)
                self.assertEqual(result["printed_verse_markers_checked"], len(source["verses"]))
                self.assertEqual(result["unassigned_original_green_spans"], 0)
                self.assertFalse(result["oshb_to_pdf_word_alignment_verified"])
                wrong = copy.deepcopy(source)
                wrong["original_source_pdf_sha256"] = "0" * 64
                with self.assertRaises(CHESLayoutMetricsError):
                    measure_private_chapter_layout(wrong, full_pdf_spans=raw)

    def test_pinned_original_source_identity_and_rights_never_relaxed(self):
        source, raw = dummy("Gen", 1)
        attempts = [
            ("original_source_pdf_sha256", "0"*64),
            ("source_pdf_page_count", 99),
            ("source_pdf_byte_length", 55000),
            ("ches_pdf_green_spans", 525),
            ("verses_extracted", 30),
            ("original_source_pdf_sha256", True),
            ("full_source_text_in_public_git_permitted", True),
            ("source_book_identifier_is_not_verified_oshb_book_mapping", False),
            ("alignment_with_oshb_words_verified", True),
            ("olt_english_translation_approved", True),
            ("independent_grammar_or_sense_approved", True),
            ("publication_status", "PUBLIC"),
        ]
        for field, value in attempts:
            with self.subTest(field=field, value=value), self.assertRaises(CHESLayoutMetricsError):
                modified = copy.deepcopy(source)
                modified[field] = value
                measure_private_chapter_layout(modified, full_pdf_spans=raw)
        wrong, raw = dummy("Gen", 1)
        wrong["verses"][9]["reference"] = "Gen.1.9"
        with self.assertRaises(CHESLayoutMetricsError):
            measure_private_chapter_layout(wrong, full_pdf_spans=raw)
        wrong, raw = dummy("Gen", 1)
        wrong["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0]["pdf_x"] = -1
        with self.assertRaises(CHESLayoutMetricsError):
            measure_private_chapter_layout(wrong, full_pdf_spans=raw)

    def test_marker_mismatch_or_raw_green_ink_loss_is_rejected(self):
        source, raw = dummy("Gen", 2)
        raw = [s for s in raw if not (s["color"] == 0x888888 and s["text"] == "2:4")]
        with self.assertRaises(CHESLayoutMetricsError):
            measure_private_chapter_layout(source, full_pdf_spans=raw)
        source, raw = dummy("Gen", 2)
        raw = [s for s in raw if not (s["color"] == 0x008000 and
                                      s["text"] == "INVENTED-Gen-2-5-0")]
        with self.assertRaises(CHESLayoutMetricsError):
            measure_private_chapter_layout(source, full_pdf_spans=raw)


if __name__ == "__main__":
    unittest.main()
