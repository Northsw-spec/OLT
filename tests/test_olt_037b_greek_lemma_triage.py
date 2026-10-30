"""OLT-037B: falsifiable source-based Greek numeric ambiguity triage."""
from __future__ import annotations

import base64
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from olt_core.engine import SourceContractError
from olt_core.greek_alignment import read_aligned_greek_book
from olt_core.greek_lemma_triage import (
    CHECKPOINT, SOURCE_STATUS, _source_candidate_brief,
    _validate_original_word, build_review_queue, emit_checkpoint_chunks,
    serialize_review_queue, verify_committed_queue,
)
from olt_core.greek_lexicon import read_tbesg

ROW = {
    "source": "STEPBible_TBESG_CC_BY_4_0",
    "publication_status": "BLOCKED",
    "translation_approved": False,
    "source_disambiguated_strong": "G0026G",
    "source_extended_strong": "G0026",
    "source_unified_strong": "G0026G",
    "source_dstrong_relation_note": "source editor's category",
    "source_line_number": 71,
    "source_greek_lemma_form_candidate": "ἀγάπη",
    "source_morph_category": "N",
    "source_english_short_gloss_EVIDENCE_ONLY": "source gloss",
}


class TestOLT037B(unittest.TestCase):
    def test_source_candidate_presents_ids_without_translation_approval(self):
        candidate = _source_candidate_brief(ROW)
        self.assertEqual(candidate["native_step_dstrong"], "G0026G")
        self.assertEqual(candidate["source_extended_strong"], "G0026")
        self.assertEqual(candidate["source_line_number"], 71)
        self.assertEqual(candidate["greek_lemma_HEADWORD_CANDIDATE_ONLY"], "ἀγάπη")
        self.assertEqual(candidate["english_short_gloss_SOURCE_ONLY_NOT_OLT_TRANSLATION"],
                         "source gloss")
        self.assertNotIn("selected_lemma", candidate)
        self.assertNotIn("approved_english_translation", candidate)

    def test_source_candidate_rejects_falsely_approved_rows(self):
        for edited in [
            dict(ROW, translation_approved=True),
            dict(ROW, publication_status="PUBLISHED"),
            dict(ROW, source="OTHER_UNPINNED_SOURCE"),
        ]:
            with self.subTest(edited=edited):
                with self.assertRaises(SourceContractError):
                    _source_candidate_brief(edited)

    def test_actual_original_greek_word_locator_is_derived_and_not_approved(self):
        book = read_aligned_greek_book("3JO")
        verse = next(v for v in book["aligned_verses"] if v["reference"] == "3John.1.1")
        word = verse["words"][0]
        self.assertEqual(_validate_original_word(word, "3John.1.1", 1), 3588)
        self.assertIsNone(word["original_source_native_word_id"])
        self.assertEqual(word["publication_status"], "BLOCKED")
        for changed in [
            dict(word, publication_status="APPROVED"),
            dict(word, original_source_native_word_id="invented"),
            dict(word, source_reference="3John.1.2"),
            dict(word, ordinal_in_source_verse=2),
            dict(word, official_editor_strong_number="0"),
            dict(word, official_editor_strong_number="G3588"),
            dict(word, owner_translation="fake"),
        ]:
            with self.subTest(changed=changed):
                with self.assertRaises(SourceContractError):
                    _validate_original_word(changed, "3John.1.1", 1)

    def test_canonical_serialization_and_explicit_snapshot_drift_detection(self):
        payload = {"checkpoint": CHECKPOINT, "reviewed_cases": 0,
                   "publication_status": "BLOCKED"}
        canonical = serialize_review_queue(payload)
        self.assertEqual(json.loads(canonical), payload)
        self.assertTrue(canonical.endswith("\n"))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(canonical, encoding="utf-8")
            verify_committed_queue(payload, Path(d))
            path.write_text(canonical.replace("BLOCKED", "APPROVED"),
                            encoding="utf-8")
            with self.assertRaises(SourceContractError):
                verify_committed_queue(payload, Path(d))
            path.unlink()
            with self.assertRaises(SourceContractError):
                verify_committed_queue(payload, Path(d))

    def test_checkpoints_are_lossless_and_sha_verified_in_logs(self):
        obj = {"checkpoint": CHECKPOINT, "unicode": "Γαΐῳ",
               "source": "STEP Bible CC BY 4.0", "selected_lemma": None}
        buffer = StringIO()
        with redirect_stdout(buffer):
            emit_checkpoint_chunks(obj)
        lines = buffer.getvalue().splitlines()
        self.assertEqual(lines[0], "OLT037B_CHECKPOINT_BEGIN")
        self.assertTrue(lines[-1].startswith("OLT037B_CHECKPOINT_END "))
        encoded = "".join(s.removeprefix("OLT037B_CHECKPOINT_PART ")
                          for s in lines[1:-1])
        decoded = base64.b64decode(encoded, validate=True)
        self.assertEqual(decoded, serialize_review_queue(obj).encode("utf-8"))
        self.assertEqual(lines[-1].split()[-1], hashlib.sha256(decoded).hexdigest())

    def test_small_fake_lexicon_cannot_pass_full_original_corpus_audit(self):
        # Full 27-book counts and source identity are mandatory. A fixture with
        # two synthetic dictionary candidates is not an accepted production audit.
        from olt_core.greek_lexicon import parse_tbesg_text
        synthetic = ("G0026\tG0026 =\tG0026\tἀγάπη\ta\tN\tlove\tdefinition\n"
                     "G0026\tG0026B =\tG0026\tἀγάπη\ta\tN\tlove\tdefinition")
        groups = parse_tbesg_text(synthetic)
        with self.assertRaises(SourceContractError):
            build_review_queue(groups)

    def test_frozen_complete_review_queue_is_unapproved_and_source_scoped(self):
        path = ROOT / "data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json"
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "a0291d66b506f7070263e8afc8c78ac160d2f9081720993b487e0cee3bc6db5b")
        report = json.loads(raw.decode("utf-8"))
        self.assertEqual(report["checkpoint"], CHECKPOINT)
        self.assertEqual(report["distinct_numeric_reference_review_cases"], 107)
        self.assertEqual(report["rp2018_primary_word_positions"], 140149)
        self.assertEqual(report["primary_positions_with_multiple_numeric_candidates"], 12539)
        self.assertEqual(report["original_editor_alternative_analyses"], 28)
        self.assertEqual(report["reviewed_cases"], 0)
        self.assertEqual(report["approved_english_lexical_entries"], 0)
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertEqual(sum(c["source_word_occurrence_count"] for c in report["cases"]), 12539)
        self.assertEqual(len(report["original_editor_alternative_analysis_review_queue"]), 28)
        self.assertEqual(report["cases"][0]["original_rp2018_strong_number"], "3004")
        self.assertTrue(all(c["selected_dstrong"] is None
                            and c["selected_lexical_sense"] is None
                            and c["owner_editorial_approval"] is False
                            and c["independent_philological_signoff"] is False
                            and c["publication_status"] == "BLOCKED"
                            for c in report["cases"]))

    def test_complete_original_source_triage_requires_pinned_tbseg(self):
        source = os.environ.get("OLT037_TBESG_PATH")
        if not source:
            self.skipTest("Full source-pinned TBESG integration runs in dedicated GitHub CI")
        groups = read_tbesg(Path(source))
        result = build_review_queue(groups)
        self.assertEqual(result["checkpoint"], CHECKPOINT)
        self.assertEqual(result["rp2018_primary_word_positions"], 140149)
        self.assertEqual(result["primary_positions_with_single_numeric_candidate"], 127610)
        self.assertEqual(result["primary_positions_with_multiple_numeric_candidates"], 12539)
        self.assertEqual(result["primary_positions_without_numeric_candidate"], 0)
        self.assertGreater(result["distinct_numeric_reference_review_cases"], 0)
        self.assertEqual(result["original_editor_alternative_analyses"], 28)
        self.assertEqual(sum(x["source_word_occurrence_count"]
                             for x in result["cases"]), 12539)
        self.assertEqual(len(result["original_editor_alternative_analysis_review_queue"]), 28)
        self.assertTrue(all(x["candidate_ambiguity_kind"] ==
                            "MULTIPLE_STEP_DSTRONG_SAME_NUMERIC_PORTION" and
                            x["source_evidence_status"] == SOURCE_STATUS and
                            x["scientific_classification"] == "NOT_YET_DETERMINED" and
                            x["homonym_vs_polysemy_vs_entity_distinction"] == "NOT_REVIEWED" and
                            x["selected_dstrong"] is None and
                            x["selected_greek_lemma"] is None and
                            not x["independent_philological_signoff"] and
                            x["publication_status"] == "BLOCKED"
                            for x in result["cases"]))
        self.assertTrue(all(x["selected_primary_or_alternative"] is None and
                            x["publication_status"] == "BLOCKED"
                            for x in result["original_editor_alternative_analysis_review_queue"]))
        self.assertEqual(result["reviewed_cases"], 0)
        self.assertEqual(result["approved_english_lexical_entries"], 0)
        self.assertEqual(result["publication_status"], "BLOCKED")
        saved = ROOT / "data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json"
        self.assertTrue(saved.exists(), "Canonical Greek triage checkpoint must exist")
        verify_committed_queue(result)


if __name__ == "__main__":
    unittest.main()
