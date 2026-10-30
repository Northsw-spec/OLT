"""OLT-035B: 27 real Greek continuous books and two variant auxiliaries."""
from __future__ import annotations
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from olt_core.engine import SourceContractError
from olt_core.sources import read_greek_3john, git_blob_sha1
from olt_core.nt_corpus import (
    read_nt_inventory, read_nt_book, read_nt_ancillary, verify_nt_corpus
)

class TestOLT035B(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg=read_nt_inventory()

    def test_all_27_real_original_book_files_are_byte_identical(self):
        scan=verify_nt_corpus()
        self.assertEqual(scan["books"],27)
        self.assertEqual(scan["verified_ancillary_files"],2)
        self.assertGreater(scan["greek_verse_rows"],7000)
        self.assertLess(scan["greek_verse_rows"],9000)
        self.assertEqual(scan["publication_status"],"BLOCKED")
        self.assertEqual(scan["source_word_token_ids"],"NOT_IMPORTED")
        self.assertEqual(scan["source_lemma_morphology"],"NOT_IMPORTED")
        self.assertFalse(scan["textual_variants_independently_reviewed"])

    def test_full_nt_source_revision_and_27_canonical_book_order(self):
        reg=self.reg
        self.assertEqual(reg["source_commit"],"27a45ff1b7be6c17ccbfeac414f3f55732ae8e28")
        self.assertEqual(reg["source_tag"],"v3.3.2")
        self.assertEqual(reg["text_edition"],"ROBINSON_PIERPONT_BYZANTINE_TEXTFORM_2018")
        self.assertEqual(len(reg["continuous_books"]),27)
        self.assertEqual(len(reg["ancillary_readings"]),2)
        self.assertEqual(reg["continuous_books"][0]["canonical_book_id"],"Matt")
        self.assertEqual(reg["continuous_books"][-1]["canonical_book_id"],"Rev")
        self.assertEqual(len({b["upstream_book_code"] for b in reg["continuous_books"]}),27)
        self.assertEqual(reg["release_status"],"BLOCKED")

    def test_each_verse_is_real_greek_not_synthetic_tokenization(self):
        for code in ("MAT","JOH","ACT","ROM","REV","3JO"):
            with self.subTest(book=code):
                b=read_nt_book(code)
                self.assertGreater(b["verse_count"],1)
                self.assertTrue(b["verses"][0]["original_greek_text"])
                self.assertIsNone(b["verses"][0]["original_source_token_ids"])
                self.assertIsNone(b["verses"][0]["original_lemma_ids"])
                self.assertIsNone(b["verses"][0]["original_morphology"])
                self.assertIsNone(b["verses"][0]["owner_translation"])
                self.assertEqual(b["word_alignment_status"],"NOT_AVAILABLE_IN_UPSTREAM_VERSE_CSV")
                self.assertEqual(b["publication_status"],"BLOCKED")

    def test_mat_1_1_is_actual_greek_source_not_english_or_guessed(self):
        m=read_nt_book("MAT")
        v=m["verses"][0]
        self.assertEqual(v["reference"],"Matt.1.1")
        self.assertTrue(v["original_greek_text"].startswith("Βίβλος γενέσεως"))
        self.assertIn("Ἰησοῦ",v["original_greek_text"])
        self.assertIsNone(v["original_lemma_ids"])

    def test_old_third_john_sample_is_exactly_same_under_new_full_inventory(self):
        v1=read_greek_3john()["verses"]
        v2=read_nt_book("3JO")["verses"]
        self.assertEqual(len(v1),14)
        self.assertEqual(len(v2),14)
        self.assertEqual([x["original_script_verse_text"] for x in v1],
                         [x["original_greek_text"] for x in v2])
        self.assertEqual(v2[0]["reference"],"3John.1.1")

    def test_separate_pa_and_acts24_are_kept_with_provenance_not_spliced(self):
        reg=self.reg
        self.assertNotIn("PA",[b["upstream_book_code"] for b in reg["continuous_books"]])
        self.assertNotIn("ACT24",[b["upstream_book_code"] for b in reg["continuous_books"]])
        pa=read_nt_ancillary("PA")
        act=read_nt_ancillary("ACT24")
        self.assertTrue(pa["must_not_merge_without_textual_review"])
        self.assertTrue(act["must_not_merge_without_textual_review"])
        self.assertEqual((pa["passage_text_verses"][0]["chapter"],pa["passage_text_verses"][0]["verse"]),(7,53))
        self.assertEqual((act["passage_text_verses"][0]["chapter"],act["passage_text_verses"][0]["verse"]),(24,6))
        self.assertEqual(pa["publication_status"],"BLOCKED")
        self.assertIsNone(act["source_word_identifiers"])

    def test_no_automatic_duplicate_variant_overwrite(self):
        reg=self.reg
        self.assertTrue(reg["textual_variant_policy"]["source_auxiliary_not_main_default"])
        self.assertTrue(reg["textual_variant_policy"]["possible_overlapping_verse_ids_are_not_silent_overwrites"])
        self.assertTrue(reg["textual_variant_policy"]["place_ancillary_text_only_after_independent_textual_review"])

    def test_reject_book_code_path_traversal_and_noncontinuous_extra_file(self):
        for code in ("../MAT","PA","ACT24","NONE",""):
            with self.subTest(code=code):
                with self.assertRaises(SourceContractError):
                    read_nt_book(code)

    def test_reject_unknown_ancillary_code(self):
        with self.assertRaises(SourceContractError):
            read_nt_ancillary("JOH")

    def test_reject_tampering_with_unicode_original_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            dst=root/"data/imported/nt/rp2018/2JO.csv"
            dst.parent.mkdir(parents=True)
            raw=(ROOT/"data/imported/nt/rp2018/2JO.csv").read_bytes()
            dst.write_bytes(raw.replace("Ὁ".encode(),b"NOT_GREEK",1))
            with self.assertRaisesRegex(SourceContractError,"Greek file bytes"):
                read_nt_book("2JO",root,self.reg)

    def test_reject_premature_lexical_morphology_certification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            dest=root/"data/engine/olt_035b_rp2018_verse_inventory.json"
            dest.parent.mkdir(parents=True)
            bad=copy.deepcopy(self.reg)
            bad["full_nt_word_token_ids_verified"]=True
            dest.write_text(json.dumps(bad),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"linguistically reviewed"):
                read_nt_inventory(root)

    def test_reject_missing_or_forged_nt_book_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            dest=root/"data/engine/olt_035b_rp2018_verse_inventory.json"
            dest.parent.mkdir(parents=True)
            bad=copy.deepcopy(self.reg)
            bad["continuous_books"].pop()
            dest.write_text(json.dumps(bad),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"incomplete"):
                read_nt_inventory(root)

    def test_reject_false_variant_as_continuous_book(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            dest=root/"data/engine/olt_035b_rp2018_verse_inventory.json"
            dest.parent.mkdir(parents=True)
            bad=copy.deepcopy(self.reg)
            bad["continuous_books"][0]["upstream_book_code"]="PA"
            bad["continuous_books"][0]["repo_path"]="data/imported/nt/rp2018/PA.csv"
            bad["continuous_books"][0]["upstream_path"]="csv-unicode/ccat/no-variants/PA.csv"
            dest.write_text(json.dumps(bad),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"silently become"):
                read_nt_inventory(root)

    def test_source_file_blob_sha_stays_equal_to_upstream_in_repos(self):
        for code in ("3JO","MAT","REV"):
            with self.subTest(code=code):
                item=next(i for i in self.reg["continuous_books"] if i["upstream_book_code"]==code)
                local=(ROOT/item["repo_path"]).read_bytes()
                self.assertEqual(len(local),item["byte_length"])
                self.assertEqual(git_blob_sha1(local),item["upstream_git_blob_sha1"])

    def test_invalid_greek_lexical_reuse_is_not_marked_published(self):
        self.assertTrue(all(not b["lexical_morphology_available"] for b in self.reg["continuous_books"]))
        self.assertFalse(self.reg["full_nt_lemma_morphology_verified"])
        self.assertFalse(self.reg["locale_translation_generated"])
        self.assertEqual(self.reg["source_text_human_review"],"NOT_DONE")
        self.assertEqual(self.reg["release_status"],"BLOCKED")

if __name__=="__main__":
    unittest.main()
