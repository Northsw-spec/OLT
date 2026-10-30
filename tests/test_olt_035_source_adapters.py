"""OLT-035: real-source hashes, Aramaic selection, NT Greek byte identity."""
from __future__ import annotations
import copy
import csv
from io import StringIO
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from olt_core.sources import (
    SOURCE_ADAPTER_VERSION, SourceContractError, git_blob_sha1,
    read_provenance, load_ot_book, normalize_ot_verse, verify_ot_corpus,
    read_greek_3john, exact_source_lemma_components, ot_morph_language,
)

class TestOLT035(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=read_provenance()
        cls.old_genesis=json.loads(
            (ROOT/"data/research/genesis_01_verse_01_alignment_proposal.json").read_text(encoding="utf-8")
        )

    def test_39_immutable_books_and_both_ot_languages_counted(self):
        result=verify_ot_corpus()
        self.assertEqual((result["books"],result["verses"],result["word_tokens"]),
                         (39,23213,306785))
        self.assertEqual((result["tagged_hebrew"],result["tagged_aramaic"]),(301837,4948))
        self.assertEqual(result["independent_morphology_review"],"NOT_DONE")
        self.assertEqual(result["publication_status"],"BLOCKED")
        self.assertIn("NOT_RECOMPUTED",result["upstream_xml_sha256_status"])

    def test_all_source_manifest_hashes_are_independent_anchors(self):
        reg=self.registry
        self.assertEqual(SOURCE_ADAPTER_VERSION,"0.1.0")
        self.assertEqual(len(reg["ot"]["books"]),39)
        self.assertEqual(reg["ot"]["upstream_commit"],
                         "3d15126fb1ef74867fc1434be1942e837932691f")
        self.assertEqual(reg["nt"]["upstream_commit"],
                         "27a45ff1b7be6c17ccbfeac414f3f55732ae8e28")
        for spec in reg["ot"]["books"]:
            self.assertEqual(len(spec["book_json_git_blob_sha1"]),40)
            self.assertEqual(len(spec["upstream_osis_xml_sha256"]),64)
            self.assertGreater(spec["book_json_bytes"],0)
        self.assertEqual(reg["ot"]["license"]["oshb_morphology"],"CC_BY_4_0")
        self.assertEqual(reg["nt"]["license"],"PUBLIC_DOMAIN_SOURCE_AND_CODE_AS_STATED_IN_UPSTREAM_LICENSE")

    def test_real_genesis1_original_words_match_existing_proposal(self):
        source=normalize_ot_verse("Gen","Gen.1.1")
        proposal=self.old_genesis["source_alignment"]
        self.assertEqual(source["source_word_count"],7)
        self.assertEqual([s["token_id"] for s in source["tokens"]],
                         [p["source_token_id"] for p in proposal])
        self.assertEqual([s["original_script"] for s in source["tokens"]],
                         [p["pointed_hebrew"] for p in proposal])
        self.assertEqual([s["raw_morphology"] for s in source["tokens"]],
                         [p["source_morphology"] for p in proposal])
        self.assertEqual([s["raw_lemma"] for s in source["tokens"]],
                         [p["source_raw_lemma"] for p in proposal])
        self.assertEqual(source["tokens"][1]["lemma_id"],"1254 a")
        self.assertEqual(source["tokens"][2]["lemma_id"],"430")
        self.assertEqual(source["tokens"][2]["source_language"],"hbo")
        self.assertIsNone(source["translated_text"])
        self.assertEqual(source["publication_status"],"BLOCKED")

    def test_real_aramaic_source_occurrences_preserve_source_language(self):
        source=normalize_ot_verse("Dan","Dan.2.5")
        self.assertGreater(source["source_language_counts"].get("arc",0),0)
        tokens=[x for x in source["tokens"] if x["source_language"]=="arc"]
        self.assertTrue(all(x["raw_morphology"].startswith("A") for x in tokens))
        self.assertTrue(all(x["publication_status"]=="BLOCKED" for x in tokens))

    def test_original_source_component_extensions_not_silently_merged(self):
        self.assertEqual(exact_source_lemma_components("c/b/1254 a"),["1254 a"])
        self.assertEqual(exact_source_lemma_components("c/b/1254 b"),["1254 b"])
        self.assertNotEqual(exact_source_lemma_components("1254 a"),
                            exact_source_lemma_components("1254 b"))
        self.assertEqual(exact_source_lemma_components("c/1008+"),["1008+"])
        self.assertEqual(exact_source_lemma_components("c/b"),[])
        self.assertEqual(exact_source_lemma_components("1/2"),["1","2"])

    def test_source_morphology_language_not_guessed_by_book_or_spellings(self):
        self.assertEqual(ot_morph_language("HVqp3ms"),"hbo")
        self.assertEqual(ot_morph_language("AVqp3ms"),"arc")
        self.assertEqual(ot_morph_language("AC/Vqw3ms"),"arc")
        with self.assertRaisesRegex(SourceContractError,"language tag"):
            ot_morph_language("Vqp3ms")

    def test_exact_greek_file_matches_upstream_blob_and_14_verses(self):
        nt=read_greek_3john()
        self.assertEqual(nt["upstream_commit"],
                         "27a45ff1b7be6c17ccbfeac414f3f55732ae8e28")
        self.assertEqual((nt["source_book"],nt["verse_count"]),("3John",14))
        self.assertEqual(nt["word_tokenization"],"NOT_DONE")
        self.assertEqual(nt["greek_morphology_status"],"NOT_IMPORTED")
        self.assertEqual(nt["publication_status"],"BLOCKED")
        self.assertEqual(nt["verses"][0]["verse_id"],"3John.1.1")
        self.assertTrue(nt["verses"][0]["original_script_verse_text"].startswith("Ὁ πρεσβύτερος"))
        self.assertIn("Γαΐῳ",nt["verses"][0]["original_script_verse_text"])
        self.assertEqual(nt["verses"][-1]["verse_id"],"3John.1.14")
        for v in nt["verses"]:
            self.assertIsNone(v["word_token_ids"])
            self.assertIsNone(v["lemma_ids"])
            self.assertIsNone(v["raw_morphology"])
            self.assertIsNone(v["translation"])
        raw=(ROOT/"data/imported/nt/rp2018/3JO.csv").read_bytes()
        self.assertEqual(git_blob_sha1(raw),self.registry["nt"]["sample_derived_unicode_csv_upstream_git_blob_sha1"])

    def test_3john_csv_verses_are_preserved_exact_without_normalization(self):
        nt=read_greek_3john()
        with (ROOT/"data/imported/nt/rp2018/3JO.csv").open("r",encoding="utf-8",newline="") as stream:
            rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),14)
        self.assertEqual([r["text"] for r in rows],
                         [v["original_script_verse_text"] for v in nt["verses"]])

    def test_reject_source_registry_falsely_complete_greek(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p=root/"data/engine/olt_035_source_provenance.json"
            p.parent.mkdir(parents=True)
            j=copy.deepcopy(self.registry)
            j["nt"]["full_nt_token_identifiers_imported"]=True
            p.write_text(json.dumps(j),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"not completely imported"):
                read_provenance(root)

    def test_reject_mismatch_of_imported_book_byte_checksum(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            dst=root/"data/imported/books/Obad.json"
            dst.parent.mkdir(parents=True)
            dst.write_bytes((ROOT/"data/imported/books/Obad.json").read_bytes()+b"\n")
            with self.assertRaisesRegex(SourceContractError,"Git blob digest"):
                load_ot_book("Obad",root,self.registry)

    def test_reject_single_word_tampering_even_valid_json(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            dst=root/"data/imported/books/Obad.json"
            dst.parent.mkdir(parents=True)
            data=load_ot_book("Obad")
            data["verses"][0]["words"][0]["hebrew"]="FICTIONAL_ORIGINAL"
            dst.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
            with self.assertRaisesRegex(SourceContractError,"Git blob digest"):
                load_ot_book("Obad",root,self.registry)

    def test_reject_source_path_traversal_and_unpinned_book(self):
        for book in ("../Gen","Gen/../Exod","DoesNotExist",""):
            with self.subTest(book=book):
                with self.assertRaises(SourceContractError):
                    load_ot_book(book,ROOT,self.registry)

    def test_reject_changing_greek_text_byte_or_verse(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            dst=root/"data/imported/nt/rp2018/3JO.csv"
            dst.parent.mkdir(parents=True)
            raw=(ROOT/"data/imported/nt/rp2018/3JO.csv").read_bytes()
            dst.write_bytes(raw.replace("Γαΐῳ".encode(),b"BAD",1))
            with self.assertRaisesRegex(SourceContractError,"not byte-identical"):
                read_greek_3john(root,self.registry)

    def test_reject_greek_original_without_original_14_verses(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            dst=root/"data/imported/nt/rp2018/3JO.csv"
            dst.parent.mkdir(parents=True)
            txt=(ROOT/"data/imported/nt/rp2018/3JO.csv").read_text(encoding="utf-8")
            dst.write_text("\n".join(txt.splitlines()[:-1])+"\n",encoding="utf-8")
            # strict source hash blocks shortened file BEFORE any verse parsing can misrepresent coverage.
            with self.assertRaisesRegex(SourceContractError,"not byte-identical"):
                read_greek_3john(root,self.registry)

    def test_reject_greek_claims_of_independent_morphology(self):
        self.assertFalse(self.registry["nt"]["independent_greek_morphology_imported"])
        self.assertFalse(self.registry["nt"]["full_nt_text_import_complete"])
        self.assertFalse(self.registry["nt"]["greek_lemma_alignment_complete"])
        self.assertEqual(self.registry["nt"]["greek_source_word_ids_status"],
                         "NOT_AVAILABLE_IN_THIS_CSV; NO_TOKEN_ID_FABRICATION")

    def test_normalized_greek_source_is_verse_level_not_fabricated_word_level(self):
        sample=read_greek_3john()
        self.assertTrue(all("original_script_verse_text" in v for v in sample["verses"]))
        self.assertTrue(all(v["word_token_ids"] is None for v in sample["verses"]))
        self.assertTrue(all(v["lemma_ids"] is None for v in sample["verses"]))

if __name__=="__main__":
    unittest.main()
