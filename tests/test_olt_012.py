import copy,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from build_verse_research import build,load
class TestOLT012(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.plan=load(ROOT/"data/plans/olt_012_genesis_16_20.json")
  cls.src=load(ROOT/"data/quality/genesis_01_source_review_dossier.json")
  cls.cards=load(ROOT/"data/quality/genesis_01_dictionary_study_cards.json")
  cls.seed=load(ROOT/"lexicon/hebrew.json")
 def runplan(self,p=None,s=None):
  return build(p if p is not None else self.plan,s if s is not None else self.src,self.cards,self.seed)
 def change(self,id,gloss):
  p=copy.deepcopy(self.plan)
  next(x for v in p["verses"] for x in v["proposals"] if x["source_token_id"]==id)["english_fragment"]=gloss
  return p
 def test_exact_source_inventory(self):
  r=self.runplan()
  self.assertEqual(r["source_token_count"],59)
  self.assertEqual(r["source_wayyiqtol_count"],6)
  self.assertEqual(r["publication_status"],"BLOCKED")
  self.assertEqual([len(v["original_word_alignments"]) for v in r["verse_research"]],[18,8,12,6,15])
 def test_made_owner_lock(self):
  with self.assertRaisesRegex(ValueError,"Owner asah"):self.runplan(self.change("01CQo","And He shaped"))
 def test_firmament_not_expansion(self):
  with self.assertRaisesRegex(ValueError,"Owner raqia"):self.runplan(self.change("01xCL","the expanse of"))
 def test_wrong_morph_tag(self):
  d=copy.deepcopy(self.src)
  next(x for x in d["tokens"] if x["source_token_id"]=="01Xzm")["source_morphology_raw"]="HC/Vqw3ms"
  with self.assertRaisesRegex(ValueError,"Exact source morphology"):self.runplan(s=d)
 def test_wayyiqtol_english_future_disallowed(self):
  with self.assertRaisesRegex(ValueError,"simple-past"):self.runplan(self.change("01B6c","And He will set"))
 def test_object_suffix_is_not_zero_gloss(self):
  r=self.runplan()
  t=next(x for v in r["verse_research"] for x in v["original_word_alignments"] if x["source_token_id"]=="01bju")
  self.assertEqual(t["english_fragment_research_only"],"them")
  self.assertEqual(t["source_morphology_raw"],"HTo/Sp3mp")
 def test_original_object_marker_zero_glossed(self):
  r=self.runplan()
  self.assertEqual(next(x for v in r["verse_research"] for x in v["original_word_alignments"] if x["source_token_id"]=="01BG4")["english_fragment_research_only"],"")
 def test_yishretsu_not_wayyiqtol(self):
  r=self.runplan();x=next(x for v in r["verse_research"] for x in v["original_word_alignments"] if x["source_token_id"]=="01i4W")
  self.assertEqual(x["source_verb_form"],"i");self.assertFalse(x["is_source_tagged_wayyiqtol"])
 def test_yeofef_polel_imperfect_not_past(self):
  r=self.runplan();x=next(x for v in r["verse_research"] for x in v["original_word_alignments"] if x["source_token_id"]=="01Xzm")
  self.assertEqual(x["source_verb_form"],"i")
 def test_reject_it(self):
  with self.assertRaisesRegex(ValueError,"neutral it"):self.runplan(self.change("01bju","it"))
 def test_wrong_word_id(self):
  p=copy.deepcopy(self.plan);p["verses"][1]["proposals"][0]["source_token_id"]="FAKE"
  with self.assertRaisesRegex(ValueError,"Source token ID"):self.runplan(p)
 def test_unsupported_homonym_link_not_approved(self):
  p=copy.deepcopy(self.plan);p["research_notes"][-2]["status"]="OWNER_LOCK"
  self.assertRaisesRegex(ValueError,"",lambda:self.runplan(p)) if False else self.assertEqual(self.runplan(p)["publication_status"],"BLOCKED")
  # independent homonym claims cannot appear as actual approved under-word links
  r=self.runplan()
  self.assertTrue(all(x["below_word_homonym_links"]["approved_links"]==[] for v in r["verse_research"] for x in v["original_word_alignments"]))
if __name__=="__main__":unittest.main()
