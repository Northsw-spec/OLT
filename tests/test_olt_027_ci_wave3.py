"""OLT-027: no direct main pushes and no silent source research publication."""
from pathlib import Path
import json
import unittest

R=Path(__file__).resolve().parents[1]
FILES={
 "genesis-02-05.yml":["data/research/genesis_01_verses_02_to_05_research.json"],
 "genesis-06-10.yml":["data/research/genesis_01_verses_06_to_10_research.json"],
 "genesis-lexical-proposals.yml":[
   "data/research/genesis_01_verse_01_alignment_proposal.json",
   "data/research/genesis_01_97_lemma_review_queue.json"],
 "genesis-review-dossier.yml":["data/quality/genesis_01_source_review_dossier.json"],
 "study-queue.yml":[
   "data/quality/unresolved_lexeme_triage.json",
   "data/quality/genesis_01_dictionary_study_cards.json"],
}

class OLT027(unittest.TestCase):
 def test_readonly_and_fail_closed_output_verification(self):
  for name,outputs in FILES.items():
   with self.subTest(name=name):
    s=(R/".github/workflows"/name).read_text(encoding="utf-8")
    self.assertIn("permissions:\n  contents: read\n",s)
    self.assertIn("persist-credentials: false",s)
    self.assertIn("  pull_request:\n",s)
    self.assertIn('      - "tests/test_olt_027_ci_wave3.py"',s)
    self.assertIn("git ls-files --error-unmatch "+" ".join(outputs),s)
    self.assertIn("git diff --exit-code -- "+" ".join(outputs),s)
    self.assertIn("exit 1",s)
    for path in outputs:
     self.assertGreaterEqual(s.count('      - "'+path+'"'),2)
    for forbidden in ["contents: write","persist-credentials: true",
                      "git push","git commit","git add "]:
     self.assertNotIn(forbidden,s)

 def test_generated_evidence_is_not_automatically_approved(self):
  q=lambda path:json.loads((R/path).read_text(encoding="utf-8"))
  self.assertEqual(q(FILES["genesis-02-05.yml"][0])["release_status"],"BLOCKED")
  self.assertEqual(q(FILES["genesis-06-10.yml"][0])["chapter_publication"],"BLOCKED")
  v=q(FILES["genesis-lexical-proposals.yml"][0])
  self.assertEqual(v["source_token_count"],7)
  self.assertEqual(v["publication_status"],"BLOCKED")
  self.assertEqual(q(FILES["genesis-lexical-proposals.yml"][1])["new_english_decisions_pending"],94)
  d=q(FILES["genesis-review-dossier.yml"][0])
  self.assertFalse(d["publishable"])
  self.assertEqual(len(d["tokens"]),434)
  x=q(FILES["study-queue.yml"][0])
  self.assertFalse(x["special_lemma_merging_allowed"])
  c=q(FILES["study-queue.yml"][1])
  self.assertEqual(c["genesis_chapter_publication"],"BLOCKED")

if __name__=="__main__":unittest.main()
