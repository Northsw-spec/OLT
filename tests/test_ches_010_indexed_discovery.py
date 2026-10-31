"""CHES-010: safe synthetic source index; no original provider text or PDFs."""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
from unittest.mock import patch
import unittest

from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_010_indexed_discovery import (
    TARGETS, TARGET_MAP, CHES010Error, _source_urls_from_index,
    _download_original_pdf, examine_indexed_sources,
)

def synthetic_index(*, missing: tuple[str,int] | None = None) -> bytes:
    groups = [("gen",50),("exo",40)]
    for i in range(37):
        prefix = "p"+chr(97+i//26)+chr(97+i%26)
        groups.append((prefix,23 if i < 25 else 22))
    assert sum(count for _,count in groups) == 929
    links = [
        '<a href="/OnlineInterlinear/OTpdf/{}{}.pdf">a</a>'.format(prefix,num)
        for prefix,count in groups
        for num in range(1,count+1)
        if missing != (prefix,num)
    ]
    return ("<html><body>"+"".join(links)+"</body></html>").encode("utf-8")


def fake_source(pdf: bytes, book: str, chapter: int, *, approved_targets):
    assert pdf.startswith(b"%PDF-")
    assert approved_targets == TARGET_MAP
    original = load_ot_book(book, ROOT, read_provenance(ROOT))
    verses = [v for v in original["verses"]
              if v["reference"].startswith(f"{book}.{chapter}.")]
    assert len(verses) == approved_targets[(book,chapter)]
    return {
        "checkpoint": "CHES-009-SOURCE-DISCOVERY",
        "scope": f"{book}.{chapter}",
        "original_pdf_sha256": "a"*64,
        "original_pdf_byte_length": len(pdf),
        "original_pdf_page_count": 4,
        "printed_pdf_verses_confirmed_by_engineering": len(verses),
        "authentic_oshb_original_word_tokens_observed": sum(len(v["words"]) for v in verses),
        "private_green_ches_pdf_spans_extracted": 12*len(verses),
        "unassigned_original_green_spans": 0,
        "source_pin_status": "DISCOVERY_ONLY_NOT_ENGINE_APPROVED",
        "word_and_morpheme_alignment_verified": False,
        "english_translation_owner_approved": False,
        "publication_status": "BLOCKED",
    }


def fake_fetch(_url: str) -> bytes:
    return b"%PDF-" + b"\x00" * 1300


class TestCHES010IndexDrivenDiscovery(unittest.TestCase):
    def test_synthetic_929_chapter_index_yields_only_four_exact_source_links(self):
        urls, index = _source_urls_from_index(synthetic_index())
        self.assertEqual(len(urls), 4)
        self.assertEqual(index["discovered_chapter_pdf_count"], 929)
        self.assertEqual(index["discovered_original_source_filename_prefix_count"],39)
        self.assertEqual(urls["Gen",5],
                         "https://www.scripture4all.org/OnlineInterlinear/OTpdf/gen5.pdf")
        self.assertEqual(urls["Exod",4],
                         "https://www.scripture4all.org/OnlineInterlinear/OTpdf/exo4.pdf")

    def test_fake_original_pdf_sources_return_numeric_only_and_no_word_mappings(self):
        index = synthetic_index()
        with patch("scripts.ches_010_indexed_discovery.discover_source",
                   side_effect=fake_source):
            report = examine_indexed_sources(index, fetch_pdf=fake_fetch)
        self.assertEqual(report["selected_new_original_chapter_PDFs"],4)
        self.assertEqual(report["total_printed_original_verse_markers"],107)
        self.assertTrue(report["all_original_source_greens_assigned_to_verses"])
        self.assertEqual(report["source_pin_status"],"DISCOVERY_ONLY_NOT_ENGINE_APPROVED")
        self.assertEqual(len(report["selected_source_metadata"]),4)
        self.assertFalse(report["english_translation_owner_approved"])
        self.assertFalse(report["word_and_morpheme_alignment_verified"])
        self.assertEqual(report["publication_status"],"BLOCKED")
        self.assertEqual({x["scope"] for x in report["selected_source_metadata"]},
                         {"Gen.5","Gen.6","Exod.3","Exod.4"})
        encoded = json.dumps(report)
        self.assertNotIn("FAKE-COPYRIGHTED-TEXT", encoded)
        self.assertNotIn("original_ches_line_text", encoded)

    def test_missing_source_url_unknown_external_link_and_incomplete_index_fail(self):
        with self.assertRaises(CHES010Error):
            _source_urls_from_index(synthetic_index(missing=("gen",5)))
        with self.assertRaises(CHES010Error):
            _source_urls_from_index(b"<html><a href='/OnlineInterlinear/OTpdf/gen5.pdf'>one</a></html>")
        untrusted = synthetic_index().replace(
            b'/OnlineInterlinear/OTpdf/gen5.pdf',
            b'https://untrusted.example/OnlineInterlinear/OTpdf/gen5.pdf'
        )
        with self.assertRaises(ValueError):
            _source_urls_from_index(untrusted)

    def test_invalid_original_pdf_and_unverified_approval_are_rejected(self):
        with self.assertRaises(CHES010Error):
            examine_indexed_sources(synthetic_index(),fetch_pdf=lambda _: b"<html>ERROR</html>")
        def unsafe(pdf,book,chapter,*,approved_targets):
            result=fake_source(pdf,book,chapter,approved_targets=approved_targets)
            result["word_and_morpheme_alignment_verified"]=True
            return result
        with patch("scripts.ches_010_indexed_discovery.discover_source",
                   side_effect=unsafe),self.assertRaises(CHES010Error):
            examine_indexed_sources(synthetic_index(),fetch_pdf=fake_fetch)

    def test_network_downloader_rejects_untrusted_source_or_redirect_without_tls_downgrade(self):
        for url in (
            "http://www.scripture4all.org/OnlineInterlinear/OTpdf/gen5.pdf",
            "https://evil.example/OnlineInterlinear/OTpdf/gen5.pdf",
            "https://www.scripture4all.org:444/OnlineInterlinear/OTpdf/gen5.pdf",
            "https://www.scripture4all.org/Other/gen5.pdf",
        ):
            with self.subTest(url=url),self.assertRaises(CHES010Error):
                _download_original_pdf(url)
        class FakeResponse:
            def __init__(self, final):
                self.final=final
            def geturl(self): return self.final
            def read(self, length): return b"%PDF-"+b"a"*1500
            def __enter__(self): return self
            def __exit__(self,*args): return False
        real="https://www.scripture4all.org/OnlineInterlinear/OTpdf/gen5.pdf"
        with patch("scripts.ches_010_indexed_discovery.urlopen",
                   return_value=FakeResponse("https://another.example/gen5.pdf")),self.assertRaises(CHES010Error):
            _download_original_pdf(real)
        with patch("scripts.ches_010_indexed_discovery.urlopen",
                   return_value=FakeResponse(real)):
            self.assertTrue(_download_original_pdf(real).startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
