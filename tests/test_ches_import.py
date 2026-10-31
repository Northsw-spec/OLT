"""CHES-001: private-only original PDF extractor negative and source-contract tests."""
import json
import tempfile
import unittest
from pathlib import Path

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
