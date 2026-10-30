"""OLT-037C: no contextual source exemplar can become an invented Greek gloss."""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
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
from olt_core.greek_alignment import read_aligned_greek_book
from olt_core.greek_lexicon import read_tbesg
from olt_core.greek_sense_dossier import (
    CASE_NUMBERS, CHECKLIST, CHECKPOINT, PREVIOUS_REPORT_SHA256,
    REPORT_PATH, _load_frozen_triage, _occurrence, _sample_with_reasons,
    _validate_context, build_context_dossiers, emit_source_checkpoint,
    serialize_dossiers, verify_frozen_dossiers,
)


class TestOLT037C(unittest.TestCase):
    def test_target_scope_is_explicit_and_no_approval_criteria_are_skipped(self):
        self.assertEqual(CASE_NUMBERS, (3004, 3754))
        self.assertEqual(CHECKPOINT, "OLT-037C")
        self.assertEqual(PREVIOUS_REPORT_SHA256,
                         "a0291d66b506f7070263e8afc8c78ac160d2f9081720993b487e0cee3bc6db5b")
        self.assertEqual(len(CHECKLIST), 7)
        self.assertTrue(any("Greek syntax" in item for item in CHECKLIST))
        self.assertTrue(any("independent Greek lexica" in item for item in CHECKLIST))
        self.assertTrue(any("human scholarly signoff" in item for item in CHECKLIST))

    def test_full_107_case_source_queue_must_be_unchanged(self):
        old = _load_frozen_triage(ROOT)
        self.assertEqual(old["distinct_numeric_reference_review_cases"], 107)
        self.assertEqual(old["reviewed_cases"], 0)
        self.assertEqual(old["publication_status"], "BLOCKED")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json"
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / "data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json")
                               .read_bytes() + b" ")
            with self.assertRaises(SourceContractError):
                _load_frozen_triage(root)

    def test_context_window_must_match_original_unicode_offsets(self):
        greek = read_aligned_greek_book("3JO")
        verse = next(x for x in greek["aligned_verses"] if x["reference"] == "3John.1.1")
        first = verse["words"][0]
        _validate_context(first, verse, 1)
        occurrence = _occurrence(greek["book_id"], verse, 1)
        self.assertEqual(occurrence["source_word_ordinal"], 1)
        self.assertEqual(occurrence["original_unicode_word"],
                         first["accented_unicode_word_form"])
        self.assertEqual(occurrence["source_previous_three_words"], [])
        self.assertTrue(occurrence["source_next_three_words"])
        self.assertEqual(occurrence["publication_status"], "BLOCKED")
        self.assertIsNone(occurrence["selected_stepbible_sense"])
        self.assertIsNone(occurrence["selected_english_translation"])

        altered = deepcopy(first)
        altered["unicode_verse_character_span"]["start"] += 1
        with self.assertRaises(SourceContractError):
            _validate_context(altered, verse, 1)
        bad_verse = dict(verse, original_accented_greek_verse="INVENTED GREEK")
        with self.assertRaises(SourceContractError):
            _validate_context(first, bad_verse, 1)
        bad_word = dict(first, owner_translation="guessed English translation")
        with self.assertRaises(SourceContractError):
            _validate_context(bad_word, verse, 1)

    def test_deterministic_samples_preserve_all_raw_morph_codes_and_surface_forms(self):
        records = [
            {"book": "Matt", "olt_derived_word_locator_NOT_PUBLISHER_NATIVE": "a",
             "original_rp2018_editor_morphology": "V-1",
             "original_unicode_word": "λέγων", "publication_status": "BLOCKED",
             "selected_stepbible_sense": None, "selected_english_translation": None},
            {"book": "Matt", "olt_derived_word_locator_NOT_PUBLISHER_NATIVE": "b",
             "original_rp2018_editor_morphology": "V-2",
             "original_unicode_word": "εἶπεν", "publication_status": "BLOCKED",
             "selected_stepbible_sense": None, "selected_english_translation": None},
            {"book": "Mark", "olt_derived_word_locator_NOT_PUBLISHER_NATIVE": "c",
             "original_rp2018_editor_morphology": "V-1",
             "original_unicode_word": "λέγων", "publication_status": "BLOCKED",
             "selected_stepbible_sense": None, "selected_english_translation": None},
        ]
        selected = _sample_with_reasons(records)
        self.assertEqual([x["olt_derived_word_locator_NOT_PUBLISHER_NATIVE"] for x in selected],
                         ["a", "b", "c"])
        self.assertIn("FIRST_OCCURRENCE_OF_EXACT_UNICODE_SURFACE",
                      selected[0]["sample_selection_reasons"])
        self.assertIn("LAST_OCCURRENCE_IN_BOOK_SOURCE_ORDER",
                      selected[1]["sample_selection_reasons"])
        self.assertIn("FIRST_OCCURRENCE_IN_BOOK_SOURCE_ORDER",
                      selected[2]["sample_selection_reasons"])
        with self.assertRaises(SourceContractError):
            _sample_with_reasons([])
        translated = deepcopy(records)
        translated[0]["selected_english_translation"] = "guessed"
        with self.assertRaises(SourceContractError):
            _sample_with_reasons(translated)

    def test_exact_dossier_serialization_and_tampering_controls(self):
        payload = {"checkpoint": CHECKPOINT, "approved_greek_lemma": None,
                   "original_word": "ἔλεγεν", "publication_status": "BLOCKED"}
        plain = serialize_dossiers(payload)
        self.assertEqual(json.loads(plain), payload)
        self.assertTrue(plain.endswith("\n"))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / REPORT_PATH
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(plain, encoding="utf-8")
            verify_frozen_dossiers(payload, Path(d))
            path.write_text(plain.replace("BLOCKED", "APPROVED"), encoding="utf-8")
            with self.assertRaises(SourceContractError):
                verify_frozen_dossiers(payload, Path(d))
            path.unlink()
            with self.assertRaises(SourceContractError):
                verify_frozen_dossiers(payload, Path(d))

    def test_ci_checkpoint_transfer_is_content_addressable(self):
        payload = {"checkpoint": CHECKPOINT, "source_text": "λέγων", "selected_sense": None}
        out = StringIO()
        with redirect_stdout(out):
            emit_source_checkpoint(payload)
        lines = out.getvalue().splitlines()
        self.assertEqual(lines[0], "OLT037C_CHECKPOINT_BEGIN")
        self.assertTrue(lines[-1].startswith("OLT037C_CHECKPOINT_END "))
        import base64
        data = base64.b64decode("".join(
            line.removeprefix("OLT037C_CHECKPOINT_PART ") for line in lines[1:-1]
        ), validate=True)
        self.assertEqual(data, serialize_dossiers(payload).encode("utf-8"))
        self.assertEqual(hashlib.sha256(data).hexdigest(), lines[-1].split()[-1])

    def test_pinned_original_3004_and_3754_source_dossiers(self):
        path = os.environ.get("OLT037_TBESG_PATH")
        if not path:
            self.skipTest("External pinned lexicon integration runs in dedicated OLT-037C CI")
        source = read_tbesg(Path(path))
        report = build_context_dossiers(source)
        self.assertEqual(report["all_nt_original_greek_word_positions_inspected"], 140149)
        self.assertEqual(report["number_of_case_studies"], 2)
        self.assertEqual(report["number_of_verified_greek_lemma_decisions"], 0)
        self.assertEqual(report["number_of_approved_english_master_entries"], 0)
        self.assertEqual(report["number_of_generated_target_translations"], 0)
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertTrue(report["no_english_gloss_treated_as_translation"])
        one, control = report["cases"]
        self.assertEqual(one["rp2018_original_editor_strong_number"], "3004")
        self.assertEqual(one["primary_source_word_positions"], 2315)
        self.assertEqual(one["observed_original_greek_unicode_surface_count"], 83)
        self.assertEqual([x["native_step_dstrong"] for x in
                          one["source_lexicon_candidates_NOT_APPROVED"]],
                         ["G3004G", "G3004H"])
        self.assertEqual(one["literal_candidate_headword_count"], 1)
        self.assertTrue(one["literal_candidate_headwords_all_equal"])
        self.assertEqual(control["rp2018_original_editor_strong_number"], "3754")
        self.assertEqual(control["primary_source_word_positions"], 1287)
        self.assertEqual(control["observed_original_greek_unicode_surface_count"], 2)
        self.assertEqual([x["native_step_dstrong"] for x in
                          control["source_lexicon_candidates_NOT_APPROVED"]],
                         ["G3754G", "G3754H"])
        for case in report["cases"]:
            samples = case["sampled_original_greek_contexts_NO_SENSE_ASSIGNED"]
            self.assertEqual(len(samples), case["evidence_sample_count"])
            self.assertEqual(len(set(x["original_unicode_word"] for x in samples)),
                             case["observed_original_greek_unicode_surface_count"])
            self.assertEqual(len(set(x["original_rp2018_editor_morphology"] for x in samples)),
                             len(case["original_raw_editor_morphology_code_frequencies"]))
            self.assertEqual(set(x["book"] for x in samples),
                             set(case["original_source_occurrences_by_book"]))
            self.assertTrue(all(x["selected_stepbible_sense"] is None and
                                x["selected_english_translation"] is None and
                                x["publication_status"] == "BLOCKED"
                                for x in samples))
            self.assertIsNone(case["approved_greek_lemma"])
            self.assertIsNone(case["approved_english_translation"])
            self.assertFalse(case["independent_philological_signoff"])
            self.assertFalse(case["owner_editorial_approval"])
            self.assertFalse(any(x["contextual_sense_assignments"] for x in [case]))
        committed = ROOT / REPORT_PATH
        if committed.is_file():
            verify_frozen_dossiers(report)


if __name__ == "__main__":
    unittest.main()
