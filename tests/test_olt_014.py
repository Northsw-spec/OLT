import copy,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"scripts"))
from build_verse_research import load,build
class OLT014(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.plan=load(R/"data/plans/olt_014_genesis_26_31.json")
  cls.original=load(R/"data/quality/genesis_01_source_review_dossier.json")
  cls.cards=load(R/"data/quality/genesis_01_dictionary_study_cards.json")
  cls.seed=load(R/"lexicon/hebrew.json")
 def check(self,p=None,s=None):
  return build(self.plan if p is None else p,self.original if s is None else s,self.cards,self.seed)
 def edit(self,id,gloss):
  p=copy.deepcopy(self.plan)
  next(x for v in p["verses"] for x in v["proposals"] if x["source_token_id"]==id)["english_fragment"]=gloss
  return p
 def test_exact_117_source_words(self):
  r=self.check()
  self.assertEqual(r["source_token_count"],117)
  self.assertEqual(r["source_wayyiqtol_count"],9)
  self.assertEqual([len(v["original_word_alignments"]) for v in r["verse_research"]],[19,13,22,27,21,15])
  self.assertEqual(len(r["non_numeric_grammar_token_ids"]),5)
  self.assertEqual(r["publication_status"],"BLOCKED")
 def test_asah_not_bara_26(self):
  with self.assertRaisesRegex(ValueError,"Owner asah"):self.check(self.edit("01oiy","Let Us shape"))
 def test_bara_not_create_27(self):
  with self.assertRaisesRegex(ValueError,"Owner bara"):self.check(self.edit("01PUg","He created"))
 def test_qatal_bara_not_wayyiqtol(self):
  r=self.check()
  t=next(x for v in r["verse_research"] for x in v["original_word_alignments"] if x["source_token_id"]=="01PUg")
  self.assertFalse(t["is_source_tagged_wayyiqtol"]);self.assertEqual(t["source_verb_form"],"p")
 def test_earth_feminine_suffix(self):
  p=self.edit("01yT5","and subdue it")
  with self.assertRaisesRegex(ValueError,"neutral it"):self.check(p)
 def test_missing_original_word_fails(self):
  p=copy.deepcopy(self.plan);p["verses"][3]["proposals"].pop()
  with self.assertRaisesRegex(ValueError,"count differs"):self.check(p)
 def test_wrong_source_morphology_fails(self):
  s=copy.deepcopy(self.original)
  next(x for x in s["tokens"] if x["source_token_id"]=="012gM")["source_morphology_raw"]="HC/Vqw1cs"
  with self.assertRaisesRegex(ValueError,"Exact source morphology"):self.check(s=s)
 def test_pronominal_object_him_and_them(self):
  r=self.check()
  tokens={x["source_token_id"]:x for v in r["verse_research"] for x in v["original_word_alignments"]}
  self.assertEqual(tokens["01pUN"]["english_fragment_research_only"],"him")
  self.assertEqual(tokens["013gY"]["english_fragment_research_only"],"them")
 def test_non_numeric_preposition_person_number(self):
  r=self.check()
  tokens={x["source_token_id"]:x for v in r["verse_research"] for x in v["original_word_alignments"]}
  for id,gloss in (("01ypu","to them"),("01pAw","to you"),("01884","in him"),("01wEr","to you"),("01teU","in him")):
   self.assertEqual(tokens[id]["english_fragment_research_only"],gloss)
 def test_no_false_trinity_equated_to_lexeme(self):
  p=copy.deepcopy(self.plan)
  p["research_notes"][4]["status"]="APPROVED"
  with self.assertRaisesRegex(ValueError,"Claimed certainty"):self.check(p)
 def test_nonpublication_and_homonyms_below_word(self):
  r=self.check()
  self.assertFalse(r["full_english_lexicon_approved"])
  self.assertEqual(r["under_word_homonym_presentation"],"UNDER_ENGLISH_WORD")
  self.assertTrue(all(not x["below_word_homonym_links"]["approved_links"] for v in r["verse_research"] for x in v["original_word_alignments"]))
if __name__=="__main__":unittest.main()
