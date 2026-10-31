"""Synthetic Nehemiah 7 verse-numbering regressions; real PDF only in isolated CI.

No original third-party source glosses/PDF bytes in repository or test output.
"""
from __future__ import annotations

import os
from pathlib import Path
import unittest

from scripts.ches_import import (
    assign_ches_to_explicit_verses,
    explicit_verse_markers,
    import_private_pdf,
    is_ches_green,
    page_spans,
)

PRIMARY = tuple(range(1, 68)) + tuple(range(69, 74))


def invented_chapter() -> list[dict]:
    rows = []
    for verse in PRIMARY:
        y = 30.0 + verse * 12
        # Gray primary digits and nearby BLACK numeric alternatives mimic
        # the actual printed original Nehemiah 7 PDF glyph geometry.
        rows.extend([
            {"text": "7", "page": 1, "x": 30, "y": y, "color": 0x888888},
            {"text": f":{verse}", "page": 1, "x": 35, "y": y, "color": 0x888888},
            {"text": "ARTIFICIAL-ENGLISH-ONLY", "page": 1, "x": 90,
             "y": y + 4, "color": 0x008000},
            {"text": "Fake AV column", "page": 1, "x": 700, "y": y,
             "color": 0x000000},
        ])
        if verse >= 69:
            rows.append({
                "text": f"(7:{verse - 1})", "page": 1, "x": 50,
                "y": y + 1.5, "color": 0x000000
            })
    return rows


class TestNehemiahSevenSourceNumbering(unittest.TestCase):
    def test_primary_missing_68_and_five_explicit_alternates_remain_separate(self):
        source = invented_chapter()
        actual = assign_ches_to_explicit_verses(
            source, 7, expected_verses=72, source_book="neh"
        )
        self.assertEqual(tuple(v["verse"] for v in actual), PRIMARY)
        self.assertEqual(len(actual), 72)
        self.assertEqual(
            [(v["verse"], v["alternate_verse"]) for v in actual if v["alternate_verse"]],
            [(n, n - 1) for n in range(69, 74)],
        )
        self.assertEqual(sum(len(v["ches_spans"]) for v in actual), 72)
        self.assertFalse(any("Fake AV" in str(v["ches_spans"]) for v in actual))
        self.assertNotIn(68, [v["verse"] for v in actual])
        self.assertEqual(actual[-1]["verse"], 73)
        self.assertEqual(actual[-1]["alternate_verse"], 72)

    def test_exception_must_never_apply_to_other_book_or_chapter(self):
        for book, chapter in [("gen", 7), ("neh", 8), (None, 7)]:
            with self.subTest(book=book, chapter=chapter), self.assertRaises(ValueError):
                assign_ches_to_explicit_verses(
                    invented_chapter(), chapter, source_book=book
                )

    def test_bad_alt_or_noncanonical_verse_gap_must_fail_closed(self):
        for original, replacement in [
            ("(7:68)", "(7:67)"),
            ("(7:68)", "(6:68)"),
            ("(7:68)", "(7:69)"),
            ("(7:68)", ""),
            (":67", ":68"),
            (":69", ":68"),
        ]:
            source = invented_chapter()
            for span in source:
                if original in span["text"] and (span["color"] == 0x888888 or
                                                 span["text"].startswith("(")):
                    span["text"] = span["text"].replace(original, replacement, 1)
                    break
            with self.subTest(change=(original, replacement)), self.assertRaises(ValueError):
                assign_ches_to_explicit_verses(
                    source, 7, expected_verses=72, source_book="neh"
                )

    def test_black_alternative_must_be_unique_nearby_and_exact(self):
        for field, value in (
            ("x", 550),
            ("y", 9000),
            ("color", 0x888888),
        ):
            with self.subTest(field=field):
                source = invented_chapter()
                alt = next(row for row in source if row["text"] == "(7:68)")
                alt[field] = value
                with self.assertRaises(ValueError):
                    assign_ches_to_explicit_verses(
                        source, 7, expected_verses=72, source_book="neh"
                    )
        duplicate = invented_chapter()
        duplicate.append(next(
            row.copy() for row in duplicate if row["text"] == "(7:68)"
        ))
        with self.assertRaises(ValueError):
            assign_ches_to_explicit_verses(
                duplicate, 7, expected_verses=72, source_book="neh"
            )

    def test_gap_cannot_be_declared_73_verses_without_printed_source(self):
        with self.assertRaises(ValueError):
            assign_ches_to_explicit_verses(
                invented_chapter(), 7, expected_verses=73, source_book="neh"
            )

    def test_real_pdf_integration_only_in_dedicated_https_verified_actions(self):
        pdf = os.environ.get("CHES_TEST_NEH7_PDF")
        if not pdf:
            self.skipTest("External original source loaded only in dedicated read-only CI")
        original = Path(pdf).read_bytes()
        report = import_private_pdf(original, "neh", 7, expected_verses=72)
        self.assertEqual(report["source_pdf_page_count"], 6)
        self.assertEqual(report["verses_extracted"], 72)
        self.assertEqual(
            [int(row["reference"].rsplit(".", 1)[1]) for row in report["verses"]],
            list(PRIMARY),
        )
        alternates = [
            row["original_pdf_alternate_verse_number_not_oshb_crosswalk"]
            for row in report["verses"]
            if "original_pdf_alternate_verse_number_not_oshb_crosswalk" in row
        ]
        self.assertEqual(alternates, list(range(68, 73)))
        # Original green PDF glyph fragments must not disappear during parsing.
        import fitz
        with fitz.open(stream=original, filetype="pdf") as doc:
            all_green = sum(
                1
                for i, page in enumerate(doc, 1)
                for span in page_spans(page, i)
                if is_ches_green(span["color"])
            )
        self.assertEqual(report["ches_pdf_green_spans"], all_green)
        self.assertFalse(report["alignment_with_oshb_words_verified"])
        self.assertFalse(report["olt_english_translation_approved"])
        self.assertEqual(report["publication_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
