import sys,copy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"scripts"))
from audit_full_genesis_research import audit,load,DIR,INPUTS,SOURCE,preview
class OLT015(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.src=load(SOURCE)
  cls.parts=[load(DIR/p) for p in INPUTS]
 def make(self,parts=None):
  return audit(self.src,self.parts if parts is None else parts)
 def test_full_434_source_alignment_and_31_verses(self):
  x=self.make()
  self.assertEqual(x["source_verses"],31)
  self.assertEqual(x["original_source_word_tokens"],434)
  self.assertEqual(x["source_tagged_wayyiqtol_count"],50)
  self.assertEqual(x["distinct_exact_source_lemma_ids"],97)
  self.assertEqual(x["actual_original_grammar_only_word_tokens"],7)
  self.assertEqual(x["publication_status"],"BLOCKED")
  self.assertEqual(x["authoritatively_approved_english_verses"],0)
 def test_duplicate_original_word_rejected(self):
  p=copy.deepcopy(self.parts)
  a=p[3]["verse_research"][0]["original_word_alignments"]
  a[1]["source_token_id"]=a[0]["source_token_id"]
  with self.assertRaisesRegex(ValueError,"Source token ID|Duplicate"):self.make(p)
 def test_missing_one_word_rejected(self):
  p=copy.deepcopy(self.parts);p[4]["verse_research"][0]["original_word_alignments"].pop()
  with self.assertRaisesRegex(ValueError,"count differs"):self.make(p)
 def test_wrong_original_morphology_rejected(self):
  p=copy.deepcopy(self.parts);p[6]["verse_research"][0]["original_word_alignments"][0]["source_morphology_raw"]="HVqp3ms"
  with self.assertRaisesRegex(ValueError,"Original Hebrew/lemma/morphology"):self.make(p)
 def test_false_publication_rejected(self):
  p=copy.deepcopy(self.parts);p[5]["publication_status"]="PUBLISHED"
  with self.assertRaisesRegex(ValueError,"claimed publication"):self.make(p)
 def test_verse_reorder_rejected(self):
  p=copy.deepcopy(self.parts);p[2]["verses"][0],p[2]["verses"][1]=p[2]["verses"][1],p[2]["verses"][0]
  with self.assertRaisesRegex(ValueError,"misordered verses"):self.make(p)
 def test_english_neutral_pronoun_rejected(self):
  p=copy.deepcopy(self.parts);p[6]["verse_research"][-1]["english_main_research_proposal"]="And it was so."
  with self.assertRaisesRegex(ValueError,"Neutral pronoun"):self.make(p)
 def test_owner_bara_locked(self):
  p=copy.deepcopy(self.parts);p[6]["verse_research"][1]["original_word_alignments"][0]["english_fragment_research_only"]="And He created"
  with self.assertRaisesRegex(ValueError,"Bara owner-lock"):self.make(p)
 def test_genesis_1_4_exact_language_locked(self):
  p=copy.deepcopy(self.parts);p[1]["verses"][2]["english_main_proposal"]=p[1]["verses"][2]["english_main_proposal"].replace("[he was]","was")
  with self.assertRaisesRegex(ValueError,"Owner-approved Genesis 1:4"):self.make(p)
 def test_genesis_1_1_bracket_in_main_with_source_footnote(self):
  a=self.make()
  v=a["genesis_1_research_verses"][0]
  self.assertEqual(v["proposed_english_research_text"],
   "In the Beginning [of His Power] God — He shaped the Heavens and the Earth.")
  self.assertEqual(len(v["verse_footnote_proposals"]),1)
  self.assertEqual(v["verse_footnote_proposals"][0]["evidence_references"],["Gen.49.3","Deut.21.17"])
  md=preview(a)
  self.assertIn("the Earth.[^gen-1-1-power]",md)
  self.assertIn("[^gen-1-1-power]: [of His Power]",md)
  self.assertIn("separate Hebrew noun",md)
  self.assertEqual(a["authoritatively_approved_english_verses"],0)
 def test_missing_genesis_1_1_bracket_fails(self):
  p=copy.deepcopy(self.parts)
  p[0]["main_english_proposal"]=p[0]["unsupplemented_english_baseline_for_source_comparison"]
  with self.assertRaisesRegex(ValueError,"bracketed main text"):
   self.make(p)
 def test_missing_genesis_1_1_footnote_fails(self):
  p=copy.deepcopy(self.parts)
  p[0]["footnote_drafts"]=[x for x in p[0]["footnote_drafts"] if x.get("id")!="gen-1-1-power"]
  with self.assertRaisesRegex(ValueError,"footnote anchor"):
   self.make(p)
 def test_footnote_cannot_imply_power_is_literal_hebrew(self):
  p=copy.deepcopy(self.parts)
  note=next(x for x in p[0]["footnote_drafts"] if x.get("id")=="gen-1-1-power")
  note["is_independent_hebrew_lexeme"]=True
  with self.assertRaisesRegex(ValueError,"truthful intertextual"):
   self.make(p)
 def test_render_is_clearly_unapproved(self):
  md=preview(self.make())
  self.assertEqual(md.count("### Gen.1."),31)
  self.assertIn("NOT APPROVED BIBLE TEXT",md)
  self.assertIn("RELEASE BLOCKED",md)
if __name__=="__main__":unittest.main()
