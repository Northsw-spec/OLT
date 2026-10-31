"""CHES-010: six-to-ten authentic-source batch checkpoint compatibility.

The original English strings are synthetic from the established CHES-009
test helper. No licensed CHES English or original source PDFs are published.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_008_private_batch import (
    BATCH,EXTENDED_BATCH,INDEXED_BATCH,CHESBatchError,STATE_FILE,
    run_private_chapter_batch,
)
from test_ches_009_six_source_batch import fake_pdf, fake_generator


class TestCHES010IndexedResumablePrivateBatch(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pdf_dir=Path(self.temp.name)
        self.output=self.pdf_dir/".olt-private"/"english"

    def run_fake(self,*,extended=False,indexed=False,limit=None):
        opts={"extended":extended,"indexed":indexed}
        if limit is not None:
            opts["limit"]=limit
        with patch("scripts.ches_008_private_batch._verified_pdf",
                   side_effect=fake_pdf),patch(
            "scripts.ches_008_private_batch._generate",
            side_effect=fake_generator):
            return run_private_chapter_batch(self.pdf_dir,self.output,**opts)

    def test_prior_six_are_skipped_new_four_built_then_all_ten_skipped(self):
        first=self.run_fake(extended=True)
        self.assertEqual((first["built"],first["skipped"],first["failed"]),(6,0,0))
        self.assertTrue(first["complete"])
        state=json.loads((self.output/STATE_FILE).read_text(encoding="utf-8"))
        prior=dict(state["chapters"])
        second=self.run_fake(indexed=True)
        self.assertEqual((second["built"],second["skipped"],second["failed"]),(4,6,0))
        self.assertTrue(second["complete"])
        self.assertEqual(second["total_supported_pinned_chapters"],10)
        self.assertEqual(second["completed_chapters_stored_private"],10)
        third=self.run_fake(indexed=True)
        self.assertEqual((third["built"],third["skipped"],third["failed"]),(0,10,0))
        self.assertTrue(third["complete"])
        backward=self.run_fake(extended=True)
        self.assertEqual((backward["built"],backward["skipped"]),(0,6))
        self.assertEqual(backward["total_supported_pinned_chapters"],6)
        original_mode=self.run_fake()
        self.assertEqual((original_mode["built"],original_mode["skipped"]),(0,4))
        self.assertTrue(original_mode["complete"])
        latest=json.loads((self.output/STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(len(latest["chapters"]),10)
        for key,record in prior.items():
            self.assertEqual(latest["chapters"][key],record)
        self.assertEqual(third["publication_status"],"BLOCKED")
        self.assertFalse(third["english_translation_owner_approved"])
        self.assertNotIn("INVENTED-PRIVATE-ENGLISH",json.dumps(second))

    def test_ten_source_last_source_failure_is_retryable(self):
        self.run_fake(extended=True)
        def missing(folder,filename,pin):
            if filename=="ches-ex4.pdf":
                raise CHESBatchError("MISSING_OR_UNSAFE_SOURCE_PDF")
            return fake_pdf(folder,filename,pin)
        with patch("scripts.ches_008_private_batch._verified_pdf",
                   side_effect=missing),patch(
            "scripts.ches_008_private_batch._generate",
            side_effect=fake_generator):
            failed=run_private_chapter_batch(
                self.pdf_dir,self.output,indexed=True
            )
        self.assertEqual((failed["built"],failed["skipped"],failed["failed"]),(3,6,1))
        self.assertFalse(failed["complete"])
        self.assertEqual(failed["failed_chapter_codes"],[
            {"scope":"Exod.4","code":"MISSING_OR_UNSAFE_SOURCE_PDF"}
        ])
        retried=self.run_fake(indexed=True)
        self.assertEqual((retried["built"],retried["skipped"],retried["failed"]),(1,9,0))
        self.assertTrue(retried["complete"])

    def test_only_explicit_indexed_scope_allows_more_than_six(self):
        self.assertEqual(len(BATCH),4)
        self.assertEqual(len(EXTENDED_BATCH),6)
        self.assertEqual(len(INDEXED_BATCH),10)
        self.assertEqual(INDEXED_BATCH[:6],EXTENDED_BATCH)
        for values in (
            {"limit":10},
            {"limit":10,"extended":True},
            {"limit":11,"indexed":True},
            {"extended":True,"indexed":True},
            {"indexed":"truthy"},
        ):
            with self.subTest(values=values),self.assertRaises(CHESBatchError):
                run_private_chapter_batch(self.pdf_dir,self.output,**values)


if __name__=="__main__":
    unittest.main()
