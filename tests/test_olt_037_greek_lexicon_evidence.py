"""OLT-037: independent Greek lexicon research is not approved translation."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from olt_core.engine import SourceContractError
from olt_core.greek_lexicon import (
    _lexicon_line,
    _word_evidence,
    audit_lemma_evidence,
    parse_tbesg_text,
    read_tbesg,
    read_tbesg_manifest,
    verify_tbesg_bytes,
)
from olt_core.sources import git_blob_sha1

DATA = [
    "eStrong#\tdStrong\tuStrong\tGreek\tTransliteration\tMorph\tGloss\tMeaning",
    "G0026\tG0026 =\tG0026\tἀγάπη\tagapē\tN\tlove\tSource definition A",
    "G0026\tG0026G = a semantic category\tG0026G\tἀγάπη\tagapē\tN\tcharity\tSource definition B",
    "G3056\tG3056 =\tG3056\tλόγος\tlogos\tN\tword\tSource definition C",
]


class TestOLT037(unittest.TestCase):
    def test_manifest_pinned_real_upstream_licensing_and_publication_gate(self):
        d = read_tbesg_manifest()
        self.assertEqual(d["pinned_commit"], "be4191f0082aeedddb0eff0c02c966292b2bd641")
        self.assertEqual(d["expected_byte_length"], 4736912)
        self.assertEqual(d["original_source_git_blob_sha1"],
                         "efe271a1dbb73fa01f8fa6e0f164c6687757a9ae")
        self.assertEqual(d["source_data_license"], "CC BY 4.0")
        self.assertIn("STEP Bible", d["provenance_attribution"])
        self.assertEqual(d["source_join_type"], "NUMERIC_REFERENCE_CANDIDATES_ONLY")
        self.assertTrue(d["candidate_ambiguities_must_be_preserved"])
        self.assertTrue(d["original_file_not_vendored"])
        self.assertEqual(d["independent_lexical_review"], "NOT_DONE")
        self.assertEqual(d["publication_status"], "BLOCKED")

    def test_tsv_exact_eight_columns_and_preserve_two_rows_per_number(self):
        index = parse_tbesg_text("\n".join(DATA))
        self.assertEqual(set(index), {26, 3056})
        self.assertEqual(len(index[26]), 2)
        self.assertEqual(index[26][0]["source_disambiguated_strong"], "G0026")
        self.assertEqual(index[26][1]["source_disambiguated_strong"], "G0026G")
        self.assertEqual(index[26][1]["source_line_number"], 3)
        self.assertEqual(index[26][1]["source_dstrong_relation_note"], "a semantic category")
        self.assertEqual(index[26][0]["source_greek_lemma_form_candidate"], "ἀγάπη")
        self.assertEqual(index[26][1]["source_english_short_gloss_EVIDENCE_ONLY"], "charity")
        self.assertIs(index[26][1]["translation_approved"], False)
        self.assertEqual(index[26][1]["sense_selection"], "NOT_DONE")

    def test_numeric_reference_candidate_layer_never_selects_lemma(self):
        index = parse_tbesg_text("\n".join(DATA))
        m = read_tbesg_manifest()
        word = {
            "derived_source_locator": "rp2018-v3.3.2:Matt.1.1:w0001",
            "source_reference": "Matt.1.1",
            "accented_unicode_word_form": "ἀγάπη",
            "beta_code_word_form": "agaph",
            "official_editor_strong_number": "26",
            "official_editor_morphology_code": "N-NSF",
            "additional_editor_analyses": [],
        }
        many = _word_evidence(word, index, m)
        self.assertEqual(many["candidate_count"], 2)
        self.assertEqual(many["numeric_only_source_reference_status"],
                         "MULTIPLE_NUMERIC_SOURCE_CANDIDATES_UNRESOLVED")
        self.assertIsNone(many["selected_lemma"])
        self.assertIsNone(many["selected_sense"])
        self.assertIsNone(many["approved_english_translation"])
        self.assertEqual(many["publication_status"], "BLOCKED")
        single = _word_evidence(dict(word, official_editor_strong_number="3056"), index, m)
        self.assertEqual(single["candidate_count"], 1)
        self.assertEqual(single["numeric_only_source_reference_status"],
                         "ONE_NUMERIC_SOURCE_CANDIDATE_NOT_REVIEWED")
        self.assertIsNone(single["selected_lemma"])
        none = _word_evidence(dict(word, official_editor_strong_number="99999"), index, m)
        self.assertEqual(none["candidate_count"], 0)
        self.assertEqual(none["source_lemma_candidates_NOT_CERTIFIED"], [])
        self.assertIsNone(none["selected_lemma"])

    def test_empty_duplicate_and_truncated_source_fail_closed(self):
        with self.assertRaises(SourceContractError):
            parse_tbesg_text("")
        with self.assertRaises(SourceContractError):
            parse_tbesg_text("\n".join([DATA[1], DATA[1]]))
        with self.assertRaises(SourceContractError):
            parse_tbesg_text("G0026\tG0026 =\tG0026\tἀγάπη\tX")
        with self.assertRaises(SourceContractError):
            parse_tbesg_text("G0026\tInvalidTag =\tG0026\tἀγάπη\tX\tN\tlove\ttext")
        with self.assertRaises(SourceContractError):
            parse_tbesg_text("G0026\tG0000 =\tG0026\tἀγάπη\tX\tN\tlove\ttext")

    def test_unsupported_strong_number_never_guessed(self):
        m = read_tbesg_manifest()
        with self.assertRaises(SourceContractError):
            _word_evidence({
                "official_editor_strong_number": "G0026",
            }, parse_tbesg_text("\n".join(DATA)), m)

    def test_blob_integrity_negative_controls(self):
        data = b"exact pinned test fixture"
        fixture = {
            "expected_byte_length": len(data),
            "original_source_git_blob_sha1": git_blob_sha1(data),
        }
        verify_tbesg_bytes(data, fixture)
        with self.assertRaises(SourceContractError):
            verify_tbesg_bytes(data + b"X", fixture)
        with self.assertRaises(SourceContractError):
            verify_tbesg_bytes(data.replace(b"test", b"more"), fixture)
        bad = deepcopy(fixture)
        bad["original_source_git_blob_sha1"] = "0" * 40
        with self.assertRaises(SourceContractError):
            verify_tbesg_bytes(data, bad)

    def test_real_pinned_tbesg_and_all_rp2018_word_positions_in_ci(self):
        source = os.environ.get("OLT037_TBESG_PATH")
        if not source:
            self.skipTest("Provide OLT037_TBESG_PATH to run integration against pinned TBESG")
        path = Path(source)
        self.assertTrue(path.exists(), "Missing CI-fetched source")
        groups = read_tbesg(path)
        self.assertGreater(len(groups), 1000)
        self.assertTrue(all(len(rows) >= 1 for rows in groups.values()))
        audit = audit_lemma_evidence(groups)
        self.assertEqual(audit["source_git_blob_sha1"],
                         "efe271a1dbb73fa01f8fa6e0f164c6687757a9ae")
        self.assertEqual(audit["rp2018_original_word_positions"], 140149)
        self.assertEqual(audit["alternative_editor_analyses_preserved"], 28)
        self.assertEqual(sum([
            audit["word_positions_with_one_numeric_candidate"],
            audit["word_positions_with_multiple_numeric_candidates_NOT_RESOLVED"],
            audit["word_positions_without_numeric_candidate"]
        ]), 140149)
        self.assertFalse(audit["ambiguity_auto_resolved"])
        self.assertFalse(audit["english_master_lexicon_approved"])
        self.assertEqual(audit["publication_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
