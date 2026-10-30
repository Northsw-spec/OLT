"""OLT-026: verify five source-research generators cannot push to protected main."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOWS={
  "olt-011.yml":("data/research/olt_011_genesis_11_15.json",69),
  "olt-012.yml":("data/research/olt_012_genesis_16_20.json",59),
  "olt-013.yml":("data/research/olt_013_genesis_21_25.json",74),
  "olt-014.yml":("data/research/olt_014_genesis_26_31.json",117),
  "olt-016.yml":("data/research/genesis_01_lexeme_editorial_queue.json",97),
}

class TestOLT026(unittest.TestCase):
 def test_read_only_token_permissions_and_no_main_push(self):
  for name,(artifact,count) in WORKFLOWS.items():
   with self.subTest(workflow=name):
    f=(ROOT/".github/workflows"/name).read_text(encoding="utf-8")
    self.assertIn("permissions:\n  contents: read\n",f)
    self.assertIn("persist-credentials: false",f)
    self.assertIn("  pull_request:\n",f)
    self.assertIn('      - "tests/test_olt_026_ci_wave2.py"',f)
    self.assertIn("git ls-files --error-unmatch "+artifact,f)
    self.assertIn("git diff --exit-code -- "+artifact,f)
    self.assertIn("exit 1",f)
    self.assertIn("Commit derived files through a pull request",f)
    for forbidden in ("contents: write","persist-credentials: true","git push",
                      "git commit","git add "):
     self.assertNotIn(forbidden,f)

 def test_generated_research_provenance_unchanged(self):
  for name,(artifact,count) in WORKFLOWS.items():
   with self.subTest(workflow=name):
    data=json.loads((ROOT/artifact).read_text(encoding="utf-8"))
    self.assertEqual(data["publication_status"],"BLOCKED")
    if name=="olt-016.yml":
     self.assertEqual(data["source_lemma_ids"],count)
     self.assertEqual(data["new_english_families_pending"],94)
     self.assertEqual(data["approved_homonym_links"],0)
    else:
     self.assertEqual(data["source_token_count"],count)
     self.assertFalse(data["full_english_lexicon_approved"])
     self.assertFalse(data["independent_hebrew_morphology_signed_off"])

if __name__=="__main__":unittest.main()
