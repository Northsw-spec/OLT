"""OLT-034 static schema and version-contract checks for external target-language repos."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from olt_core import ENGINE_VERSION,CONTRACT_VERSION

def load(relative):
    return json.loads((ROOT/relative).read_text(encoding="utf-8"))

class TestOLT034Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arch=load("data/engine/olt_034_architecture.json")
        cls.manifest=load("lexicon/english_master_manifest.json")
        cls.source=load("schemas/olt_034_source_record.schema.json")
        cls.locale=load("schemas/olt_034_locale_profile.schema.json")
        cls.lex=load("lexicon/hebrew.json")

    def test_json_schema_versions_and_original_source_anchors(self):
        for s in (self.source,self.locale):
            self.assertEqual(s["$schema"],"https://json-schema.org/draft/2020-12/schema")
        for field in ("verse_id","token_id","original_script","lemma_id","raw_morphology",
                      "source_language","corpus","edition_id","edition_status"):
            self.assertIn(field,self.source["required"])
        self.assertEqual(self.source["properties"]["source_language"]["enum"],["hbo","arc","grc"])
        self.assertEqual(self.source["properties"]["publication_status"]["const"],"BLOCKED")

    def test_language_profile_contract_has_no_english_pivot(self):
        for field in ("language_tag","script","direction","source_first",
                      "english_is_reference_only","token_choices","publication_status"):
            self.assertIn(field,self.locale["required"])
        self.assertTrue(self.locale["properties"]["source_first"]["const"])
        self.assertTrue(self.locale["properties"]["english_is_reference_only"]["const"])
        self.assertEqual(self.locale["properties"]["publication_status"]["const"],"BLOCKED")

    def test_source_lexical_seed_points_to_reference_manifest_not_pivot(self):
        self.assertEqual(self.lex["english_master_manifest"],"lexicon/english_master_manifest.json")
        self.assertTrue(self.lex["english_is_locale_reference_only"])
        self.assertEqual(self.lex["olt_shared_core"],"olt_core")
        self.assertEqual(self.lex["other_language_translation_input"],
                         "ORIGINAL_LANGUAGE_SOURCE_IDENTITIES_NOT_ENGLISH_SURFACES")
        self.assertEqual(len(self.lex["entries"]),15)

    def test_english_master_references_canonical_existing_data_and_owner_locks(self):
        m=self.manifest
        for path_field in ("lexical_entry_source","name_meaning_source",
                           "genesis_1_verse_01_original_aligned_reference",
                           "genesis_1_31_verse_research_reference"):
            self.assertTrue((ROOT/m[path_field]).is_file(),path_field)
        owners={x["id"]:x["english_base"] for x in self.lex["entries"] if x["status"]=="OWNER_LOCKED"}
        self.assertEqual(owners,m["owner_locked_hebrew_english_families"])
        self.assertEqual(m["owner_requested_name_meaning_examples"]["God/Elohim"],"Mighty Governance")
        self.assertEqual(m["owner_requested_name_meaning_examples"]["Noah"],"Rest")
        self.assertFalse(m["all_ot_english_master_lexicon_complete"])
        self.assertFalse(m["nt_greek_master_lexicon_complete"])

    def test_engine_package_and_contract_release_state(self):
        self.assertEqual(ENGINE_VERSION,"0.1.0")
        self.assertEqual(CONTRACT_VERSION,"1.0")
        self.assertEqual(self.arch["reusable_package"],"olt_core")
        self.assertEqual(self.arch["bible_release_status"],"BLOCKED")
        self.assertFalse(self.arch["english_reference_may_fall_back_to_target_translation"])
        self.assertFalse(self.arch["target_repositories_created_by_this_checkpoint"])

if __name__=="__main__":
    unittest.main()
