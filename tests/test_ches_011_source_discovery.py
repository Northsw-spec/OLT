"""CHES-011: synthetic 929-link source-index tests; authentic OSHB verse evidence.

No original CHES PDF files, third-party English fragments or editorial
texts are stored in these public fixtures.
"""
from __future__ import annotations
import json
import unittest
from unittest.mock import patch

from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_010_indexed_discovery import (
    CHES010Error, _source_urls_from_index, examine_indexed_sources,
)
from scripts.ches_011_source_discovery import NEW_CHAPTERS

def fake_html() -> bytes:
    groups = [("gen", 50), ("exo", 40)]
    groups += [("p" + chr(97+i//26) + chr(97+i%26), 23 if i < 25 else 22)
               for i in range(37)]
    assert len(groups) == 39 and sum(n for _, n in groups) == 929
    return ("<html>" + "".join(
        f'<a href="/OnlineInterlinear/OTpdf/{prefix}{n}.pdf">link</a>'
        for prefix, count in groups for n in range(1, count + 1)
    ) + "</html>").encode("utf-8")


def synthetic_source(pdf: bytes, book: str, chapter: int, *, approved_targets):
    if not pdf.startswith(b"%PDF-"):
        raise ValueError("Original PDF missing")
    expected = approved_targets[book, chapter]
    original = load_ot_book(book, ROOT, read_provenance(ROOT))
    verses = [v for v in original["verses"]
              if v["reference"].startswith(f"{book}.{chapter}.")]
    if len(verses) != expected:
        raise ValueError("Hebrew verse total differs")
    return {
        "scope": f"{book}.{chapter}",
        "source_pin_status": "DISCOVERY_ONLY_NOT_ENGINE_APPROVED",
        "printed_pdf_verses_confirmed_by_engineering": expected,
        "authentic_oshb_original_word_tokens_observed":
            sum(len(v["words"]) for v in verses),
        "private_green_ches_pdf_spans_extracted": len(verses) * 12,
        "unassigned_original_green_spans": 0,
        "word_and_morpheme_alignment_verified": False,
        "english_translation_owner_approved": False,
        "publication_status": "BLOCKED",
    }


class TestCHES011BoundedOriginalSourceDiscovery(unittest.TestCase):
    def test_source_targets_have_genuine_pinned_oshb_original_verse_inventories(self):
        self.assertEqual(len(NEW_CHAPTERS), 4)
        for book, chapter, prefix, count in NEW_CHAPTERS:
            with self.subTest(book=book, chapter=chapter):
                original = load_ot_book(book, ROOT, read_provenance(ROOT))
                references = [
                    verse["reference"] for verse in original["verses"]
                    if verse["reference"].startswith(f"{book}.{chapter}.")
                ]
                self.assertEqual(
                    references, [f"{book}.{chapter}.{i}" for i in range(1, count + 1)]
                )
                self.assertEqual(prefix, "gen" if book == "Gen" else "exo")

    def test_discovery_new_four_does_not_change_existing_six_or_ten_chapter_scope(self):
        links, index = _source_urls_from_index(fake_html(), targets=NEW_CHAPTERS)
        self.assertEqual(len(links), 4)
        self.assertEqual(index["discovered_chapter_pdf_count"], 929)
        self.assertEqual(index["discovered_original_source_filename_prefix_count"], 39)
        self.assertEqual(
            links["Gen", 7],
            "https://www.scripture4all.org/OnlineInterlinear/OTpdf/gen7.pdf"
        )
        self.assertEqual(
            links["Exod", 6],
            "https://www.scripture4all.org/OnlineInterlinear/OTpdf/exo6.pdf"
        )
        self.assertNotIn(("Gen", 1), links)
        with patch("scripts.ches_010_indexed_discovery.discover_source",
                   side_effect=synthetic_source):
            report = examine_indexed_sources(
                fake_html(), targets=NEW_CHAPTERS,
                fetch_pdf=lambda url: b"%PDF-FAKE-NO-LICENSED-TEXT" + b"x" * 1500
            )
        self.assertEqual(report["checkpoint"], "CHES-011-SOURCE-INDEX-DISCOVERY")
        self.assertEqual(report["selected_new_original_chapter_PDFs"], 4)
        self.assertEqual(report["total_printed_original_verse_markers"], 99)
        self.assertEqual(
            {r["scope"] for r in report["selected_source_metadata"]},
            {"Gen.7", "Gen.8", "Exod.5", "Exod.6"}
        )
        self.assertTrue(report["all_original_source_greens_assigned_to_verses"])
        self.assertFalse(report["english_translation_owner_approved"])
        self.assertFalse(report["word_and_morpheme_alignment_verified"])
        self.assertEqual(report["source_pin_status"],
                         "DISCOVERY_ONLY_NOT_ENGINE_APPROVED")
        self.assertNotIn("FAKE-NO-LICENSED-TEXT", json.dumps(report))

    def test_reject_duplicate_unknown_or_out_of_bounds_targets(self):
        for invalid in (
            NEW_CHAPTERS + (NEW_CHAPTERS[0],),
            (("Gen", 7, "exo", 24),),
            (("Gen", True, "gen", 24),),
            (("Lev", 1, "lev", 17),),
            (("Exod", 6, "exo", 0),),
            (),
            NEW_CHAPTERS * 3,
        ):
            with self.subTest(invalid=str(invalid)[:120]), self.assertRaises(CHES010Error):
                _source_urls_from_index(fake_html(), targets=invalid)

    def test_reject_bad_pdf_and_false_claims_of_alignment_or_english_approval(self):
        with self.assertRaises(CHES010Error):
            examine_indexed_sources(fake_html(), targets=NEW_CHAPTERS,
                                    fetch_pdf=lambda _: b"<html>NOT_PDF</html>")
        for field, value in (
            ("word_and_morpheme_alignment_verified", True),
            ("english_translation_owner_approved", True),
            ("unassigned_original_green_spans", 1),
        ):
            def fake_invalid(pdf, book, chapter, *, approved_targets):
                item = synthetic_source(pdf, book, chapter,
                                        approved_targets=approved_targets)
                item[field] = value
                return item
            with self.subTest(field=field), patch(
                "scripts.ches_010_indexed_discovery.discover_source",
                side_effect=fake_invalid
            ), self.assertRaises(CHES010Error):
                examine_indexed_sources(fake_html(), targets=NEW_CHAPTERS,
                                        fetch_pdf=lambda _: b"%PDF-" + b"x" * 2000)


if __name__ == "__main__":
    unittest.main()
