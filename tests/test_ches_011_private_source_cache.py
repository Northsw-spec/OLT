"""CHES-011: private cached PDF group, no original licensed source text in tests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_010_pin_registry import read_next_source_pins
from scripts.ches_010_private_source_cache import (
    cache_indexed_originals, CHES010CacheError,
)
from scripts.ches_011_source_discovery import NEW_CHAPTERS


class TestCHES011SecondPrivatePinnedSourceCache(unittest.TestCase):
    def test_new_source_group_is_private_reusable_and_never_overwrites_changed_files(self):
        originals = read_next_source_pins()
        overrides = {}
        urls = {}
        blobs = {}
        for p in originals:
            book, chapter = p["original_book"], p["original_chapter"]
            body = (f"%PDF-SYNTHETIC-CHES011-{book}-{chapter}-".encode("ascii")
                    + b"x" * 2000)
            checked = {
                **p,
                "source_pdf_bytes": len(body),
                "source_pdf_sha256": hashlib.sha256(body).hexdigest(),
            }
            overrides[book, chapter] = checked
            urls[book, chapter] = p["original_pdf_url"]
            blobs[p["original_pdf_url"]] = body

        def synthetic_audit(pdf, book, chapter, *, root, approved_targets):
            assert approved_targets[book, chapter] == overrides[
                book, chapter
            ]["printed_pdf_verses_confirmed_by_engineering"]
            pin = overrides[book, chapter]
            return {
                "scope": f"{book}.{chapter}",
                "source_pin_status": "DISCOVERY_ONLY_NOT_ENGINE_APPROVED",
                "original_pdf_sha256": pin["source_pdf_sha256"],
                "original_pdf_byte_length": pin["source_pdf_bytes"],
                "original_pdf_page_count": pin["source_pdf_pages"],
                "printed_pdf_verses_confirmed_by_engineering":
                    pin["printed_pdf_verses_confirmed_by_engineering"],
                "authentic_oshb_original_word_tokens_observed":
                    pin["oshb_original_word_tokens_observed"],
                "private_green_ches_pdf_spans_extracted":
                    pin["green_ches_pdf_spans_extracted"],
                "unassigned_original_green_spans": 0,
                "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS":
                    pin["verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"],
                "verses_with_green_fragments_on_multiple_pdf_pages":
                    pin["verses_with_green_fragments_on_multiple_pdf_pages"],
                "min_green_spans_in_one_verse": pin["min_green_spans_in_one_verse"],
                "max_green_spans_in_one_verse": pin["max_green_spans_in_one_verse"],
                "word_and_morpheme_alignment_verified": False,
                "english_translation_owner_approved": False,
                "publication_status": "BLOCKED",
            }

        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / ".olt-private" / "source-pdfs"
            with patch(
                "scripts.ches_010_private_source_cache._source_urls_from_index",
                return_value=(urls, {"source_index_html_sha256": "b" * 64})
            ), patch(
                "scripts.ches_010_private_source_cache.read_next_source_pins",
                return_value=list(overrides.values())
            ), patch(
                "scripts.ches_010_private_source_cache.pinned_record",
                side_effect=lambda book, ch, root: overrides[book, ch]
            ), patch(
                "scripts.ches_010_private_source_cache.discover_source",
                side_effect=synthetic_audit
            ):
                a = cache_indexed_originals(b"SYNTHETIC", out,
                                            fetch_pdf=blobs.__getitem__, next_group=True)
                self.assertEqual(a["checkpoint"], "CHES-011-PINNED-PRIVATE-SOURCE-CACHE")
                self.assertEqual((a["new_private_source_files_created"],
                                  a["exact_private_source_files_skipped"]), (4, 0))
                b = cache_indexed_originals(b"SYNTHETIC", out,
                                            fetch_pdf=blobs.__getitem__, next_group=True)
                self.assertEqual((b["new_private_source_files_created"],
                                  b["exact_private_source_files_skipped"]), (0, 4))
                self.assertNotIn("SYNTHETIC-CHES011", json.dumps(b))
                for pin in originals:
                    file = out / pin["private_pdf_filename"]
                    self.assertEqual(file.stat().st_mode & 0o777, 0o600)
                altered = out / originals[0]["private_pdf_filename"]
                altered.write_bytes(b"%PDF-EDITED-ORIGINAL")
                with self.assertRaises(CHES010CacheError):
                    cache_indexed_originals(b"SYNTHETIC", out,
                                            fetch_pdf=blobs.__getitem__, next_group=True)
                self.assertEqual(altered.read_bytes(), b"%PDF-EDITED-ORIGINAL")
                wrong = dict(blobs)
                wrong[originals[1]["original_pdf_url"]] = b"%PDF-TAMPERED"
                with self.assertRaises(CHES010CacheError):
                    cache_indexed_originals(b"SYNTHETIC", out,
                                            fetch_pdf=wrong.__getitem__, next_group=True)

    def test_group_flag_must_be_boolean_before_network_or_directory_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            private = Path(temp) / ".olt-private" / "source"
            with self.assertRaises(CHES010CacheError):
                cache_indexed_originals(b"FAKE", private, next_group="yes")
            self.assertFalse(private.exists())


if __name__ == "__main__":
    unittest.main()
