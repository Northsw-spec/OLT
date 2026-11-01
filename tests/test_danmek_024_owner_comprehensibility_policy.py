"""DANMEK-024 owner policy: keep readability work active without false claims."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/policy/danmek_024_english_comprehensibility_owner_priority.json"
DOC = ROOT / "docs/DANMEK_024_OWNER_ENGLISH_COMPREHENSIBILITY_AND_WORD_ORDER.md"


class TestDanMek024OwnerComprehensibilityGate(unittest.TestCase):
    def test_explicit_readability_priority_and_no_automatic_edit(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(
            policy["checkpoint"],
            "DANMEK-024-OWNER-ENGLISH-COMPREHENSIBILITY-PRIORITY-2026-11-01",
        )
        self.assertEqual(policy["status"], "ACTIVE")
        true_fields = (
            "must_continue_review_of_311_ambiguous_english_order_cases",
            "cases_311_are_not_asserted_translation_errors",
            "goal_is_not_wholesale_retranslation_of_DANMEK",
            "comprehensibility_review_covers_more_than_the_311_regex_ambiguities",
            "owner_previous_satisfaction_not_blanket_linguistic_certification",
            "existing_english_reader_is_immutable_reference_baseline",
            "english_case_proposals_require_traceable_sources",
            "automatic_english_word_order_proposal_generation_allowed",
            "plausible_english_candidate_must_not_be_mislabeled_verified",
            "preserve_english_early_modern_register",
            "preserve_english_simple_past_for_only_verified_wayyiqtol",
            "preserve_waw_as_and_where_original_hebrew_supports_it",
            "preserve_english_explicit_subject_repetition_where_required",
            "preserve_source_semantics_and_lexical_owner_decisions",
            "protect_no_divine_pronoun_capitalization_rule",
            "protected_english_reader_code_and_existing_snapshot_must_not_change_without_separate_user_approval",
        )
        for field in true_fields:
            self.assertIs(policy[field], True, field)
        false_fields = (
            "automatic_application_to_owner_verified_english_reader_allowed",
            "automatic_unverified_grammar_signoff_allowed",
            "original_subject_identification_without_verified_source_alignment_allowed",
            "original_ches_and_oshb_source_text_public_upload_allowed",
            "independent_hebrew_to_english_word_alignment_verified",
            "all_311_grammar_conclusions_verified",
            "full_english_bible_translation_owner_approved",
        )
        for field in false_fields:
            self.assertIs(policy[field], False, field)
        self.assertEqual(policy["publication_status"], "BLOCKED")
        self.assertEqual(
            policy["next_engineering_checkpoint"],
            "DANMEK-025-PRIVATE_ENGLISH_READABILITY_PROPOSALS",
        )
        self.assertIn("INSUFFICIENT_SOURCE_ALIGNMENT",
                      policy["proposed_candidate_statuses"])
        self.assertIn("NO_CHANGE_RECOMMENDED_WITH_REASON",
                      policy["proposed_candidate_statuses"])
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn("311", doc)
        self.assertIn("a command to stop grammar/reordering work", doc)
        self.assertIn("DANMEK-025", doc)
        self.assertIn("publication", doc.lower())

    def test_no_licensed_source_data_or_private_paths_in_new_policy(self):
        combined = POLICY.read_text() + DOC.read_text()
        for forbidden in (
            "/home/", "source_ches_spans_NOT_OLT_TRANSLATION",
            "private_ches_text", "original_script",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertEqual((ROOT / "README.md").read_bytes(), b"")


if __name__ == "__main__":
    unittest.main()
