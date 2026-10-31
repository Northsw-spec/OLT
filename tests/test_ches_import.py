"""CHES-001: private-only original PDF extractor negative and source-contract tests."""
import json
import tempfile
import unittest
from pathlib import Path

from unittest.mock import patch
from scripts.ches_private_batch import private_batch, fetch_exact_source, validate_inventory
from scripts.ches_index import parse_index, INDEX
from scripts.ches_import import (
    is_ches_green, explicit_verse_markers, assign_ches_to_explicit_verses,
    write_private_json, import_private_pdf
)


def item(text, page, x, y, color):
    return {"text": text, "page": page, "x": x, "y": y, "color": color}


BLACK = 0x000000
GRAY = 0x888888
GREEN = 0x008000
SOURCE_TEST = [
    item("1", 1, 45, 50, GRAY),
    item(":1", 1, 49, 50, GRAY),
    item("in·beginning", 1, 90, 69, GREEN),
    item("he-created", 1, 110, 69, GREEN),
    item("In the beginning God created", 1, 700, 50, BLACK),
    item("1", 1, 45, 140, GRAY),
    item(":2", 1, 49, 140, GRAY),
    item("she-became", 1, 90, 159, GREEN),
    item("chaos", 1, 120, 159, GREEN),
    item("And the earth was without form", 1, 700, 140, BLACK),
]


