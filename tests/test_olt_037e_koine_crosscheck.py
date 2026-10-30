"""OLT-037E falsifiable original Koine + LSJ source crosscheck, never approval."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from olt_core.engine import SourceContractError
from olt_core.greek_koine_crosscheck import (
    CHECKPOINT, REPORT_PATH, TARGETS, LSJ_PREVIOUS_SHA256,
    _frozen_lsj_source, _lossy_ascii_key_signature,
    index_abbott_source_entries, inspect_lsj_source_keys, build_source_crosscheck,
    require_exact_checkpoint, serialize_report,
)
from scripts.fetch_olt_037e_abbott import (
    README_LENGTH, SOURCE_LENGTH, SOURCE_LICENSE_SENTENCE,
    read_abbott_manifest, verify_abbott_source, verify_original_readme,
)


class TestOLT037E(unittest.TestCase):
    def test_source_is_pinned_public_domain_with_original_readme(self):
        m=read_abbott_manifest()
        self.assertEqual(m["upstream_pinned_commit"],
                         "8c00cb244761aa23659421a8cbbbf7a3b27b7d59")
        self.assertEqual(m["upstream_source_git_blob_sha1"],
                         "e10dcfa534dbc71168ca6ac273e991348bab2bb2")
        self.assertEqual(m["upstream_source_byte_length"],SOURCE_LENGTH)
        self.assertEqual(m["upstream_readme_git_blob_sha1"],
                         "64eda828221708e54d3b23d2d8a1c17b1e76a1ef")
        self.assertIn("public domain",SOURCE_LICENSE_SENTENCE)
        self.assertEqual(m["source_license_status"],"PUBLIC_DOMAIN_AS_STATED_BY_UPSTREAM_PROJECT")
        self.assertTrue(m["original_source_never_vendored"])
        self.assertFalse(m["approved_greek_lemma_identity"])
        self.assertFalse(m["approved_lexical_sense"])
        self.assertFalse(m["approved_english_master_entry"])
        self.assertEqual(m["publication_status"],"BLOCKED")
        self.assertEqual(REPORT_PATH,
                         "data/quality/olt_037e_abbott_koine_and_lsj_key_diagnostics.json")

    def test_wrong_xml_bytes_or_license_statement_never_pass(self):
        m=read_abbott_manifest()
        for fake in [b"","<TEI><entry n='λέγω|G3004'/></TEI>".encode("utf-8"),
                     b"X"*SOURCE_LENGTH]:
            with self.subTest(size=len(fake)):
                with self.assertRaises(SourceContractError):
                    verify_abbott_source(fake,m)
        with self.assertRaises(SourceContractError):
            verify_original_readme(b"fake public domain")
        with self.assertRaises(SourceContractError):
            verify_original_readme(b"X"*README_LENGTH)

    def test_prior_independent_lsj_source_keys_remain_immutable(self):
        src=_frozen_lsj_source(ROOT)
        self.assertEqual(src["checkpoint"],"OLT-037D")
        self.assertEqual(src["scholarly_decisions_approved"],0)
        self.assertEqual(src["publication_status"],"BLOCKED")
        self.assertEqual(LSJ_PREVIOUS_SHA256,
                         "ea9f6e031897630cd5645ace24797e91e145f2018e5dba236b8951d5f1aa4973")
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json"
            path.parent.mkdir(parents=True)
            path.write_bytes((ROOT/"data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json").read_bytes()+b" ")
            with self.assertRaises(SourceContractError):
                _frozen_lsj_source(Path(directory))

    def test_lsj_ascii_neighborhood_does_not_select_dictionary_lemma(self):
        source=[
           {"source_tei_entry_id":"a","source_tei_entry_key_UNREVIEWED":"o(/ti"},
           {"source_tei_entry_id":"b","source_tei_entry_key_UNREVIEWED":"o(=ti1"},
           {"source_tei_entry_id":"c","source_tei_entry_key_UNREVIEWED":"o(/tion"},
           {"source_tei_entry_id":"d","source_tei_entry_key_UNREVIEWED":"le/gw1"},
        ]
        self.assertEqual(_lossy_ascii_key_signature("o(/ti"),"oti")
        self.assertEqual(_lossy_ascii_key_signature("o(=ti1"),"oti")
        self.assertEqual(_lossy_ascii_key_signature("le/gw2"),"legw")
        observation=inspect_lsj_source_keys(source,"o(/ti")
        self.assertEqual([x["source_tei_entry_id"] for x in
            observation["exact_original_source_key_matches_UNREVIEWED"]],["a"])
        self.assertEqual([x["source_tei_entry_id"] for x in
            observation["lossy_signature_source_key_records_DIAGNOSTIC_ONLY"]],
            ["a","b"])
        self.assertEqual(observation["lossy_ascii_prefix_count_DIAGNOSTIC_ONLY"],3)
        self.assertFalse(observation["lossy_evidence_automatically_resolves_original_exact_miss"])
        self.assertFalse(observation["any_dictionary_lemma_or_sense_approved"])

    def test_full_teixml_source_entry_index_preserves_unapproved_definition_evidence(self):
        entries="".join(f'<entry n="δοκιμή|G9888"><form><orth>δοκιμή</orth></form></entry>'
                        for _ in range(4001))
        source=(
          '<?xml version="1.0" encoding="UTF-8"?>'
          '<TEI xmlns="http://www.crosswire.org/2008/TEIOSIS/namespace">'
          '<teiHeader></teiHeader><text><body>'+entries+
          '<entry n="λέγω|G2036|G3004"><form><orth>λέγω</orth></form>'
          '<sense><def>original say</def><gloss>original speak</gloss></sense></entry>'
          '<entry n="ὅτι|G3754"><form><orth>ὅτι</orth></form>'
          '<sense><def>original conjunction</def></sense></entry>'
          '</body></text></TEI>'
        ).encode("utf-8")
        results=index_abbott_source_entries(source)
        self.assertEqual(results["original_xml_entry_count"],4003)
        self.assertEqual(len(results["case_entries"]["3004"]),1)
        self.assertEqual(len(results["case_entries"]["3754"]),1)
        first=results["case_entries"]["3004"][0]
        self.assertEqual(first["native_abbott_entry_attribute_n_SOURCE_ONLY"],
                         "λέγω|G2036|G3004")
        self.assertEqual(first["all_native_abbott_strong_crossrefs_SOURCE_ONLY"],
                         ["2036","3004"])
        self.assertTrue(first["native_entry_references_multiple_strong_numbers"])
        self.assertEqual(first["first_source_orth_forms_NOT_APPROVED"],["λέγω"])
        self.assertEqual(first["first_source_def_or_gloss_records_NOT_OLT_TRANSLATION"],
                         [{"original_source_tag":"def","original_source_text":"original say"},
                          {"original_source_tag":"gloss","original_source_text":"original speak"}])
        self.assertEqual(first["original_source_def_or_gloss_count"],2)
        self.assertFalse(first["abbott_dictionary_gloss_used_as_translation"])
        self.assertIsNone(first["biblical_contextual_sense_selected"])
        self.assertEqual(first["publication_status"],"BLOCKED")
        with self.assertRaises(SourceContractError):
            index_abbott_source_entries(b"<!DOCTYPE TEI><TEI><entry n='word|G3004'/></TEI>")
        with self.assertRaises(SourceContractError):
            index_abbott_source_entries(b"<TEI><entry n='G3004'/></TEI>")

    def test_generated_source_report_must_match_checkpoint_exactly(self):
        item={"checkpoint":CHECKPOINT,"publication_status":"BLOCKED",
              "human_approved_lexical_senses":0}
        expected=serialize_report(item)
        self.assertEqual(json.loads(expected),item)
        self.assertTrue(expected.endswith("\n"))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/REPORT_PATH
            p.parent.mkdir(parents=True)
            p.write_text(expected,encoding="utf-8")
            require_exact_checkpoint(item,Path(d))
            p.write_text(expected.replace("BLOCKED","APPROVED"),encoding="utf-8")
            with self.assertRaises(SourceContractError):
                require_exact_checkpoint(item,Path(d))
            p.unlink()
            with self.assertRaises(SourceContractError):
                require_exact_checkpoint(item,Path(d))

    def test_locked_complete_original_source_report_is_unapproved_and_exact(self):
        raw=(ROOT/REPORT_PATH).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "f6e0c31f4a7c736df307e55c10d0860ea47edf7aa6dc2c28b61d6b81430ee435")
        evidence=json.loads(raw.decode("utf-8"))
        self.assertEqual(evidence["checkpoint"],CHECKPOINT)
        self.assertEqual(evidence["source_abbott_entries_in_full_original_teixml"],6153)
        self.assertEqual(evidence["source_abbott_entries_with_native_n_attribute"],5896)
        self.assertEqual(evidence["original_greek_word_positions_crosschecked"],[2315,1287])
        self.assertEqual(evidence["machine_approved_lexical_senses"],0)
        self.assertEqual(evidence["human_approved_lexical_senses"],0)
        self.assertEqual(evidence["approved_english_master_entries"],0)
        self.assertEqual(evidence["publication_status"],"BLOCKED")
        greek,conjunction=evidence["source_cases"]
        self.assertEqual(greek["rp2018_original_strong_number"],"3004")
        self.assertEqual(conjunction["rp2018_original_strong_number"],"3754")
        self.assertEqual(len(greek["abbott_smith_original_source_lexical_entries_UNREVIEWED"]),1)
        self.assertEqual(len(conjunction["abbott_smith_original_source_lexical_entries_UNREVIEWED"]),1)
        source=greek["abbott_smith_original_source_lexical_entries_UNREVIEWED"][0]
        self.assertEqual(source["native_abbott_entry_attribute_n_SOURCE_ONLY"],
                         "λέγω|G2036|G2046|G3004|G4483")
        self.assertTrue(source["native_entry_references_multiple_strong_numbers"])
        self.assertEqual(source["all_native_abbott_strong_crossrefs_SOURCE_ONLY"],
                         ["2036","2046","3004","4483"])
        self.assertEqual(source["original_source_def_or_gloss_count"],11)
        self.assertEqual(conjunction["abbott_smith_original_source_lexical_entries_UNREVIEWED"][0]
                         ["original_source_def_or_gloss_count"],3)
        self.assertEqual([r["source_tei_entry_key_UNREVIEWED"] for r in
            conjunction["lsj_original_source_key_diagnostic"]
            ["lossy_signature_source_key_records_DIAGNOSTIC_ONLY"]],["o(/ti^"])
        self.assertEqual(conjunction["lsj_original_source_key_diagnostic"]
                         ["exact_original_source_key_matches_UNREVIEWED"],[])
        self.assertTrue(all(r["selected_lsj_entry_id"] is None
                            and r["selected_abbott_lexical_sense"] is None
                            and r["contextual_greek_lemma_approved"] is None
                            and r["owner_english_master_word"] is None
                            and r["independent_philological_signoff"] is False
                            and r["owner_editorial_approval"] is False
                            and r["publication_status"]=="BLOCKED"
                            for r in evidence["source_cases"]))

    def test_actual_original_koine_and_lsj_external_sources_in_ci(self):
        abbott_path=os.environ.get("OLT037E_ABBOTT_PATH")
        lsj_dir=os.environ.get("OLT037E_LSJ_DIR")
        if not abbott_path or not lsj_dir:
            self.skipTest("Full exact-git-blob independent Koine LSJ integration runs dedicated CI")
        result=build_source_crosscheck(Path(abbott_path),Path(lsj_dir))
        self.assertEqual(result["checkpoint"],CHECKPOINT)
        self.assertEqual(result["publication_status"],"BLOCKED")
        self.assertEqual(result["machine_approved_lexical_senses"],0)
        self.assertEqual(result["human_approved_lexical_senses"],0)
        self.assertEqual(result["independently_signed_greek_lemma_assignments"],0)
        self.assertEqual(result["approved_english_master_entries"],0)
        self.assertEqual(result["published_scripture_verses"],0)
        self.assertEqual(result["original_greek_word_positions_crosschecked"],[2315,1287])
        self.assertGreater(result["source_abbott_entries_in_full_original_teixml"],4000)
        self.assertEqual([x["rp2018_original_strong_number"]
                          for x in result["source_cases"]],list(TARGETS))
        for x in result["source_cases"]:
            self.assertTrue(x["both_lexica_have_interdependencies_NOT_INDEPENDENT_VOTES"])
            self.assertFalse(x["abbott_original_source_lemma_equals_rp2018_verified"])
            self.assertFalse(x["english_source_gloss_equal_to_olt_translation"])
            self.assertIsNone(x["selected_abbott_lexical_sense"])
            self.assertIsNone(x["selected_lsj_entry_id"])
            self.assertIsNone(x["contextual_greek_lemma_approved"])
            self.assertFalse(x["independent_philological_signoff"])
            self.assertFalse(x["owner_editorial_approval"])
            self.assertEqual(x["publication_status"],"BLOCKED")
        target=ROOT/REPORT_PATH
        self.assertTrue(target.is_file(),
                        "The canonical original Koine lexical research artifact must be frozen")
        require_exact_checkpoint(result)


if __name__=="__main__":
    unittest.main()
