import sys,copy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from genesis_02_05_research import make,parse,MAIN,NOTES
import json
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads((ROOT/"data/quality/genesis_01_source_review_dossier.json").read_text())
  cls.cards=json.loads((ROOT/"data/quality/genesis_01_dictionary_study_cards.json").read_text())
 def check(self,source=None,plan=None,main=None,notes=None):
  return make(self.source if source is None else source,self.cards,plan,main,notes)
 def test_full_45_token_scope(self):
  d=self.check()
  self.assertEqual(d["source_token_count"],45)
  self.assertEqual(d["source_tagged_wayyiqtol_count"],7)
  self.assertEqual([v["source_word_count"] for v in d["verses"]],[14,6,12,13])
  self.assertEqual(d["release_status"],"BLOCKED")
  self.assertEqual(len({x["source_token_id"] for v in d["verses"] for x in v["source_aligned_tokens"]}),45)
 def test_bad_source_id_is_rejected(self):
  s=copy.deepcopy(self.source)
  next(x for x in s["tokens"] if x["source_token_id"]=="01USR")["source_token_id"]="invented"
  with self.assertRaisesRegex(ValueError,"Source token"):self.check(source=s)
 def test_bad_source_morphology_is_rejected(self):
  s=copy.deepcopy(self.source)
  next(x for x in s["tokens"] if x["source_token_id"]=="01LeN")["source_morphology_raw"]="HC/Vqw3ms"
  with self.assertRaisesRegex(ValueError,"Source token"):self.check(source=s)
 def test_verb_wrong_tense_is_rejected(self):
  p=copy.deepcopy(parse());p["Gen.1.5"][0]["gloss"]="And has called"
  with self.assertRaisesRegex(ValueError,"Wayyiqtol"):self.check(plan=p)
 def test_verb_jussive_must_not_be_past(self):
  s=copy.deepcopy(self.source)
  next(x for x in s["tokens"] if x["source_token_id"]=="01fpo")["source_tagged_wayyiqtol"]=True
  with self.assertRaisesRegex(ValueError,"Jussive"):self.check(source=s)
 def test_participle_must_not_be_past(self):
  s=copy.deepcopy(self.source)
  next(x for x in s["tokens"] if x["source_token_id"]=="01yNB")["source_tagged_wayyiqtol"]=True
  with self.assertRaisesRegex(ValueError,"Piel"):self.check(source=s)
 def test_main_text_it_is_rejected(self):
  m=dict(MAIN);m["Gen.1.2"]="And it was."
  with self.assertRaisesRegex(ValueError,"Neutral it"):self.check(main=m)
 def test_exact_gen_1_4_clause_is_locked(self):
  m=dict(MAIN);m["Gen.1.4"]=m["Gen.1.4"].replace("that [he was]","that was")
  with self.assertRaisesRegex(ValueError,"owner-approved"):self.check(main=m)
 def test_object_marker_must_have_zero_english(self):
  p=copy.deepcopy(parse());p["Gen.1.4"][2]["gloss"]="it"
  with self.assertRaisesRegex(ValueError,"Object marker"):self.check(plan=p)
 def test_christological_link_cannot_be_lexical_approval(self):
  notes=copy.deepcopy(NOTES);next(n for n in notes if n["type"]=="TYPOLOGY_RESEARCH_CANDIDATE")["status"]="VERIFIED_HOMONYM"
  with self.assertRaisesRegex(ValueError,"Typology falsely"):self.check(notes=notes)
if __name__=="__main__":unittest.main()
