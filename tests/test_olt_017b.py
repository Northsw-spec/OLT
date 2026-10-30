import unittest,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=json.loads((ROOT/"data/research/olt_017b_scholarly_lexemes.json").read_text())
S=json.loads((ROOT/"data/quality/genesis_01_source_review_dossier.json").read_text())
class OLT017B(unittest.TestCase):
 def test_research_never_approves_words_or_links(self):
  self.assertEqual(A["source_lexeme_ids_count"],4)
  self.assertEqual(A["new_approved_english_families"],0)
  self.assertEqual(A["approved_homonym_links"],0)
  self.assertEqual(A["publication_status"],"BLOCKED")
 def test_all_four_ids_are_actual_source_words(self):
  d={x["source_token_id"]:x for x in S["tokens"]}
  self.assertEqual(len(A["cases"]),4)
  for c in A["cases"]:
   self.assertEqual(c["reference"],"Gen.1.2")
   self.assertEqual(d[c["source_token_id"]]["verse"],"Gen.1.2")
   self.assertIn(c["exact_lemma"],d[c["source_token_id"]]["exact_lexemes"])
   self.assertEqual(c["pointed_hebrew"],d[c["source_token_id"]]["pointed_source_word"])
   self.assertEqual(c["raw_morphology"],d[c["source_token_id"]]["source_morphology_raw"])
 def test_separate_tohu_bohu_lexemes(self):
  d={c["question_id"]:c for c in A["cases"]}
  self.assertNotEqual(d["OLT-017B-TOHU"]["exact_lemma"],d["OLT-017B-BOHU"]["exact_lemma"])
  self.assertEqual(d["OLT-017B-BOHU"]["raw_morphology"],"HC/Ncmsa")
 def test_piel_participle_not_wayyiqtol(self):
  d=next(c for c in A["cases"] if c["question_id"]=="OLT-017B-RACHAPH")
  self.assertEqual(d["raw_morphology"],"HVprfsa")
  self.assertFalse(next(t for t in S["tokens"] if t["source_token_id"]==d["source_token_id"])["source_tagged_wayyiqtol"])
 def test_evidence_provenance_and_no_homonym_certification(self):
  for c in A["cases"]:
   self.assertFalse(c["homonym_identity_approved"])
   self.assertGreaterEqual(len(c["evidence"]),2)
   self.assertTrue(all(x["url"].startswith("https://") for x in c["evidence"]))
   self.assertTrue(all(x["type"] in {"BDB_LEXICAL_ENTRY","JOURNAL_ABSTRACT","DISSERTATION_REPOSITORY_ABSTRACT","MORPHOLOGY_DISPLAY"} for x in c["evidence"]))
if __name__=="__main__":unittest.main()
