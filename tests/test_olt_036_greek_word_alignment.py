"""OLT-036: genuine RP2018 Beta Code/Unicode word-alignment regression tests."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from olt_core.engine import SourceContractError
from olt_core.greek_alignment import (
    ALIGNMENT_STATUS,
    NORMALIZATION_ID,
    _align_word_verse,
    _beta_to_unaccented_greek,
    _normalized_greek_unicode,
    greek_unicode_tokens,
    read_aligned_greek_book,
    verify_greek_word_alignment,
)
from olt_core.greek_words import read_parsed_greek_book
from olt_core.nt_corpus import read_nt_book


class TestOLT036(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.strongs = read_parsed_greek_book("3JO")
        cls.greek = read_nt_book("3JO")
        cls.bp5_verse = next(x for x in cls.strongs["verse_records"]
                              if x["reference"] == "3John.1.1")
        cls.unicode_verse = next(x for x in cls.greek["verses"]
                                  if x["reference"] == "3John.1.1")

    def test_full_27_book_strict_word_alignment_and_release_gate(self):
        audit = verify_greek_word_alignment()
        self.assertEqual(audit["books"], 27)
        self.assertEqual(audit["fully_position_and_normalization_matched_verses"], 7953)
        self.assertEqual(audit["fully_position_and_normalization_matched_words"], 140149)
        self.assertEqual(audit["source_morphology_alternative_analyses_preserved"], 28)
        self.assertEqual(audit["source_only_empty_verse_positions"],
                         ["Acts.15.34", "Acts.24.7", "Acts.8.37", "Luke.17.36"])
        self.assertTrue(audit["normalization_is_lossy"])
        self.assertEqual(audit["normalization_id"], NORMALIZATION_ID)
        self.assertFalse(audit["publisher_native_word_ids_available"])
        self.assertFalse(audit["english_master_lexicon_approved"])
        self.assertFalse(audit["target_language_translation_approved"])
        self.assertEqual(audit["publication_status"], "BLOCKED")
        self.assertEqual(sum(b["aligned_words"] for b in audit["per_book"]), 140149)
        self.assertGreater(audit["unicode_tokens_with_iota_subscript_ignored_in_comparison"], 0)

    def test_3john_word_level_sources_offsets_and_no_approvals(self):
        book = read_aligned_greek_book("3JO")
        self.assertEqual(book["aligned_verse_count"], 14)
        verse = book["aligned_verses"][0]
        self.assertEqual(verse["reference"], "3John.1.1")
        self.assertEqual(verse["word_alignment_status"], ALIGNMENT_STATUS)
        self.assertEqual(verse["source_word_count"], 10)
        self.assertEqual(verse["words"][0]["beta_code_word_form"], "o")
        self.assertEqual(verse["words"][0]["accented_unicode_word_form"], "Ὁ")
        self.assertEqual(verse["words"][2]["beta_code_word_form"], "gaiw")
        self.assertEqual(verse["words"][2]["accented_unicode_word_form"], "Γαΐῳ")
        self.assertTrue(verse["words"][2]["unicode_surface_has_iota_subscript"])
        self.assertEqual(verse["words"][2]["official_editor_strong_number"], "1050")
        for index, word in enumerate(verse["words"], 1):
            with self.subTest(index=index):
                span = word["unicode_verse_character_span"]
                self.assertEqual(verse["original_accented_greek_verse"][
                    span["start"]:span["end_exclusive"]
                ], word["accented_unicode_word_form"])
                self.assertEqual(word["ordinal_in_source_verse"], index)
                self.assertEqual(word["unicode_word_position_derived_by_olt"], index)
                self.assertEqual(word["unicode_word_form_alignment"], ALIGNMENT_STATUS)
                self.assertTrue(word["alignment_is_lossy_and_not_lemma_approval"])
                self.assertIsNone(word["original_source_native_word_id"])
                self.assertIsNone(word["owner_translation"])
                self.assertFalse(word["strong_number_is_verified_dictionary_lemma"])
                self.assertEqual(word["publication_status"], "BLOCKED")
        # Read-only join: the 035D source adapter itself remains unchanged.
        self.assertIsNone(self.bp5_verse["words"][2]["accented_unicode_word_form"])
        self.assertEqual(self.bp5_verse["words"][2]["unicode_word_form_alignment"],
                         "NOT_PERFORMED")

    def test_specific_normalization_is_documented_and_lossy(self):
        self.assertEqual(_beta_to_unaccented_greek("gaiw"), "γαιω")
        self.assertEqual(_normalized_greek_unicode("Γαΐῳ"), ("γαιω", True))
        self.assertEqual(_normalized_greek_unicode("τῇ"), ("τη", True))
        self.assertEqual(_normalized_greek_unicode("Ὁ"), ("ο", False))
        self.assertEqual(_normalized_greek_unicode("λόγος"), ("λογοσ", False))
        self.assertEqual(_beta_to_unaccented_greek("logos"), "λογοσ")
        with self.assertRaises(SourceContractError):
            _normalized_greek_unicode("τ\u0305ῇ")  # unapproved mark must not be stripped
        with self.assertRaises(SourceContractError):
            _beta_to_unaccented_greek("Gaiw")
        with self.assertRaises(SourceContractError):
            _beta_to_unaccented_greek("γαιω")

    def test_punctuation_boundaries_and_exact_offsets(self):
        raw = "¶Ἀγαπητέ, ἀλλ’ Ὁ· τῷ."
        tokens = greek_unicode_tokens(raw)
        self.assertEqual([x["surface"] for x in tokens],
                         ["Ἀγαπητέ", "ἀλλ", "Ὁ", "τῷ"])
        self.assertTrue(all(raw[x["start"]:x["end"]] == x["surface"]
                            for x in tokens))
        with self.assertRaises(SourceContractError):
            greek_unicode_tokens("Ὁ hello")
        with self.assertRaises(SourceContractError):
            greek_unicode_tokens("Ὁ \u0345")

    def test_fail_closed_wrong_same_count_word_spelling(self):
        damaged = deepcopy(self.bp5_verse)
        damaged["words"][1]["beta_code_word_form"] = "presbuterox"
        with self.assertRaises(SourceContractError):
            _align_word_verse(damaged, self.unicode_verse)

    def test_fail_closed_reordered_word_even_if_count_matches(self):
        damaged = deepcopy(self.bp5_verse)
        damaged["words"][0]["beta_code_word_form"] = "presbuteros"
        damaged["words"][1]["beta_code_word_form"] = "o"
        with self.assertRaises(SourceContractError):
            _align_word_verse(damaged, self.unicode_verse)

    def test_fail_closed_count_mismatch_no_fuzzy_join(self):
        damaged = deepcopy(self.bp5_verse)
        damaged["words"].pop()
        damaged["source_word_count"] -= 1
        with self.assertRaises(SourceContractError):
            _align_word_verse(damaged, self.unicode_verse)

    def test_fail_closed_unicode_character_changed(self):
        damaged = deepcopy(self.unicode_verse)
        damaged["original_greek_text"] = damaged["original_greek_text"].replace(
            "πρεσβύτερος", "πρεσβύτερον"
        )
        with self.assertRaises(SourceContractError):
            _align_word_verse(self.bp5_verse, damaged)

    def test_fail_closed_reference_or_source_ordinal_reassigned(self):
        bad_ref = deepcopy(self.unicode_verse)
        bad_ref["reference"] = "3John.1.2"
        with self.assertRaises(SourceContractError):
            _align_word_verse(self.bp5_verse, bad_ref)
        damaged = deepcopy(self.bp5_verse)
        damaged["words"][1]["ordinal_in_source_verse"] = 1
        with self.assertRaises(SourceContractError):
            _align_word_verse(damaged, self.unicode_verse)

    def test_four_empty_slots_stay_empty_and_uncopied(self):
        luke = read_aligned_greek_book("LUK")
        acts = read_aligned_greek_book("ACT")
        self.assertEqual([x["reference"] for x in luke["empty_bp5_placeholders"]],
                         ["Luke.17.36"])
        self.assertEqual({x["reference"] for x in acts["empty_bp5_placeholders"]},
                         {"Acts.8.37", "Acts.15.34", "Acts.24.7"})
        self.assertTrue(all(x["word_count"] == 0 for x in
                            luke["empty_bp5_placeholders"] +
                            acts["empty_bp5_placeholders"]))

    def test_multiple_editor_analyses_still_on_one_original_word(self):
        matt = read_aligned_greek_book("MAT")
        verse = next(v for v in matt["aligned_verses"]
                     if v["reference"] == "Matt.26.45")
        alternatives = [w for w in verse["words"] if w["additional_editor_analyses"]]
        self.assertTrue(alternatives)
        self.assertTrue(all(w["accented_unicode_word_form"] is not None
                            for w in alternatives))
        self.assertEqual(matt["alternative_editor_parsings_preserved"], 6)
        self.assertEqual(matt["publication_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
