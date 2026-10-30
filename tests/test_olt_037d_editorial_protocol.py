"""OLT-037D: ensure source-only review forms never impersonate human approval."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from olt_core.engine import SourceContractError
from olt_core.greek_editorial_review import (
    CHECKPOINT, SOURCE_REVIEW_REQUIREMENTS, TEMPLATE_PATH,
    make_review_templates, serialize_templates, validate_unreviewed_draft,
    verify_frozen_templates,
)


class TestGreekEditorialProtocol(unittest.TestCase):
    def test_empty_evidence_forms_have_correct_real_original_source_identifiers(self):
        t=make_review_templates()
        self.assertEqual(t["checkpoint"],CHECKPOINT)
        self.assertEqual(t["expert_reviews_performed"],0)
        self.assertEqual(t["publication_status"],"BLOCKED")
        self.assertEqual(len(t["review_case_templates"]),2)
        a,b=t["review_case_templates"]
        self.assertEqual(a["original_rp2018_editor_numeric_reference"],"3004")
        self.assertEqual(b["original_rp2018_editor_numeric_reference"],"3754")
        self.assertEqual(a["original_occurrence_count"],2315)
        self.assertEqual(b["original_occurrence_count"],1287)
        self.assertEqual(a["native_lsj_entry_ids_unreviewed"],["n62204","n62205"])
        self.assertEqual(b["native_lsj_entry_keys_unreviewed"],[])
        self.assertFalse(a["independent_philological_signoff"])
        self.assertFalse(b["owner_editorial_approval"])
        validate_unreviewed_draft(t)
        self.assertEqual(len(SOURCE_REVIEW_REQUIREMENTS),7)
        self.assertTrue(any("Koine" in s for s in SOURCE_REVIEW_REQUIREMENTS))

    def test_fake_or_claimed_human_approval_fails_closed(self):
        original=make_review_templates()
        for field,value in [
            ("research_state","APPROVED"),
            ("proposed_dictionary_lemma","λέγω"),
            ("proposed_lexical_sense","invented chosen meaning"),
            ("proposed_english_gloss_NOT_OLT_TRANSLATION","say"),
            ("independently_quoted_or_cited_lexicon_sources",["fake"]),
            ("additional_koine_lexicon_sources_checked",["uncited claim"]),
            ("primary_greek_context_argument","I decided."),
            ("morphology_cross_review","verified"),
            ("independent_reviewer_identifier","fictional reviewer"),
            ("independent_reviewer_date","2026-10-31"),
            ("independent_philological_signoff",True),
            ("owner_editorial_approval",True),
            ("target_language_translation_generated",True),
            ("publication_status","PUBLISHED"),
        ]:
            with self.subTest(field=field):
                tampered=deepcopy(original)
                tampered["review_case_templates"][0][field]=value
                with self.assertRaises(SourceContractError):
                    validate_unreviewed_draft(tampered)

    def test_summary_approval_and_missing_cases_cannot_pass(self):
        src=make_review_templates()
        changes=[
            dict(src,expert_reviews_performed=1),
            dict(src,automatic_lexical_sense_decisions=1),
            dict(src,owner_approved_english_master_entries=1),
            dict(src,publication_status="PUBLISHED"),
            dict(src,review_case_templates=[]),
            dict(src,checkpoint="OLT-037E"),
        ]
        for modified in changes:
            with self.assertRaises(SourceContractError):
                validate_unreviewed_draft(modified)

    def test_json_generation_exact_and_frozen_file_required(self):
        value=make_review_templates()
        txt=serialize_templates(value)
        self.assertEqual(json.loads(txt),value)
        self.assertTrue(txt.endswith("\n"))
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            # The generated forms require immutable source files; a temporary
            # empty folder must fail to manufacture them from memory.
            with self.assertRaises((SourceContractError,FileNotFoundError)):
                verify_frozen_templates(root)

    def test_complete_canonical_templates_match_verified_sources(self):
        p=ROOT/TEMPLATE_PATH
        if not p.exists():
            self.skipTest("Initial source CI creates the exact locked reviewer form")
        t=verify_frozen_templates()
        self.assertEqual(t["independent_lsj_license"],"CC BY-SA 4.0")
        self.assertEqual(t["stepbible_data_license"],"CC BY 4.0")
        self.assertEqual(t["expert_reviews_performed"],0)
        self.assertEqual(t["owner_approved_english_master_entries"],0)


if __name__=="__main__":
    unittest.main()
