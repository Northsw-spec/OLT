import sys,unittest,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"scripts"))
from genesis_06_10_research import build,source,specs,VERSES,NOTES
class TestGenesis010(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.src=source(R/"data/quality/genesis_01_source_review_dossier.json")
  cls.cards=source(R/"data/quality/genesis_01_dictionary_study_cards.json")
  cls.seed=source(R/"lexicon/hebrew.json")
 def runcheck(self,d=None,c=None,o=None,p=None,t=None,n=None):
  return build(d or self.src,c or self.cards,o or self.seed,
      plans=p,texts=t,notes=n)
 def test_all_63_token_source_scope_and_wayyiqtol(self):
  z=self.runcheck()
  self.assertEqual(z["token_count"],63)
  self.assertEqual(z["wayyiqtol_count"],11)
  self.assertEqual([v["source_token_count"] for v in z["verses"]],[11,17,10,13,12])
  self.assertEqual(len({a["source_token_id"] for v in z["verses"] for a in v["source_tokens"]}),63)
  self.assertEqual(z["chapter_publication"],"BLOCKED")
 def test_corrupted_source_id_or_order_fails(self):
  d=copy.deepcopy(self.src)
  x=next(a for a in d["tokens"] if a["source_token_id"]=="01fsu")
  x["source_token_id"]="invented"
  with self.assertRaisesRegex(ValueError,"Original source"):self.runcheck(d=d)
 def test_wrong_original_morphology_fails(self):
  d=copy.deepcopy(self.src)
  next(a for a in d["tokens"] if a["source_token_id"]=="01NPq")["source_morphology_raw"]="HC/Vqw3mp"
  with self.assertRaisesRegex(ValueError,"Original source"):self.runcheck(d=d)
 def test_misclassified_jussive_fails(self):
  p=copy.deepcopy(specs());p["Gen.1.9"][2]["morph"]="HVNi3mp"
  with self.assertRaisesRegex(ValueError,"Original source"):self.runcheck(p=p)
 def test_yiqqawu_is_not_wayyiqtol(self):
  z=self.runcheck()
  e=z["verses"][3]["source_tokens"][2]
  self.assertEqual(e["source_verb_form_code"],"j")
  self.assertFalse(e["source_tagged_wayyiqtol"])
 def test_veteraeh_not_wayyiqtol(self):
  z=self.runcheck()
  e=z["verses"][3]["source_tokens"][9]
  self.assertEqual(e["source_verb_form_code"],"i")
 def test_owner_lock_make_never_shape(self):
  p=copy.deepcopy(specs());p["Gen.1.7"][0]["gloss"]="And He shaped"
  with self.assertRaisesRegex(ValueError,"Owner-lock asah"):self.runcheck(p=p)
 def test_owner_lock_firmament_never_expansion(self):
  p=copy.deepcopy(specs());p["Gen.1.6"][3]["gloss"]="an expanse"
  with self.assertRaisesRegex(ValueError,"Owner-lock raqia"):self.runcheck(p=p)
 def test_source_object_marker_zero_english(self):
  p=copy.deepcopy(specs());p["Gen.1.7"][2]["gloss"]="the"
  with self.assertRaisesRegex(ValueError,"direct-object marker"):self.runcheck(p=p)
 def test_past_wayyiqtol_tense(self):
  p=copy.deepcopy(specs());p["Gen.1.7"][0]["gloss"]="And He has made"
  with self.assertRaisesRegex(ValueError,"perfect/future"):self.runcheck(p=p)
 def test_english_neuter_banned(self):
  m=dict(VERSES);m["Gen.1.9"]="And God — He said, and it was so."
  with self.assertRaisesRegex(ValueError,"Neutral English"):self.runcheck(t=m)
 def test_gender_editorial_supplement_not_false_homonym(self):
  notes=copy.deepcopy(NOTES);next(x for x in notes if x["type"]=="HOMONYM_CAUTION")["status"]="OWNER_LOCK"
  with self.assertRaisesRegex(ValueError,"homonym wrongly"):self.runcheck(n=notes)
 def test_owner_seed_tamper_fails(self):
  d=copy.deepcopy(self.seed);next(x for x in d["entries"] if x["id"]=="raqia")["english_base"]="expanse"
  with self.assertRaisesRegex(ValueError,"owner English-family locks"):self.runcheck(o=d)
 def test_missing_verse_fails(self):
  p=copy.deepcopy(specs());del p["Gen.1.8"]
  with self.assertRaisesRegex(ValueError,"Wrong verse coverage"):self.runcheck(p=p)
if __name__=="__main__":unittest.main()
