"""OLT-037F: source-grounded lexical comparison, fail closed on false approvals."""
from __future__ import annotations

import base64
from copy import deepcopy
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from olt_core.engine import SourceContractError
from olt_core.greek_lexical_comparison import (
    CHECKPOINT, REPORT_PATH, TARGETS, NATIVE_LSJ_ENTRIES,
    CONTEXT_SHA256, CROSSCHECK_SHA256, _verified_json,
    extract_pinned_lsj_entries, _source_passage_example, pick_source_examples,
    build_comparison_dossiers, serialize_research, verify_frozen_source_dossiers,
    emit_initial_checkpoint,
)


class TestOLT037F(unittest.TestCase):
    def test_pinned_source_licenses_and_exact_original_lsj_keys(self):
        self.assertEqual(CHECKPOINT,"OLT-037F")
        self.assertEqual(TARGETS,("3004","3754"))
        self.assertEqual(NATIVE_LSJ_ENTRIES["3004"],
                         (("n62204","le/gw1"),("n62205","le/gw2")))
        self.assertEqual(NATIVE_LSJ_ENTRIES["3754"],(("n75695","o(/ti^"),))
        self.assertEqual(CONTEXT_SHA256,
                         "08d58d6ce13b9803ed1936dfde1ed249f3c32e44af7bdc50b8665adb593bab69")
        self.assertEqual(CROSSCHECK_SHA256,
                         "f6e0c31f4a7c736df307e55c10d0860ea47edf7aa6dc2c28b61d6b81430ee435")

    def test_actual_original_source_checkpoints_cannot_change_silently(self):
        c=_verified_json(ROOT,"data/quality/olt_037c_greek_contextual_research_dossiers.json",
                         CONTEXT_SHA256,"OLT-037C")
        e=_verified_json(ROOT,"data/quality/olt_037e_abbott_koine_and_lsj_key_diagnostics.json",
                         CROSSCHECK_SHA256,"OLT-037E")
        self.assertEqual(c["number_of_case_studies"],2)
        self.assertEqual(e["human_approved_lexical_senses"],0)
        self.assertEqual(c["publication_status"],"BLOCKED")
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"data/test.json"
            p.parent.mkdir(parents=True)
            p.write_bytes((ROOT/"data/quality/olt_037e_abbott_koine_and_lsj_key_diagnostics.json")
                         .read_bytes()+b" ")
            with self.assertRaises(SourceContractError):
                _verified_json(Path(directory),"data/test.json",
                               CROSSCHECK_SHA256,"OLT-037E")

    def test_extract_original_lsj_entry_boundaries_not_unreviewed_senses(self):
        original=(
            '<TEI.2><entryFree id="n62204" key="le/gw1">'
            '<sense n="I"><tr>say</tr><bibl>citation</bibl></sense>'
            '<sense n="II"><tr>to mean</tr><ref>other</ref></sense></entryFree>'
            '<entryFree id="n62205" key="le/gw2">'
            '<sense n="1"><tr>collect</tr></sense></entryFree></TEI.2>'
        ).encode("utf-8")
        rows=extract_pinned_lsj_entries(original,NATIVE_LSJ_ENTRIES["3004"])
        self.assertEqual([x["source_original_lsj_tei_entry_id"] for x in rows],
                         ["n62204","n62205"])
        self.assertEqual([x["source_original_lsj_tei_entry_key"] for x in rows],
                         ["le/gw1","le/gw2"])
        self.assertEqual(rows[0]["source_sense_opening_tag_count"],2)
        self.assertEqual(rows[0]["source_sense_n_labels_FIRST_12_NOT_SEMANTIC_APPROVAL"],
                         ["I","II"])
        self.assertEqual(rows[0]["source_original_bibl_tag_count"],1)
        self.assertEqual(rows[0]["source_original_ref_tag_count"],1)
        self.assertEqual(rows[0]["first_short_lsj_source_tr_excerpt_CC_BY_SA_NOT_OLT"],["say"])
        self.assertIsNone(rows[0]["selected_contextual_sense"])
        self.assertEqual(rows[0]["publication_status"],"BLOCKED")
        with self.assertRaises(SourceContractError):
            extract_pinned_lsj_entries(original, (("n62204","wrong"),))
        with self.assertRaises(SourceContractError):
            extract_pinned_lsj_entries(original, (("n62206","missing"),))
        with self.assertRaises(SourceContractError):
            extract_pinned_lsj_entries(original.replace(b"</entryFree>",b"",1),
                                      NATIVE_LSJ_ENTRIES["3004"])

    def test_duplicate_lsj_source_ids_cannot_be_silently_accepted(self):
        xml=(
            '<TEI.2><entryFree id="n62204" key="le/gw1">a</entryFree>'
            '<entryFree id="n62204" key="le/gw1">b</entryFree></TEI.2>'
        ).encode()
        with self.assertRaises(SourceContractError):
            extract_pinned_lsj_entries(xml,(("n62204","le/gw1"),))

    def test_actual_greek_word_span_must_match_original_verse(self):
        c=_verified_json(ROOT,"data/quality/olt_037c_greek_contextual_research_dossiers.json",
                         CONTEXT_SHA256,"OLT-037C")
        example=c["cases"][0]["sampled_original_greek_contexts_NO_SENSE_ASSIGNED"][0]
        output=_source_passage_example(example)
        self.assertTrue(output["original_greek_verse_UNALTERED"])
        self.assertTrue(output["exact_original_greek_word_UNALTERED"])
        self.assertTrue(output["olt_derived_greek_word_locator_NOT_NATIVE_ID"])
        self.assertIsNone(output["selected_original_source_lexical_sense"])
        self.assertIsNone(output["owner_english_lexical_equivalent"])
        self.assertEqual(output["publication_status"],"BLOCKED")
        for amended in [
            dict(example,original_unicode_verse_NOT_ENGLISH_TRANSLATION="fake Greek source"),
            dict(example,selected_stepbible_sense="unreviewed decision"),
            dict(example,selected_english_translation="fabricated"),
            dict(example,publication_status="PUBLISHED"),
        ]:
            with self.subTest(edited=amended):
                with self.assertRaises(SourceContractError):
                    _source_passage_example(amended)

    def test_deterministic_actual_contexts_without_sense_selection(self):
        c=_verified_json(ROOT,"data/quality/olt_037c_greek_contextual_research_dossiers.json",
                         CONTEXT_SHA256,"OLT-037C")
        for case in c["cases"]:
            samples=case["sampled_original_greek_contexts_NO_SENSE_ASSIGNED"]
            selected=pick_source_examples(samples)
            self.assertEqual(len(selected),5)
            self.assertEqual([x["olt_derived_greek_word_locator_NOT_NATIVE_ID"] for x in selected],
                             [x["olt_derived_greek_word_locator_NOT_NATIVE_ID"]
                              for x in pick_source_examples(samples)])
            self.assertEqual(len({x["olt_derived_greek_word_locator_NOT_NATIVE_ID"]
                                  for x in selected}),5)
            self.assertTrue(all(x["selected_independent_lexicon_entry"] is None
                                and x["selected_original_source_lexical_sense"] is None
                                and x["source_context_hypothesis_reviewed"] is False
                                and x["publication_status"]=="BLOCKED" for x in selected))
        with self.assertRaises(SourceContractError):
            pick_source_examples([])

    def test_source_json_canonical_and_exact_checkpoint_required(self):
        d={"checkpoint":CHECKPOINT,"human_philological_approvals":0,"publication_status":"BLOCKED"}
        expected=serialize_research(d)
        self.assertEqual(json.loads(expected),d)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/REPORT_PATH
            p.parent.mkdir(parents=True)
            p.write_text(expected,encoding="utf-8")
            verify_frozen_source_dossiers(d,Path(directory))
            p.write_text(expected.replace("BLOCKED","PUBLISHED"),encoding="utf-8")
            with self.assertRaises(SourceContractError):
                verify_frozen_source_dossiers(d,Path(directory))
            p.unlink()
            with self.assertRaises(SourceContractError):
                verify_frozen_source_dossiers(d,Path(directory))

    def test_original_checkpoint_chunks_are_lossless_and_content_addressable(self):
        evidence={"checkpoint":CHECKPOINT,"greek":"ὅτι","sense":None}
        output=StringIO()
        with redirect_stdout(output):
            emit_initial_checkpoint(evidence)
        lines=output.getvalue().splitlines()
        self.assertEqual(lines[0],"OLT037F_CHECKPOINT_BEGIN")
        self.assertTrue(lines[-1].startswith("OLT037F_CHECKPOINT_END "))
        payload=base64.b64decode("".join(
            line.removeprefix("OLT037F_CHECKPOINT_PART ") for line in lines[1:-1]),validate=True)
        self.assertEqual(payload,serialize_research(evidence).encode("utf-8"))
        self.assertEqual(hashlib.sha256(payload).hexdigest(),lines[-1].split()[-1])

    def test_frozen_original_greek_and_lsj_source_report_is_exact_and_unapproved(self):
        path=ROOT/REPORT_PATH
        raw=path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "0dca8643adb191e437c7801d7e363450ed07ffbe31138d3bf0090460ca0eba2c")
        obj=json.loads(raw.decode("utf-8"))
        self.assertEqual(obj["checkpoint"],CHECKPOINT)
        self.assertEqual(obj["number_of_comparison_dossiers"],2)
        self.assertEqual(obj["number_of_original_greek_verse_word_examples"],10)
        self.assertEqual(obj["lsj_original_entry_structures_verified_against_pinned_git_blobs"],3)
        self.assertEqual(obj["human_philological_approvals"],0)
        self.assertEqual(obj["owner_english_master_approvals"],0)
        self.assertEqual(obj["translated_scripture_verses_published"],0)
        self.assertEqual(obj["publication_status"],"BLOCKED")
        primary,secondary=obj["dossiers"]
        self.assertEqual(primary["total_original_rp2018_word_occurrences"],2315)
        self.assertEqual(secondary["total_original_rp2018_word_occurrences"],1287)
        self.assertEqual([x["source_original_lsj_tei_entry_id"] for x in
            primary["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]],
            ["n62204","n62205"])
        self.assertEqual([x["source_sense_opening_tag_count"] for x in
            primary["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]],[1,23])
        self.assertEqual([x["source_original_tr_tag_count"] for x in
            primary["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]],[1,76])
        self.assertEqual(primary["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"][0]
                         ["first_short_lsj_source_tr_excerpt_CC_BY_SA_NOT_OLT"],["lay"])
        self.assertEqual(primary["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"][1]
                         ["first_short_lsj_source_tr_excerpt_CC_BY_SA_NOT_OLT"],["pick up"])
        self.assertEqual([x["source_original_lsj_tei_entry_id"] for x in
            secondary["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]],
            ["n75695"])
        self.assertEqual(secondary["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"][0]
                         ["first_short_lsj_source_tr_excerpt_CC_BY_SA_NOT_OLT"],["that"])
        self.assertEqual([x["original_greek_reference"] for x in
            primary["original_source_context_examples_NOT_INTERPRETED"]],
            ["Matt.1.16","Mark.1.7","Matt.1.20","Matt.1.22","Luke.1.13"])
        self.assertEqual([x["original_greek_reference"] for x in
            secondary["original_source_context_examples_NOT_INTERPRETED"]],
            ["Matt.2.16","Mark.1.15","Matt.6.13","Luke.1.22","Matt.28.13"])
        for dossier in obj["dossiers"]:
            self.assertEqual(dossier["expert_approved_contextual_word_senses"],[])
            self.assertIsNone(dossier["independently_verified_contextual_greek_lemma"])
            self.assertFalse(dossier["independent_philological_signoff"])
            self.assertFalse(dossier["owner_english_master_approval"])
            self.assertIsNone(dossier["approved_english_word_or_phrase"])
            self.assertEqual(dossier["publication_status"],"BLOCKED")
            for entry in dossier["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]:
                self.assertEqual(entry["publication_status"],"BLOCKED")
                self.assertIsNone(entry["selected_contextual_sense"])
            for word in dossier["original_source_context_examples_NOT_INTERPRETED"]:
                self.assertEqual(word["publication_status"],"BLOCKED")
                self.assertIsNone(word["selected_independent_lexicon_entry"])
                self.assertIsNone(word["owner_english_lexical_equivalent"])
                original=word["original_greek_verse_UNALTERED"]
                span=word["original_source_unicode_word_character_span"]
                self.assertEqual(original[span["start"]:span["end_exclusive"]],
                                 word["exact_original_greek_word_UNALTERED"])

    def test_actual_pinned_external_lsj_lexical_comparison(self):
        original=os.environ.get("OLT037F_LSJ_DIR")
        if not original:
            self.skipTest("External original Perseus LSJ dictionary integration in dedicated CI")
        data=build_comparison_dossiers(Path(original))
        self.assertEqual(data["checkpoint"],CHECKPOINT)
        self.assertEqual(data["source_lsj_license"],"CC BY-SA 4.0")
        self.assertEqual(data["source_stepbible_license"],"CC BY 4.0")
        self.assertTrue(data["source_abbott_public_domain_AS_ASSERTED_BY_UPSTREAM"])
        self.assertEqual(data["lsj_original_entry_structures_verified_against_pinned_git_blobs"],3)
        self.assertEqual(data["number_of_comparison_dossiers"],2)
        self.assertEqual(data["number_of_original_greek_verse_word_examples"],10)
        self.assertEqual(data["human_philological_approvals"],0)
        self.assertEqual(data["owner_english_master_approvals"],0)
        self.assertEqual(data["translated_scripture_verses_published"],0)
        self.assertEqual(data["publication_status"],"BLOCKED")
        self.assertEqual([d["original_rp2018_editor_strong_number"] for d in data["dossiers"]],
                         ["3004","3754"])
        for dossier in data["dossiers"]:
            self.assertEqual(len(dossier["original_source_context_examples_NOT_INTERPRETED"]),5)
            self.assertIsNone(dossier["independently_verified_contextual_greek_lemma"])
            self.assertEqual(dossier["expert_approved_contextual_word_senses"],[])
            self.assertFalse(dossier["independent_philological_signoff"])
            self.assertFalse(dossier["owner_english_master_approval"])
            self.assertIsNone(dossier["approved_english_word_or_phrase"])
            self.assertEqual(dossier["publication_status"],"BLOCKED")
            self.assertTrue(all(e["selected_contextual_sense"] is None for e in
                dossier["perseus_lsj_exact_pinned_tei_entry_evidence_CC_BY_SA"]))
        p=ROOT/REPORT_PATH
        self.assertTrue(p.is_file(), "Canonical original-source comparison must be frozen")
        verify_frozen_source_dossiers(data)


if __name__=="__main__":
    unittest.main()
