import copy,unittest,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from research_underwords import attach_underwords,render_linked_verse,underword_note_definitions
from audit_full_genesis_research import audit,load,DIR,INPUTS,SOURCE,preview
OVERRIDE=ROOT/"data/policy/olt_underword_overrides.json"

class TestOLT022(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=load(SOURCE)
  cls.parts=[load(DIR/p) for p in INPUTS]
  cls.policy=load(OVERRIDE)
 def make(self,config=None):
  return audit(self.source,self.parts,underword_config=config if config is not None else self.policy)
 def test_only_one_vertical_link_source_anchored(self):
  r=self.make()
  self.assertEqual(r["source_verses"],31)
  self.assertEqual(r["original_source_word_tokens"],434)
  self.assertEqual(r["source_tagged_wayyiqtol_count"],50)
  self.assertEqual(r["underword_links_count"],1)
  self.assertEqual(r["actual_homonym_identity_links_approved"],0)
  self.assertEqual(r["authoritatively_approved_english_verses"],0)
  self.assertEqual(r["publication_status"],"BLOCKED")
  self.assertEqual(len(r["underword_manifest"]),1)
  u=r["underword_manifest"][0]
  self.assertEqual((u["reference"],u["source_token_id"],u["primary"],u["secondary"]),
                   ("Gen.1.1","01xeN","In","with"))
  self.assertTrue(u["owner_display_approved"])
  self.assertFalse(u["instrumental_claim_confirmed"])
  self.assertFalse(u["source_lexical_jesus_claim"])
  self.assertEqual([len(v.get("underword_proposals",[])) for v in r["genesis_1_research_verses"]],[1]+[0]*30)
 def test_github_preview_displays_word_exactly_under_in(self):
  r=self.make()
  md=preview(r)
  self.assertIn("| **In**<br><sub>with</sub>[^gen-1-1-bet-with] | the Beginning [of His Power][^gen-1-1-power]",md)
  self.assertEqual(md.count("<sub>with</sub>"),1)
  self.assertNotIn("In/with",md)
  self.assertEqual(md.count("[^gen-1-1-bet-with]:"),1)
  self.assertEqual(md.count("[^gen-1-1-power]:"),1)
  self.assertEqual(r["research_footnotes_count"],1)
  self.assertEqual(r["genesis_1_research_verses"][0]["proposed_english_research_text"],
                   "In the Beginning [of His Power] God — He shaped the Heavens and the Earth.")
 def test_reject_global_replacement(self):
  p=copy.deepcopy(self.policy);p["automatically_generalize_to_other_bet"]=True
  with self.assertRaisesRegex(ValueError,"global in/with"):self.make(p)
 def test_reject_false_instrumental_confirmation(self):
  p=copy.deepcopy(self.policy)
  p["underwords"][0]["this_verse_instrumental_bet_independently_established"]=True
  with self.assertRaisesRegex(ValueError,"unsupported original-language fact"):self.make(p)
 def test_reject_homonym_certification(self):
  p=copy.deepcopy(self.policy);p["underwords"][0]["underword_is_verified_homonym"]=True
  with self.assertRaisesRegex(ValueError,"unsupported original-language fact"):self.make(p)
 def test_reject_wrong_source_word(self):
  p=copy.deepcopy(self.policy);p["underwords"][0]["source_token_id"]="01Nvk"
  with self.assertRaisesRegex(ValueError,"exact original Hebrew source anchor"):self.make(p)
 def test_reject_wrong_verse(self):
  p=copy.deepcopy(self.policy);p["underwords"][0]["reference"]="Gen.1.2"
  with self.assertRaisesRegex(ValueError,"another verse"):self.make(p)
 def test_reject_reversed_or_inline_words(self):
  p=copy.deepcopy(self.policy);p["underwords"][0]["secondary_english"]="In/with"
  with self.assertRaisesRegex(ValueError,"In over with"):self.make(p)
 def test_reject_missing_theological_disclaimer(self):
  p=copy.deepcopy(self.policy)
  p["underwords"][0]["footnote"]["english"]="with is the literal Hebrew lexeme and Jesus."
  with self.assertRaisesRegex(ValueError,"essential evidence boundary"):self.make(p)
 def test_reject_missing_scholarly_evidence(self):
  p=copy.deepcopy(self.policy);p["underwords"][0]["footnote"]["evidence"]=[]
  with self.assertRaisesRegex(ValueError,"external scholarly evidence"):self.make(p)
 def test_reject_false_publication(self):
  p=copy.deepcopy(self.policy);p["publication_status"]="PUBLISHED"
  with self.assertRaisesRegex(ValueError,"falsely marked published"):self.make(p)

if __name__=="__main__":
 unittest.main()
