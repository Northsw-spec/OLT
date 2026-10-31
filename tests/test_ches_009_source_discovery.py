"""CHES-009: synthetic invalid input, authentic source inventory checks."""
from pathlib import Path
import unittest

from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_009_source_discovery import (
    CHES009SourceError, DISCOVERY, discover_source,
)


class TestCHES009OriginalSourceDiscovery(unittest.TestCase):
    def test_only_two_original_chapters_with_real_verse_inventories(self):
        for (book, chapter), count in DISCOVERY.items():
            with self.subTest(book=book, chapter=chapter):
                source = load_ot_book(book, ROOT, read_provenance(ROOT))
                references = [v["reference"] for v in source["verses"]
                              if v["reference"].startswith(f"{book}.{chapter}.")]
                self.assertEqual(references,
                                 [f"{book}.{chapter}.{i}" for i in range(1, count + 1)])

    def test_guessed_chapter_identity_and_nonpdf_are_rejected(self):
        for book, chapter in (("Gen", 5), ("Exod", 1), ("Gen", 1), ("Matt", 4)):
            with self.subTest(book=book, chapter=chapter), self.assertRaises(CHES009SourceError):
                discover_source(b"%PDF-fake", book, chapter)
        for book, chapter in DISCOVERY:
            with self.subTest(book=book, chapter=chapter), self.assertRaises(ValueError):
                discover_source(b"<html>NOT-ORIGINAL-PDF</html>", book, chapter)

    def test_no_private_chapter_text_or_false_approval_in_module_defaults(self):
        self.assertEqual(DISCOVERY, {("Gen", 4): 26, ("Exod", 2): 25})


if __name__ == "__main__":
    unittest.main()
