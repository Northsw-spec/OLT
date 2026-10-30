"""OLT-031: the 42 multi-fragment source lemmas are questions, NOT approved homonyms."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_olt_031_variation_triage import build, render, EDITORIAL, WAVE_A, WAVE_B, OUTPUT


class OLT031(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editorial = json.loads(EDITORIAL.read_text(encoding="utf-8"))
        cls.a = json.loads(WAVE_A.read_text(encoding="utf-8"))
        cls.b = json.loads(WAVE_B.read_text(encoding="utf-8"))
        cls.packet = build(cls.editorial, cls.a, cls.b)

    def test_exactly_reproduces_committed_42_case_packet(self):
        self.assertEqual(render(self.packet), OUTPUT.read_text(encoding="utf-8"))

    def test_original_hebrew_and_lemma_coverage_is_accounted_for(self):
        p = self.packet
        self.assertEqual((p["original_hebrew_verse_count"], p["original_hebrew_word_tokens"]), (31, 434))
        self.assertEqual((p["source_tokens_with_numeric_lemma"], p["source_tokens_without_numeric_lemma"]), (427, 7))
        self.assertEqual((p["exact_source_lemma_ids"], p["source_lemmas_with_multiple_unapproved_fragments"]), (97, 42))
        self.assertEqual(p["source_lemmas_with_one_unapproved_fragment"], 55)
        self.assertEqual(len(p["cases"]), 42)

    def test_each_research_variation_preserves_real_token_and_imported_morphology(self):
        by_lemma = {e["source_lemma_id"]: e for e in self.editorial["entries"]}
        seen = set()
        for case in self.packet["cases"]:
            source = by_lemma[case["source_lemma_id"]]
            self.assertEqual(case["research_fragments_exact"], source["proposed_english_fragments"])
            self.assertEqual(case["source_token_count"], len(source["source_words"]))
            self.assertEqual(len(case["distinct_imported_morphology_tags"]),
                             len({x["raw_morphology"] for x in source["source_words"]}))
            for original, copied in zip(source["source_words"], case["original_source_contexts"], strict=True):
                self.assertEqual(
                    (copied["source_token_id"], copied["verse"], copied["pointed_hebrew"],
                     copied["imported_morphology"], copied["unapproved_english_fragment"]),
                    (original["token_id"], original["reference"], original["hebrew"],
                     original["raw_morphology"], original["english_research_fragment"]),
                )
                self.assertNotIn(copied["source_token_id"], seen)
                seen.add(copied["source_token_id"])
        self.assertEqual(len(seen), 322)

    def test_morphology_differences_never_auto_certify_semantic_homonyms(self):
        self.assertEqual(self.packet["new_english_lexical_approvals"], 0)
        self.assertEqual(self.packet["new_independent_morphology_approvals"], 0)
        self.assertEqual(self.packet["approved_homonym_links"], 0)
        self.assertTrue(self.packet["fragments_are_not_proof_of_lexical_homonymy"])
        self.assertEqual(self.packet["publication_status"], "BLOCKED")
        for case in self.packet["cases"]:
            self.assertEqual(case["english_variation_cause"], "NOT_INDEPENDENTLY_DETERMINED")
            self.assertEqual(case["hebrew_homonym_identity"], "NOT_VERIFIED")
            self.assertEqual(case["editorial_status"], "REVIEW_REQUIRED")

    def test_1961_jussive_and_wayyiqtol_source_tags_are_not_conflated(self):
        case = next(c for c in self.packet["cases"] if c["source_lemma_id"] == "1961")
        self.assertIn("HVqj3ms", case["distinct_imported_morphology_tags"])
        self.assertIn("HC/Vqw3ms", case["distinct_imported_morphology_tags"])
        self.assertEqual(case["hebrew_homonym_identity"], "NOT_VERIFIED")

    def test_owner_lexical_families_not_replaced(self):
        owners = {c["source_lemma_id"]: c["owner_locked_english_family"]
                  for c in self.packet["cases"] if c["owner_locked_english_family"] is not None}
        self.assertEqual(owners, {"1254 a": "shape", "6213 a": "make", "7549": "firmament"})

    def test_reject_global_false_publication(self):
        edited = copy.deepcopy(self.editorial)
        edited["publication_status"] = "PUBLISHED"
        with self.assertRaisesRegex(ValueError, "firewall"):
            build(edited, self.a, self.b)

    def test_reject_unauthorized_english_approval(self):
        edited = copy.deepcopy(self.editorial)
        edited["entries"][0]["english_family_approval"] = "APPROVED"
        with self.assertRaisesRegex(ValueError, "silently approved"):
            build(edited, self.a, self.b)

    def test_reject_homonym_claim_from_visual_variation(self):
        edited = copy.deepcopy(self.editorial)
        edited["entries"][0]["homonym_identity_approved"] = True
        with self.assertRaisesRegex(ValueError, "homonym"):
            build(edited, self.a, self.b)

    def test_reject_lost_original_word(self):
        edited = copy.deepcopy(self.editorial)
        edited["entries"][0]["source_words"].pop()
        with self.assertRaisesRegex(ValueError, "count differs"):
            build(edited, self.a, self.b)

    def test_reject_wrong_owner_locked_english(self):
        edited = copy.deepcopy(self.editorial)
        owner = next(e for e in edited["entries"] if e["source_lemma_id"] == "1254 a")
        owner["owner_english_family"] = "create"
        with self.assertRaisesRegex(ValueError, "Owner-locked"):
            build(edited, self.a, self.b)

    def test_reject_false_scholarly_signoff(self):
        edited = copy.deepcopy(self.a)
        edited["approved_homonym_links"] = 1
        with self.assertRaisesRegex(ValueError, "Prior scholarly dossier"):
            build(self.editorial, edited, self.b)


if __name__ == "__main__":
    unittest.main()
