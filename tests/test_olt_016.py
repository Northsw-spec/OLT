import sys,copy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"scripts"))
from build_genesis_review_queue import generate,load
class TestOLT016(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=load(R/"data/research/genesis_01_complete_research_alignment.json")
  cls.cards=load(R/"data/quality/genesis_01_dictionary_study_cards.json")
  cls.seed=load(R/"lexicon/hebrew.json")
 def build(self,s=None,c=None):
  return generate(s if s is not None else self.source,c if c is not None else self.cards,self.seed)
 def test_scope_and_release_block(self):
  z=self.build()
  self.assertEqual(z["source_lemma_ids"],97)
  self.assertEqual(z["new_english_families_pending"],94)
  self.assertEqual(z["owner_locked_families"],3)
  self.assertEqual(z["publication_status"],"BLOCKED")
  self.assertEqual(z["approved_homonym_links"],0)
  self.assertTrue(all(x["homonym_slot"]["placement"]=="BELOW_ENGLISH_WORD" for x in z["entries"]))
 def test_wrong_dictionary_entry_rejected(self):
  c=copy.deepcopy(self.cards);c["cards"].pop()
  with self.assertRaises(ValueError):self.build(c=c)
 def test_source_duplicate_rejected(self):
  s=copy.deepcopy(self.source)
  s["genesis_1_research_verses"][0]["original_token_alignment"][1]["source_token_id"]=s["genesis_1_research_verses"][0]["original_token_alignment"][0]["source_token_id"]
  with self.assertRaisesRegex(ValueError,"Duplicate"):self.build(s=s)
 def test_falsely_published_rejected(self):
  s=copy.deepcopy(self.source);s["publication_status"]="PUBLISHED"
  with self.assertRaisesRegex(ValueError,"published"):self.build(s=s)
 def test_variants_do_not_automatically_prove_homonyms(self):
  z=self.build()
  self.assertTrue(z["distinct_english_fragments_do_not_prove_homonyms"])
  self.assertGreater(z["lemma_ids_with_multiple_english_fragments"],0)
  self.assertTrue(all(not r["homonym_identity_approved"] for r in z["entries"]))
if __name__=="__main__":unittest.main()
