import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_study_queue import classify_missing,make_card

class LexicalResearchQueueTests(unittest.TestCase):
 def test_plus_remains_unresolved_even_if_base_exists(self):
  x={"source_exact_lemma":"1008+","source_occurrences":2,"aug_index_key":"1008+"}
  base={"1008":{"status":"EXACT_AUG_TO_LEXICAL_INDEX","verified_existing_lexical_entry_ids":["a"]}}
  r=classify_missing(x,base,{"1008+":[{"verse":"Gen.1.1"}]},{"1008+":2})
  self.assertEqual(r["status"],"PLUS_MARKER_UNEXPLAINED")
  self.assertEqual(r["potential_base_lemma"],"1008")
  self.assertFalse(r["automatic_merger_permitted"])
  self.assertEqual(r["potential_base_source_crosswalk"]["lexical_ids"],["a"])
 def test_nonplus_absent_aug_not_reassigned(self):
  x={"source_exact_lemma":"738","source_occurrences":1,"aug_index_key":"738"}
  r=classify_missing(x,{}, {},{"738":1})
  self.assertEqual(r["status"],"AUG_INDEX_KEY_NOT_PRESENT")
  self.assertIsNone(r["potential_base_source_crosswalk"])
 def test_missing_real_crosswalk_blocks_study_card(self):
  with self.assertRaisesRegex(ValueError,"without verified"):
   make_card({"source_exact_lemma":"1"},None,{}, {},{})
 def test_wrong_dictionary_identity_blocks(self):
  lemma={"source_exact_lemma":"1","genesis_1_occurrence_count":1,
         "verse_references":["Gen.1.1"],"source_word_token_ids":["a"],
         "observed_pointed_spellings":["א"],"source_tagged_wayyiqtol_count":0}
  x={"status":"EXACT_AUG_TO_LEXICAL_INDEX",
     "verified_existing_lexical_entry_ids":["l"],
     "lexical_xrefs":[{"strong_status":{"found":["H1"]},
                      "bdb_status":{"found":["b1"]}}]}
  with self.assertRaisesRegex(ValueError,"missing actual source"):
   make_card(lemma,x,{}, {},{})
 def test_nonlocked_card_never_assigns_english(self):
  lemma={"source_exact_lemma":"1","genesis_1_occurrence_count":1,
         "verse_references":["Gen.1.1"],"source_word_token_ids":["a"],
         "observed_pointed_spellings":["א"],"source_tagged_wayyiqtol_count":0}
  x={"status":"EXACT_AUG_TO_LEXICAL_INDEX",
     "verified_existing_lexical_entry_ids":["l"],
     "lexical_xrefs":[{"strong_status":{"found":["H1"]},
                      "bdb_status":{"found":["b1"]}}]}
  dictionary={"id":"H1","headword":"א","fields":{"meaning":"word"}}
  bdb={"id":"b1","headword":"א","fields":{"def":"source glossary"}}
  c=make_card(lemma,x,{"H1":dictionary},{"b1":bdb},{})
  self.assertIsNone(c["owner_english_family"])
  self.assertIsNone(c["candidate_english_from_dictionary"])
  self.assertFalse(c["source_dictionary_meaning_is_OLT_translation"])
if __name__=="__main__":unittest.main()
