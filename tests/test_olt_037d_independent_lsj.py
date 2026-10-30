"""OLT-037D tests: independent Perseus LSJ is only evidence, never OLT approval."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from olt_core.engine import SourceContractError
from olt_core.greek_independent_lsj import (
    CHECKPOINT, CONTEXT_SHA256, RESEARCH_QUERIES,
    _entry_key_candidates, _frozen_context_dossiers, build_independent_key_inventory,
    serialize_inventory, source_entry_key_index, verify_checkpoint,
)
from scripts.fetch_olt_037d_lsj import (
    git_blob_sha1, read_lsj_source_manifest, verify_original_lsj,
)


class TestOLT037D(unittest.TestCase):
    def test_exact_original_source_and_licenses_are_locked(self):
        m = read_lsj_source_manifest()
        self.assertEqual(m["checkpoint"], CHECKPOINT)
        self.assertEqual(m["upstream_pinned_commit"],
                         "1c34cdf756c63cf37db61bd366d733431dbd7aa0")
        self.assertEqual(m["source_data_license"], "CC BY-SA 4.0")
        self.assertIn("Perseus Digital Library", m["attribution"])
        self.assertTrue(m["original_source_data_not_vendored"])
        self.assertTrue(m["no_lsj_entry_word_sense_auto_assignment"])
        self.assertFalse(m["publication_status"] != "BLOCKED")
        self.assertEqual([(x["original_byte_length"],x["original_git_blob_sha1"])
                          for x in m["file_specs"]], [
            (6753569,"0cc4c1906a4f8a0e696002dc83728d55b9cd9806"),
            (12280021,"b8a1ba605424c2df3b67f04190bde804664441c8")])

    def test_original_git_blob_sha_and_source_mutation_fail_closed(self):
        data = b'<TEI.2>Perseus<entryFree id="a" key="le/gw"/></TEI.2>'
        spec = {"original_byte_length":len(data),
                "original_git_blob_sha1":git_blob_sha1(data)}
        verify_original_lsj(data,spec)
        for modified in [data+b"X",data.replace(b"Perseus", b"Morpheus"),
                         data.replace(b"le/gw",b"le/gW")]:
            with self.subTest(modified=modified):
                with self.assertRaises(SourceContractError):
                    verify_original_lsj(modified,spec)
        with self.assertRaises(SourceContractError):
            verify_original_lsj(data,dict(spec,original_git_blob_sha1="0"*40))
        with self.assertRaises(SourceContractError):
            verify_original_lsj(bytes([255])*len(data),spec)

    def test_raw_entry_keys_not_fuzzy_matched_or_interpreted(self):
        first = '<TEI.2>Perseus ' + ''.join(
            f'<entryFree id="n{i}" key="key{i}" type="main"/>' for i in range(105)
        ) + '<entryFree id="l1" key="le/gw"/>' + (
            '<entryFree id="l2" key="le/gw1"/><entryFree id="o1" key="o(/ti"/>'
        ) + '</TEI.2>'
        rows=source_entry_key_index(first)
        self.assertEqual(len(rows),108)
        self.assertEqual([x["source_tei_entry_key_UNREVIEWED"]
                          for x in _entry_key_candidates(rows,"le/gw")],
                         ["le/gw","le/gw1"])
        self.assertEqual([x["source_tei_entry_id"]
                          for x in _entry_key_candidates(rows,"o(/ti")],["o1"])
        self.assertEqual(_entry_key_candidates(rows,"LE/GW"),[])
        self.assertEqual(_entry_key_candidates(rows,"le/g"),[])
        self.assertEqual(_entry_key_candidates(rows,"lem"),[])
        self.assertEqual(_entry_key_candidates(rows,"o(ti"),[])
        with self.assertRaises(SourceContractError):
            source_entry_key_index(first.replace('id="l2"', 'id="l1"'))
        with self.assertRaises(SourceContractError):
            source_entry_key_index(first.replace('key="le/gw1"','wrong="le/gw1"'))
        with self.assertRaises(SourceContractError):
            source_entry_key_index('<TEI.2>Perseus</TEI.2>')

    def test_prior_greek_word_dossiers_are_immutable(self):
        old=_frozen_context_dossiers(ROOT)
        self.assertEqual(old["number_of_case_studies"],2)
        self.assertEqual(old["number_of_verified_greek_lemma_decisions"],0)
        self.assertEqual(old["publication_status"],"BLOCKED")
        self.assertEqual(CONTEXT_SHA256,
                         "08d58d6ce13b9803ed1936dfde1ed249f3c32e44af7bdc50b8665adb593bab69")
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            p=d/"data/quality/olt_037c_greek_contextual_research_dossiers.json"
            p.parent.mkdir(parents=True)
            p.write_bytes((ROOT/"data/quality/olt_037c_greek_contextual_research_dossiers.json")
                          .read_bytes()+b" ")
            with self.assertRaises(SourceContractError):
                _frozen_context_dossiers(d)

    def test_proposed_original_keys_never_become_verified_lemma_identities(self):
        self.assertEqual(RESEARCH_QUERIES["3004"]["lsj_source_entry_key_query"],"le/gw")
        self.assertEqual(RESEARCH_QUERIES["3754"]["lsj_source_entry_key_query"],"o(/ti")
        self.assertEqual(RESEARCH_QUERIES["3004"]["unicode_step_source_candidate_headword"],
                         "λέγω")

    def test_immutable_generated_evidence_drift_gate(self):
        result={"checkpoint":CHECKPOINT,
                "english_master_entries_approved":0,
                "publication_status":"BLOCKED"}
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            p=d/"data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json"
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(serialize_inventory(result),encoding="utf-8")
            verify_checkpoint(result,d)
            p.write_text(serialize_inventory(result).replace("BLOCKED","PUBLISHED"),
                         encoding="utf-8")
            with self.assertRaises(SourceContractError):
                verify_checkpoint(result,d)
            p.unlink()
            with self.assertRaises(SourceContractError):
                verify_checkpoint(result,d)

    def test_original_lsj_integration_exact_source_and_no_lexical_approvals(self):
        folder=os.environ.get("OLT037D_LSJ_DIR")
        if not folder:
            self.skipTest("Only dedicated GitHub workflow fetches the pinned external LSJ XML")
        report=build_independent_key_inventory(Path(folder))
        self.assertEqual(report["checkpoint"],CHECKPOINT)
        self.assertEqual(report["source_lsj_commit"],
                         "1c34cdf756c63cf37db61bd366d733431dbd7aa0")
        self.assertEqual(report["license"],"CC BY-SA 4.0")
        self.assertEqual(report["source_shards_verified_with_original_git_blob_sha1"],2)
        self.assertEqual(report["greek_lemma_sense_independent_review"],"NOT_DONE")
        self.assertEqual(report["english_master_entries_approved"],0)
        self.assertEqual(report["scholarly_decisions_approved"],0)
        self.assertEqual(report["publication_status"],"BLOCKED")
        self.assertEqual([x["original_rp2018_strong_number"]
                          for x in report["source_lexicon_candidate_key_research_cases"]],
                         ["3004","3754"])
        for case in report["source_lexicon_candidate_key_research_cases"]:
            self.assertGreater(case["number_of_original_lsj_entryFree_start_tags_indexed"],100)
            self.assertEqual(len(case["stepbible_dstrong_ids_UNREVIEWED"]),2)
            self.assertFalse(case["greek_orthography_equivalence_independently_proven"])
            self.assertFalse(case["dictionary_lemma_identity_approved"])
            self.assertIsNone(case["nt_word_sense_assignment"])
            self.assertIsNone(case["independent_philologist_corroboration"])
            self.assertIsNone(case["owner_translation_approval"])
            self.assertIsNone(case["english_master_entry"])
            self.assertEqual(case["publication_status"],"BLOCKED")
        p=ROOT/"data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json"
        if p.is_file():
            verify_checkpoint(report)


if __name__ == "__main__":
    unittest.main()
