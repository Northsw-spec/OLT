"""CHES-010: fake original-PDF cache, immutable pin registry and ten-source resume.

No original licensed CHES text/PDF appears in synthetic tests. Authentic
Hebrew original token inventories and technical SHA pins come from OLT.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from olt_core.sources import ROOT
from scripts.ches_010_pin_registry import (
    CHES010PinError, INDEXED_BATCH_ITEMS, read_indexed_source_pins,
)
from scripts.ches_010_private_source_cache import (
    CHES010CacheError,cache_indexed_originals,
)
from scripts.ches_008_private_batch import (
    BATCH,EXTENDED_BATCH,INDEXED_BATCH,run_private_chapter_batch,
)

def fake_pinned_pdf(book: str, chapter: int) -> bytes:
    return (f"%PDF-FAKE-ORIGINAL-{book}-{chapter}-".encode() + b"\x00"*2000)


class TestCHES010IndexedPrivateCacheAndBatch(unittest.TestCase):
    def test_registry_is_exact_and_preserves_legacy_defaults(self):
        records=read_indexed_source_pins()
        self.assertEqual(len(records),4)
        self.assertEqual(len(BATCH),4)
        self.assertEqual(len(EXTENDED_BATCH),6)
        self.assertEqual(len(INDEXED_BATCH),10)
        self.assertEqual(INDEXED_BATCH[:6],EXTENDED_BATCH)
        self.assertEqual(INDEXED_BATCH[6:],INDEXED_BATCH_ITEMS)
        self.assertEqual(
            [(x["original_book"],x["original_chapter"]) for x in records],
            [("Gen",5),("Gen",6),("Exod",3),("Exod",4)]
        )
        self.assertEqual(sum(x["printed_pdf_verses_confirmed_by_engineering"] for x in records),107)
        self.assertEqual(sum(x["oshb_original_word_tokens_observed"] for x in records),1520)
        self.assertEqual(sum(x["green_ches_pdf_spans_extracted"] for x in records),1862)
        self.assertTrue(all(x["full_source_text_in_public_git_permitted"] is False for x in records))

    def test_mutated_registry_rights_and_hash_rejected(self):
        data=json.loads(
            (ROOT/"data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8")
        )
        for key,value in [
            ("word_and_morpheme_alignment_verified",True),
            ("full_source_text_in_public_git_permitted",True),
            ("source_pdf_sha256","NO-HASH"),
            ("original_chapter",True),
            ("original_pdf_url","https://fake.example/gen5.pdf"),
        ]:
            with self.subTest(field=key),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                path=root/"data/engine/olt_ches_source_manifest.json"
                path.parent.mkdir(parents=True)
                temp=copy.deepcopy(data)
                temp["indexed_original_source_pins"][0][key]=value
                path.write_text(json.dumps(temp),encoding="utf-8")
                with self.assertRaises(CHES010PinError):
                    read_indexed_source_pins(root)

    def test_all_four_source_pdfs_cached_privately_and_rerun_skips(self):
        records=read_indexed_source_pins()
        blob_lookup={}
        urls={}
        overrides={}
        for record in records:
            book,chapter=record["original_book"],record["original_chapter"]
            blob=fake_pinned_pdf(book,chapter)
            url=record["original_pdf_url"]
            urls[book,chapter]=url
            blob_lookup[url]=blob
            pin={**record,"source_pdf_bytes":len(blob),
                 "source_pdf_sha256":hashlib.sha256(blob).hexdigest()}
            overrides[book,chapter]=pin
        def fake_reader(_root):
            return list(overrides.values())
        def fake_pin(book,chapter,_root):
            return overrides[book,chapter]
        def fake_inspect(blob,book,chapter,*,root,approved_targets):
            pin=overrides[book,chapter]
            return {
                "scope":f"{book}.{chapter}",
                "source_pin_status":"DISCOVERY_ONLY_NOT_ENGINE_APPROVED",
                "original_pdf_sha256":pin["source_pdf_sha256"],
                "original_pdf_byte_length":pin["source_pdf_bytes"],
                "original_pdf_page_count":pin["source_pdf_pages"],
                "printed_pdf_verses_confirmed_by_engineering":
                    pin["printed_pdf_verses_confirmed_by_engineering"],
                "authentic_oshb_original_word_tokens_observed":
                    pin["oshb_original_word_tokens_observed"],
                "private_green_ches_pdf_spans_extracted":
                    pin["green_ches_pdf_spans_extracted"],
                "unassigned_original_green_spans":0,
                "verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS":
                    pin["verses_with_different_pdf_span_and_oshb_word_counts_NOT_TRANSLATION_ERRORS"],
                "verses_with_green_fragments_on_multiple_pdf_pages":
                    pin["verses_with_green_fragments_on_multiple_pdf_pages"],
                "min_green_spans_in_one_verse":pin["min_green_spans_in_one_verse"],
                "max_green_spans_in_one_verse":pin["max_green_spans_in_one_verse"],
                "word_and_morpheme_alignment_verified":False,
                "english_translation_owner_approved":False,
                "publication_status":"BLOCKED",
            }
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/".olt-private"/"pdfs"
            with patch("scripts.ches_010_private_source_cache._source_urls_from_index",
                       return_value=(urls,{"source_index_html_sha256":"e"*64})),patch(
                "scripts.ches_010_private_source_cache.read_indexed_source_pins",
                side_effect=fake_reader
            ),patch(
                "scripts.ches_010_private_source_cache.pinned_record",
                side_effect=fake_pin
            ),patch(
                "scripts.ches_010_private_source_cache.discover_source",
                side_effect=fake_inspect
            ):
                one=cache_indexed_originals(b"FAKE-INDEX",out,fetch_pdf=blob_lookup.__getitem__)
                self.assertEqual(one["new_private_source_files_created"],4)
                self.assertEqual(one["exact_private_source_files_skipped"],0)
                self.assertEqual(one["checked_original_source_pdfs"],4)
                two=cache_indexed_originals(b"FAKE-INDEX",out,fetch_pdf=blob_lookup.__getitem__)
                self.assertEqual(two["new_private_source_files_created"],0)
                self.assertEqual(two["exact_private_source_files_skipped"],4)
                self.assertNotIn("FAKE-ORIGINAL",json.dumps(two))
                for record in records:
                    path=out/record["private_pdf_filename"]
                    self.assertEqual(path.stat().st_mode & 0o777,0o600)
                first=out/records[0]["private_pdf_filename"]
                first.write_bytes(b"%PDF-CHANGED-PRIVATE-FILE")
                with self.assertRaises(CHES010CacheError):
                    cache_indexed_originals(b"FAKE-INDEX",out,fetch_pdf=blob_lookup.__getitem__)
                self.assertEqual(first.read_bytes(),b"%PDF-CHANGED-PRIVATE-FILE")
                # Original SHA identity is checked before any write.
                changed_data={**blob_lookup,urls[("Gen",6)]:b"%PDF-WRONG-SHA"}
                with self.assertRaises(CHES010CacheError):
                    cache_indexed_originals(b"FAKE-INDEX",out,fetch_pdf=changed_data.__getitem__)

    def test_public_output_path_does_not_receive_original_pdf(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                cache_indexed_originals(b"fake",Path(t)/"public")

if __name__ == "__main__":
    unittest.main()
