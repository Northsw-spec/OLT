import copy,unittest,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"scripts"))
from build_verse_research import load,build
class OLT013(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.plan=load(R/"data/plans/olt_013_genesis_21_25.json")
  cls.src=load(R/"data/quality/genesis_01_source_review_dossier.json")
  cls.cards=load(R/"data/quality/genesis_01_dictionary_study_cards.json")
  cls.seed=load(R/"lexicon/hebrew.json")
 def make(self,p=None,s=None):
  return build(self.plan if p is None else p,self.src if s is None else s,self.cards,self.seed)
 def edit(self,id,gloss):
  p=copy.deepcopy(self.plan)
  next(x for v in p["verses"] for x in v["proposals"] if x["source_token_id"]==id)["english_fragment"]=gloss
  return p
 def test_scope(self):
  z=self.make()
  self.assertEqual(z["source_token_count"],74);self.assertEqual(z["source_wayyiqtol_count"],9)
  self.assertEqual([len(v["original_word_alignments"]) for v in z["verse_research"]],[23,13,6,14,18])
  self.assertEqual(z["publication_status"],"BLOCKED")
 def test_bara_lock(self):
  with self.assertRaisesRegex(ValueError,"Owner bara"):self.make(self.edit("016kU","And He created"))
 def test_asah_lock(self):
  with self.assertRaisesRegex(ValueError,"Owner asah"):self.make(self.edit("01ZpQ","And He shaped"))
 def test_wrong_source_id(self):
  p=copy.deepcopy(self.plan);p["verses"][0]["proposals"][3]["source_token_id"]="invented"
  with self.assertRaisesRegex(ValueError,"Source token ID"):self.make(p)
 def test_jussive_is_not_wayyiqtol(self):
  r=self.make()
  x=next(y for v in r["verse_research"] for y in v["original_word_alignments"] if y["source_token_id"]=="018GY")
  self.assertFalse(x["is_source_tagged_wayyiqtol"]);self.assertEqual(x["source_verb_form"],"j")
 def test_imperative_is_not_wayyiqtol(self):
  r=self.make(); x=next(y for v in r["verse_research"] for y in v["original_word_alignments"] if y["source_token_id"]=="01DDb")
  self.assertFalse(x["is_source_tagged_wayyiqtol"]);self.assertEqual(x["source_verb_form"],"v")
 def test_hbr_object_suffix(self):
  r=self.make();x=next(y for v in r["verse_research"] for y in v["original_word_alignments"] if y["source_token_id"]=="0163G")
  self.assertEqual(x["english_fragment_research_only"],"them")
 def test_hbr_root_metadata_change_fails(self):
  s=copy.deepcopy(self.src)
  next(x for x in s["tokens"] if x["source_token_id"]=="01ZpQ")["source_lemma_raw"]="c/1254 a"
  with self.assertRaisesRegex(ValueError,"Exact source lemma"):self.make(s=s)
 def test_no_it_in_main_text(self):
  p=copy.deepcopy(self.plan);p["verses"][1]["english_research_draft"]="And it was so."
  with self.assertRaisesRegex(ValueError,"neutral it"):self.make(p)
 def test_christological_interpretation_not_verified_homonym(self):
  p=copy.deepcopy(self.plan);p["research_notes"][-1]["status"]="PUBLISHED"
  with self.assertRaisesRegex(ValueError,"Claimed certainty"):self.make(p)
 def test_prevent_false_release(self):
  p=copy.deepcopy(self.plan);p["status"]="APPROVED"
  with self.assertRaisesRegex(ValueError,"self-approve"):self.make(p)
if __name__=="__main__":unittest.main()
