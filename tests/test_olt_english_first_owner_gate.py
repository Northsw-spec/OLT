"""OLT-ENGLISH-FIRST-001: fail-closed owner English-only development scope.

These are owner *project-scope* checks, NOT certificates of original-language
philology, English Bible completeness, owner approval, or publication.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"data/policy/olt_english_first_owner_verification.json"
STATUS=ROOT/"docs/STATUS_CURRENT.md"
ARCH=ROOT/"docs/OLT-034_MULTILINGUAL_ARCHITECTURE.md"
README=ROOT/"README.md"
DOC=ROOT/"docs/OLT_ENGLISH_FIRST_OWNER_GATE.md"


class TestOLTEnglishFirstOwnerGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=json.loads(POLICY.read_text(encoding="utf-8"))

    def test_single_active_target_is_english_and_all_others_deferred(self):
        p=self.policy
        self.assertEqual(p["policy_id"],"OLT-ENGLISH-FIRST-001")
        self.assertEqual(p["binding_owner_decision_date"],"2026-10-31")
        self.assertEqual(p["active_translation_target_language"],"en")
        self.assertEqual(p["active_translation_target_language_name"],"English")
        self.assertEqual(p["owner_priority"],
                         "SINGLE_ACTIVE_TARGET_LANGUAGE_ENGLISH_UNTIL_COMPLETE_OWNER_VERIFIED_BIBLE")
        self.assertEqual(p["original_source_languages"],
                         ["Biblical Hebrew","Biblical Aramaic","Koine Greek"])
        self.assertEqual(p["active_source_to_target_direction"],
                         ["hbo -> en","arc -> en","grc -> en"])
        self.assertEqual(p["all_original_scripture_books_required"],66)
        self.assertEqual(p["original_testaments_required"],["OT","NT"])
        self.assertNotIn("ja",p["active_source_to_target_direction"])
        self.assertIn("ja",p["target_languages_deferred_until_owner_verifies_complete_english"])
        self.assertTrue(all(x not in {"en","English"} for x in
            p["target_languages_deferred_until_owner_verifies_complete_english"]))

    def test_no_non_english_work_or_locale_repositories_before_owner_approval(self):
        p=self.policy
        self.assertIs(p["other_target_language_translation_development_allowed_before_owner_verification"],False)
        self.assertIs(p["non_english_language_repo_creation_for_translation_allowed_before_owner_verification"],False)
        self.assertIs(p["non_english_bible_translation_generation_allowed_before_owner_verification"],False)
        self.assertEqual(p["status_of_existing_non_english_locale_profiles"],
                         "HISTORICAL_SCHEMA_STUBS_ONLY_NO_TRANSLATION_WORK")
        self.assertEqual(p["existing_multilingual_architecture"],"DEFERRED_NOT_DELETED")
        self.assertFalse(p["english_complete_bible_owner_verification_status"] != "NOT_DONE")
        self.assertEqual(p["source_to_english_final_complete_translation_status"],"NOT_DONE")
        self.assertEqual(p["english_source_first_translation_engine_prototype_status"],"NOT_DONE")
        self.assertEqual(p["bible_publication_status"],"BLOCKED")

    def test_owner_must_verify_whole_english_bible_not_ci_or_partial_work(self):
        p=self.policy
        self.assertIs(p["owner_verification_must_be_explicit"],True)
        self.assertIs(p["verification_must_cover_complete_original_to_english_bible"],True)
        self.assertIs(p["github_ci_can_replace_owner_bible_approval"],False)
        self.assertIs(p["artificial_owner_approval_by_automation_forbidden"],True)
        self.assertIs(p["independent_philological_review_gates_still_apply"],True)
        self.assertIs(p["historical_source_corpus_research_kept"],True)
        self.assertIs(p["english_verse_research_drafts_may_be_generated_before_full_owner_verification"],True)
        self.assertIs(p["english_verse_drafts_are_not_final_owner_approved_translation"],True)
        self.assertTrue(p["next_implementation_priority"][0].startswith(
            "Build an actual runnable source-to-English OLT translation prototype"))

    def test_binding_owner_policy_visible_to_future_sessions_and_architecture(self):
        self.assertTrue(DOC.is_file())
        self.assertTrue(STATUS.is_file())
        status=STATUS.read_text(encoding="utf-8")
        self.assertIn("OLT-ENGLISH-FIRST-001",status[:1900])
        self.assertIn("sole active target language is ENGLISH",status[:2000])
        self.assertIn("Complete 66-book English translation: NOT DONE",status[:2600])
        self.assertIn("Owner approval: NOT DONE",status[:2600])
        self.assertIn("Scripture publication: BLOCKED",status[:2600])
        self.assertIn("OLT_ENGLISH_FIRST_OWNER_GATE.md",status[:2600])
        self.assertIn("English is the only current translation target",
                      ARCH.read_text(encoding="utf-8")[:900])
        readme=README.read_text(encoding="utf-8")[:1200]
        self.assertIn("English only",readme)
        self.assertIn("Japanese, Amharic",readme)
        text=DOC.read_text(encoding="utf-8")
        self.assertIn("all 66 canonical books",text)
        self.assertIn("personally verify",text)
        self.assertIn("wayyiqtol",text)
        self.assertIn("BLOCKED",text)


if __name__=="__main__":
    unittest.main()
