"""OLT-035D source-first Greek morphology and lexical-reference regression gates."""
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
from olt_core.greek_words import (
    read_word_manifest, read_parsed_greek_book, verify_greek_words, _parse_one_verse
)
from olt_core.nt_corpus import read_nt_book
from olt_core.sources import git_blob_sha1


class TestOLT035D(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=read_word_manifest()

    def test_full_official_morphology_source_27_books_and_actual_numbers(self):
        audit=verify_greek_words()
        self.assertEqual(audit["official_source_books"],27)
        self.assertEqual(audit["official_beta_strongs_verses"],7957)
        self.assertEqual(audit["matching_unicode_verse_rows"],7953)
        self.assertEqual(audit["original_bp5_empty_verse_slots"],4)
        self.assertTrue(audit["source_only_positions_are_empty_placeholders_not_additional_greek_text"])
        self.assertEqual(audit["editor_source_word_form_records"],140149)
        self.assertEqual(audit["unique_position_locators"],140149)
        self.assertEqual(audit["extra_alternative_parse_pairs_attached_to_words"],28)
        self.assertEqual(audit["publication_status"],"BLOCKED")
        self.assertEqual(audit["upstream_commit"],
                         "27a45ff1b7be6c17ccbfeac414f3f55732ae8e28")

    def test_27_official_editor_files_are_pinned_not_derived_unicode_only(self):
        registry=self.registry
        self.assertEqual(registry["source_file_kind"],
                         "OFFICIAL_EDITOR_BP5_BETA_CODE_UNACCENTED_WITH_STRONG_NUMBER_AND_RAW_MORPHOLOGY")
        self.assertEqual(len(registry["files"]),27)
        self.assertEqual(registry["license"],"PUBLIC_DOMAIN")
        self.assertFalse(registry["external_source_native_word_ids_provided"])
        self.assertFalse(registry["word_lemma_forms_and_senses_certified"])
        self.assertTrue(registry["morphology_alternatives_preserved"])
        for f in registry["files"]:
            with self.subTest(file=f["repo_path"]):
                raw=(ROOT/f["repo_path"]).read_bytes()
                self.assertEqual(len(raw),f["byte_length"])
                self.assertEqual(git_blob_sha1(raw),f["official_git_blob_sha1"])

    def test_source_book_matthew_one_one_actual_original_beta_strong_morph(self):
        book=read_parsed_greek_book("MAT")
        one=book["verse_records"][0]
        self.assertEqual(one["reference"],"Matt.1.1")
        self.assertEqual(one["source_word_count"],8)
        self.assertEqual(one["words"][0]["beta_code_word_form"],"biblos")
        self.assertEqual(one["words"][0]["official_editor_strong_number"],"976")
        self.assertEqual(one["words"][0]["official_editor_morphology_code"],"N-NSF")
        self.assertEqual(one["words"][0]["derived_source_locator"],
                         "rp2018-v3.3.2:Matt.1.1:w0001")
        self.assertIsNone(one["words"][0]["accented_unicode_word_form"])
        self.assertIsNone(one["words"][0]["original_source_native_word_id"])
        self.assertFalse(one["words"][0]["strong_number_is_verified_dictionary_lemma"])
        self.assertEqual(one["words"][0]["publication_status"],"BLOCKED")

    def test_actual_3john_source_14_verses_and_editors_strongs(self):
        book=read_parsed_greek_book("3JO")
        self.assertEqual(book["verse_count"],14)
        self.assertEqual(book["primary_word_forms"],217)
        self.assertEqual(book["additional_alternative_parse_pairs"],0)
        first=book["verse_records"][0]["words"]
        self.assertEqual((first[0]["beta_code_word_form"],first[0]["official_editor_strong_number"],
                          first[0]["official_editor_morphology_code"]),
                         ("o","3588","T-NSM"))
        self.assertEqual(first[1]["beta_code_word_form"],"presbuteros")

    def test_ambiguous_matthew_26_45_morphology_remains_on_same_words(self):
        b=read_parsed_greek_book("MAT")
        v=next(x for x in b["verse_records"] if x["reference"]=="Matt.26.45")
        sleep=next(w for w in v["words"] if w["beta_code_word_form"]=="kaqeudete")
        rest=next(w for w in v["words"] if w["beta_code_word_form"]=="anapauesqe")
        self.assertEqual(sleep["official_editor_morphology_code"],"V-PAI-2P")
        self.assertEqual(sleep["additional_editor_analyses"],
                         [{"strong_number":"2518","morphology_code":"V-PAM-2P",
                           "source_status":"OFFICIAL_EDITOR_ALTERNATE_UNREVIEWED"}])
        self.assertEqual(rest["official_editor_morphology_code"],"V-PMI-2P")
        self.assertEqual(rest["additional_editor_analyses"][0]["morphology_code"],"V-PMM-2P")
        self.assertEqual(v["additional_alternative_parse_pairs"],2)
        self.assertEqual(v["source_word_count"],len(v["words"]))

    def test_revelation_3_17_preserves_alternative_genitive_gender(self):
        v=next(x for x in read_parsed_greek_book("REV")["verse_records"]
               if x["reference"]=="Rev.3.17")
        word=next(x for x in v["words"] if x["beta_code_word_form"]=="oudenos")
        self.assertEqual(word["official_editor_morphology_code"],"A-GSN-N")
        self.assertEqual(word["additional_editor_analyses"][0]["morphology_code"],"A-GSM-N")

    def test_four_extra_original_bp5_verses_are_reported_not_silently_dropped(self):
        ex=["Luke.17.36","Acts.8.37","Acts.15.34","Acts.24.7"]
        report=verify_greek_words()
        self.assertEqual(report["official_bp5_only_verse_refs_require_textual_review"],sorted(ex))
        for code,ref in [("LUK","Luke.17.36"),("ACT","Acts.8.37"),
                         ("ACT","Acts.15.34"),("ACT","Acts.24.7")]:
            src=read_parsed_greek_book(code)
            u=read_nt_book(code)
            self.assertIn(ref,{v["reference"] for v in src["verse_records"]})
            self.assertNotIn(ref,{v["reference"] for v in u["verses"]})
            source_empty=next(v for v in src["verse_records"] if v["reference"]==ref)
            self.assertEqual(source_empty["words"],[])
            self.assertEqual(source_empty["source_word_count"],0)
            self.assertEqual(source_empty["source_slot_kind"],"EMPTY_EDITOR_VERSE_PLACEHOLDER")
            self.assertFalse(source_empty["contains_greek_word_forms"])

    def test_verse_reference_join_not_automatic_unicode_word_surface_alignment(self):
        word=read_parsed_greek_book("MAT")["verse_records"][0]["words"][0]
        self.assertEqual(word["unicode_word_form_alignment"],"NOT_PERFORMED")
        self.assertIsNone(word["accented_unicode_word_form"])
        self.assertTrue(self.registry["only_verse_reference_join_to_unicode_allowed"])
        self.assertTrue(self.registry["no_unreviewed_word_level_strong_to_unicode_alignment"])

    def test_generated_word_position_id_not_a_publisher_word_id(self):
        word=read_parsed_greek_book("3JO")["verse_records"][0]["words"][0]
        self.assertIn("OLT_POSITION",word["derived_locator_origin"])
        self.assertIsNone(word["original_source_native_word_id"])
        self.assertFalse(self.registry["external_source_native_word_ids_provided"])
        self.assertFalse(self.registry["word_lemma_forms_and_senses_certified"])

    def test_parse_alternative_pair_without_inventing_extra_surface(self):
        v=_parse_one_verse("01.01 logos 3056 {N-NSM} 3056 {N-VSM} kai 2532 {CONJ}",
                           "John","source/Strongs/04_JOH.BP5","f"*40)
        self.assertEqual(v["source_word_count"],2)
        self.assertEqual(v["additional_alternative_parse_pairs"],1)
        self.assertEqual(v["words"][0]["additional_editor_analyses"][0]["morphology_code"],"N-VSM")


    def test_known_empty_slot_is_not_allowed_to_acquire_fake_greek_words(self):
        blank=_parse_one_verse("17.36 ","Luke","source/Strongs/03_LUK.BP5","f"*40)
        self.assertEqual(blank["words"],[])
        self.assertFalse(blank["contains_greek_word_forms"])
        with self.assertRaisesRegex(SourceContractError,"unexpectedly contains"):
            _parse_one_verse("17.36 logos 3056 {N-NSM}",
                             "Luke","source/Strongs/03_LUK.BP5","f"*40)

    def test_reject_unattached_alternate_morphology(self):
        with self.assertRaisesRegex(SourceContractError,"Unattached"):
            _parse_one_verse("01.01 3056 {N-NSM}","John","source", "f"*40)

    def test_reject_incomplete_or_malformed_editor_word_triple(self):
        for source in ("01.01 logos 3056","01.01 logos ABC {N-NSM}",
                       "01.01 logos 3056 {bad tag}","01.01"):
            with self.subTest(source=source):
                with self.assertRaises(SourceContractError):
                    _parse_one_verse(source,"John","source","f"*40)

    def test_reject_duplicate_or_unknown_official_book(self):
        for code in ("PA","ACT24","NOT","../MAT",""):
            with self.subTest(code=code):
                with self.assertRaises(SourceContractError):
                    read_parsed_greek_book(code)

    def test_reject_tampered_official_greek_bp5_source_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            f=next(x for x in self.registry["files"] if x["upstream_book_code"]=="3JO")
            dest=root/f["repo_path"]
            dest.parent.mkdir(parents=True)
            raw=(ROOT/f["repo_path"]).read_bytes()
            dest.write_bytes(raw.replace(b"presbuteros",b"DIFFERENT__",1))
            with self.assertRaisesRegex(SourceContractError,"editor's Git blob"):
                read_parsed_greek_book("3JO",root,self.registry)

    def test_reject_falsely_approved_native_word_id_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            dest=root/"data/engine/olt_035d_greek_word_source_manifest.json"
            dest.parent.mkdir(parents=True)
            fake=copy.deepcopy(self.registry)
            fake["external_source_native_word_ids_provided"]=True
            dest.write_text(json.dumps(fake),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"philological safety"):
                read_word_manifest(root)

    def test_reject_changes_to_critical_four_verse_exceptions(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            dest=root/"data/engine/olt_035d_greek_word_source_manifest.json"
            dest.parent.mkdir(parents=True)
            fake=copy.deepcopy(self.registry)
            fake["known_bp5_verses_absent_from_main_unicode_csv"]=[]
            dest.write_text(json.dumps(fake),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"Four source witness differences"):
                read_word_manifest(root)

    def test_reject_forged_morphology_or_lexical_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            dest=root/"data/engine/olt_035d_greek_word_source_manifest.json"
            dest.parent.mkdir(parents=True)
            fake=copy.deepcopy(self.registry)
            fake["word_lemma_forms_and_senses_certified"]=True
            dest.write_text(json.dumps(fake),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"philological safety"):
                read_word_manifest(root)

if __name__=="__main__":
    unittest.main()