class TestCHESPrivateImport(unittest.TestCase):
    def test_only_green_pdf_ink_is_ches(self):
        self.assertTrue(is_ches_green(GREEN))
        self.assertTrue(is_ches_green(0x009900))
        self.assertFalse(is_ches_green(BLACK))
        self.assertFalse(is_ches_green(0xFFFFFF))
        self.assertFalse(is_ches_green(0x880000))
        self.assertFalse(is_ches_green(0x0055CC))
        self.assertFalse(is_ches_green("green"))

    def test_explicit_original_pdf_markers_only(self):
        marks=explicit_verse_markers(SOURCE_TEST, 1)
        self.assertEqual([x["verse"] for x in marks],[1,2])
        self.assertEqual(explicit_verse_markers(SOURCE_TEST, 2),[])

    def test_green_source_spans_exclude_kjv_translation(self):
        rows=assign_ches_to_explicit_verses(SOURCE_TEST,1,2)
        self.assertEqual([x["verse"] for x in rows],[1,2])
        self.assertEqual([[s["original_ches_line_text"] for s in x["ches_spans"]]
                          for x in rows],
                         [["in·beginning","he-created"],["she-became","chaos"]])
        self.assertFalse(any("In the beginning God" in s["original_ches_line_text"]
                             for v in rows for s in v["ches_spans"]))

    def test_missing_duplicate_reordered_or_wrong_verse_markers_are_rejected(self):
        with self.assertRaises(ValueError):
            assign_ches_to_explicit_verses(SOURCE_TEST, 2)
        with self.assertRaises(ValueError):
            assign_ches_to_explicit_verses(SOURCE_TEST, 1, 31)
        with self.assertRaises(ValueError):
            assign_ches_to_explicit_verses(SOURCE_TEST+[item("1:2",1,60,180,GRAY)],1)
        with self.assertRaises(ValueError):
            assign_ches_to_explicit_verses([s for s in SOURCE_TEST if s["text"]!=":1"],1)
        with self.assertRaises(ValueError):
            assign_ches_to_explicit_verses([s for s in SOURCE_TEST if s["text"]!="she-became"
                                           and s["text"]!="chaos"],1)

    def test_no_chapter_english_approval_or_license_inference(self):
        with self.assertRaises(ValueError):
            import_private_pdf(b"not a PDF","Gen",1)
        with self.assertRaises(ValueError):
            import_private_pdf(b"%PDF-"+b" " * 1500,"../../gen",1)
        with self.assertRaises(ValueError):
            import_private_pdf(b"%PDF-"+b" " * 1500,"Gen",0)

    def test_private_output_cannot_be_written_to_normal_repo_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            dummy={"source":"CHES", "english_olt_translation_approved":False}
            with self.assertRaises(ValueError):
                write_private_json(dummy, root/"data/quality/ches.json")
            allowed=root/".olt-private"/"ches"/"Gen.1.json"
            write_private_json(dummy, allowed)
            self.assertTrue(allowed.is_file())
            self.assertEqual(json.loads(allowed.read_text(encoding="utf8")),dummy)

    def test_original_pdf_index_discovery_is_safe_and_in_order(self):
        index=(
            '<html><body>'
            '<a href="OTpdf/gen1.pdf">Chapter 1</a>'
            '<a href="OTpdf/gen2.pdf">Chapter 2</a>'
            '<a href="OTpdf/ex1.pdf">Chapter 1</a>'
            '</body></html>'
        ).encode("utf8")
        result=parse_index(index)
        self.assertEqual(result["source_index_url"],INDEX)
        self.assertEqual(result["discovered_chapter_pdf_count"],3)
        self.assertEqual(result["discovered_original_source_filename_prefix_count"],2)
        self.assertEqual([c["source_book_filename_prefix_NOT_OLT_BOOK_ID"] for c in
                         result["chapter_links"]],["gen","gen","ex"])
        self.assertEqual([c["source_chapter_filename_number"] for c in
                         result["chapter_links"]],[1,2,1])
        self.assertEqual(result["downloaded_chapter_pdf_count"],0)
        self.assertFalse(result["ches_text_extracted_from_this_index"])
        self.assertFalse(result["rights_for_public_CHES_data_export_confirmed"])
        self.assertEqual(result["publication_status"],"BLOCKED")

    def test_duplicate_index_navigation_link_is_safely_deduplicated(self):
        source=b'<a href="OTpdf/gen1.pdf">1</a><a href="OTpdf/gen1.pdf">another menu</a>'
        found=parse_index(source)
        self.assertEqual(found["discovered_chapter_pdf_count"],1)
        self.assertEqual(found["duplicate_index_pdf_link_occurrences_deduplicated"],1)

    def test_external_unordered_untrusted_pdf_index_urls_rejected(self):
        for html in (
            b'<a href="OTpdf/gen2.pdf">2</a>',
            b'<a href="https://evil.test/OnlineInterlinear/OTpdf/gen1.pdf">evil</a>',
            b'<a href="../OTpdf/gen1.pdf">path traversal</a>',
            b'<a href="OTpdf/gen1.pdf?token=bad">query</a>',
        ):
            with self.subTest(html=html):
                with self.assertRaises(ValueError):
                    parse_index(html)

    def test_private_batch_rejects_untrusted_origins_and_uncertain_inventory(self):
        for url in (
            "https://evil.example/OnlineInterlinear/OTpdf/gen1.pdf",
            "https://www.scripture4all.org/OnlineInterlinear/../secret.pdf",
            "http://www.scripture4all.org/OnlineInterlinear/OTpdf/gen1.pdf",
        ):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    fetch_exact_source(url,5000)
        with self.assertRaises(ValueError):
            validate_inventory(b'<a href="OTpdf/gen1.pdf">1</a>')

    def test_private_batch_is_sequential_resumable_and_still_unapproved(self):
        index=parse_index(b'<a href="OTpdf/gen1.pdf">1</a>')
        def fake_source(pdf,book,chapter):
            self.assertEqual((pdf,book,chapter),(b"mock-only","gen",1))
            return {"source_book_identifier_is_not_verified_oshb_book_mapping":True,
                    "original_source_pdf_sha256":"a"*64,
                    "verses":[{"reference":"gen.1.1"}],
                    "verses_extracted":1,
                    "ches_pdf_green_spans":2,
                    "full_source_text_in_public_git_permitted":False,
                    "publication_status":"BLOCKED"}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/".olt-private"/"ches"
            calls=[]
            def source(url,max_bytes):
                calls.append((url,max_bytes))
                return b"mock-only"
            with patch("scripts.ches_private_batch.import_private_pdf",fake_source):
                first=private_batch(index,root,limit=1,fetch=source)
            self.assertEqual(first["newly_imported_to_private_storage"],1)
            self.assertEqual(first["existing_private_chapters_validated_for_resume_only"],0)
            self.assertFalse(first["amharic_translation_authorized"])
            self.assertFalse(first["whole_old_testament_chapter_coverage_qa_complete"])
            self.assertEqual(first["publication_status"],"BLOCKED")
            self.assertEqual(len(calls),1)
            self.assertTrue((root/"gen.1.json").is_file())
            resumed=private_batch(index,root,limit=1,fetch=source)
            self.assertEqual(resumed["newly_imported_to_private_storage"],0)
            self.assertEqual(resumed["existing_private_chapters_validated_for_resume_only"],1)
            self.assertEqual(len(calls),1)
            with self.assertRaises(ValueError):
                private_batch(index,Path(folder)/"public",limit=1,fetch=source)
            with self.assertRaises(ValueError):
                private_batch(index,root,limit=1,delay_seconds=0.01,fetch=source)

    def test_actual_chapter_original_pdf_integration_only_when_explicit(self):
        import os
        file=os.environ.get("CHES_TEST_PDF")
        if not file:
            self.skipTest("Public foundation has no original CHES PDF; external source test runs in dedicated CI")
        real=import_private_pdf(Path(file).read_bytes(),"Gen",1,expected_verses=31)
        self.assertEqual(real["book"],"Gen")
        self.assertEqual(real["chapter"],1)
        self.assertEqual(real["verses_extracted"],31)
        manifest=json.loads((Path(__file__).resolve().parents[1]/
            "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8"))
        spec=manifest["source_reference"]
        self.assertEqual(real["original_source_pdf_sha256"],spec["source_pdf_sha256"])
        self.assertEqual(real["source_pdf_byte_length"],spec["source_pdf_bytes"])
        self.assertEqual(real["source_pdf_page_count"],spec["source_pdf_pages"])
        self.assertEqual(real["ches_pdf_green_spans"],spec["green_ches_pdf_spans_extracted"])
        self.assertEqual(real["verses_extracted"],spec["printed_pdf_verses_confirmed_by_engineering"])
        self.assertFalse(manifest["public_redistribution_rights_confirmed"])
        self.assertFalse(manifest["downstream_amharic_derivative_rights_confirmed"])
        self.assertEqual(manifest["current_active_translation_target"],"en")
        self.assertFalse(real["full_source_text_in_public_git_permitted"])
        self.assertFalse(real["alignment_with_oshb_words_verified"])
        self.assertFalse(real["olt_english_translation_approved"])
        self.assertEqual(real["publication_status"],"BLOCKED")
        self.assertEqual(len({v["reference"] for v in real["verses"]}),31)
        self.assertGreater(real["ches_pdf_green_spans"],100)
        self.assertTrue(all(v["source_ches_spans_NOT_OLT_TRANSLATION"] for v in real["verses"]))


if __name__=="__main__":
    unittest.main()
