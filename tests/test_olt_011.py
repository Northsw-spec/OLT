import unittest,copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_verse_research import build,load
class TestOLT011(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=load(ROOT/"data/plans/olt_011_genesis_11_15.json")
  cls.src=load(ROOT/"data/quality/genesis_01_source_review_dossier.json")
  cls.cards=load(ROOT/"data/quality/genesis_01_dictionary_study_cards.json")
  cls.seed=load(ROOT/"lexicon/hebrew.json")
 def make(self,p=None,src=None,seed=None):
  return build(p if p is not None else self.p,src if src is not None else self.src,self.cards,seed if seed is not None else self.seed)
 def edit(self,id,gloss=None,**props):
  p=copy.deepcopy(self.p)
  t=next(z for v in p["verses"] for z in v["proposals"] if z["source_token_id"]==id)
  if gloss is not None:t["english_fragment"]=gloss
  t.update(props)
  return p
 def test_exact_scope_and_no_false_pass(self):
  x=self.make()
  self.assertEqual(x["source_token_count"],69)
  self.assertEqual(x["source_wayyiqtol_count"],8)
  self.assertEqual(sorted(x["non_numeric_grammar_token_ids"]),["01J9J","01SV6"])
  self.assertEqual(x["publication_status"],"BLOCKED")
  self.assertFalse(x["full_english_lexicon_approved"])
  self.assertEqual(x["under_word_homonym_presentation"],"UNDER_ENGLISH_WORD")
  self.assertTrue(all(not w["english_lexical_approval"] for v in x["verse_research"] for w in v["original_word_alignments"]))
 def test_missing_original_token_fails(self):
  p=copy.deepcopy(self.p);p["verses"][0]["proposals"].pop()
  with self.assertRaisesRegex(ValueError,"count differs"):self.make(p)
 def test_wrong_original_id_fails(self):
  p=copy.deepcopy(self.p);p["verses"][0]["proposals"][0]["source_token_id"]="FAKE"
  with self.assertRaisesRegex(ValueError,"Source token ID"):self.make(p)
 def test_source_morphology_fails(self):
  s=copy.deepcopy(self.src)
  next(x for x in s["tokens"] if x["source_token_id"]=="01btu")["source_morphology_raw"]="HC/Vqw3cp"
  with self.assertRaisesRegex(ValueError,"Exact source morphology"):self.make(src=s)
 def test_sequential_perfect_is_not_wayyiqtol(self):
  x=self.make()
  t=next(w for v in x["verse_research"] for w in v["original_word_alignments"] if w["source_token_id"]=="01btu")
  self.assertEqual(t["source_verb_form"],"q");self.assertFalse(t["is_source_tagged_wayyiqtol"])
 def test_owner_make_participle_never_shape(self):
  with self.assertRaisesRegex(ValueError,"Owner asah"):self.make(self.edit("01V27","shaping"))
 def test_firmament_source_lemma_lock(self):
  with self.assertRaisesRegex(ValueError,"Owner raqia"):self.make(self.edit("01FiN","in the expanse of"))
 def test_conjunction_waw_cannot_be_dropped(self):
  with self.assertRaisesRegex(ValueError,"conjunction was dropped"):self.make(self.edit("01AxB","He said"))
 def test_neutral_it_forbidden(self):
  with self.assertRaisesRegex(ValueError,"neutral it"):self.make(self.edit("01SV6","in it"))
 def test_homonyms_cannot_be_inline_slash(self):
  p=copy.deepcopy(self.p);p["presentation"]="INLINE_SLASH"
  with self.assertRaisesRegex(ValueError,"below English"):self.make(p)
 def test_proposal_cannot_self_certify(self):
  p=copy.deepcopy(self.p);p["publishable"]=True
  with self.assertRaisesRegex(ValueError,"cannot self-approve"):self.make(p)
 def test_jussive_does_not_get_wayyiqtol_tense(self):
  p=self.edit("01Qsh",expect_verb_form="w")
  with self.assertRaisesRegex(ValueError,"Expected source verb-form"):self.make(p)
 def test_verse_missing_fails(self):
  p=copy.deepcopy(self.p);p["verses"].pop()
  with self.assertRaisesRegex(ValueError,"verse"):self.make(p)
if __name__=="__main__":unittest.main()
