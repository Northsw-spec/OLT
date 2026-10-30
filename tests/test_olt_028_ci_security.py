"""OLT-028: regression barrier against CI pushing or approving research."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW_DIR=ROOT/".github/workflows"
WAVE_FOUR={
 "audit-corpus.yml":["data/quality/corpus_audit.json","data/quality/observed_exact_lemmas.json","data/quality/genesis_01_morphology.json","data/quality/lexicon_candidates.jsonl","data/quality/genesis_01_owner_lock_anchors.json","data/quality/lexicon_join_report.json"],
 "bdb-nested.yml":["data/imported/lexicon/bdb_nested.jsonl.gz","data/quality/bdb_nested_manifest.json","data/quality/genesis_01_bdb_sense_evidence.json"],
 "import-ot.yml":["data/imported/manifest.json"],
 "lexicon-candidates.yml":["data/quality/lexicon_candidates.jsonl","data/quality/genesis_01_owner_lock_anchors.json","data/quality/lexicon_join_report.json"],
 "verify-xml-crosswalk.yml":["data/quality/verified_id_crosswalk.jsonl","data/quality/verified_id_crosswalk_report.json"],
}

class TestOLT028(unittest.TestCase):
 def test_every_workflow_has_no_default_branch_write(self):
  files=sorted(WORKFLOW_DIR.glob("*.yml"))
  self.assertEqual(len(files),22)
  for path in files:
   with self.subTest(workflow=path.name):
    s=path.read_text(encoding="utf-8")
    for forbidden in ("contents: write","git push origin HEAD:main","persist-credentials: true"):
     self.assertNotIn(forbidden,s)
    self.assertNotIn("git commit -m ",s)

 def test_final_five_workflows_are_pr_scoped_and_fail_closed(self):
  for name,products in WAVE_FOUR.items():
   with self.subTest(workflow=name):
    s=(WORKFLOW_DIR/name).read_text(encoding="utf-8")
    self.assertIn("permissions:\n  contents: read",s)
    self.assertIn("persist-credentials: false",s)
    self.assertIn("  pull_request:\n",s)
    self.assertIn('      - "tests/test_olt_028_ci_security.py"',s)
    self.assertIn("git ls-files --error-unmatch",s)
    self.assertIn("git status --porcelain --untracked-files=all",s)
    self.assertIn("exit 1",s)
    for product in products:
     if name=="import-ot.yml":
      # The OT importer intentionally triggers on its entire generated tree.
      self.assertIn('      - "data/imported/**"',s)
      self.assertIn("git status --porcelain --untracked-files=all -- data/imported",s)
     else:
      self.assertGreaterEqual(s.count('      - "'+product+'"'),1)
     self.assertTrue((ROOT/product).is_file())

 def test_pinned_source_independence_and_publication_block(self):
  def load(path):
   return json.loads((ROOT/path).read_text(encoding="utf-8"))
  imported=load("data/imported/manifest.json")
  self.assertEqual(imported["corpus"]["books"],39)
  self.assertEqual(imported["hard_limits"]["genesis_1_publication"],"BLOCKED")
  bdb=load("data/quality/bdb_nested_manifest.json")
  self.assertEqual(bdb["entries"],11845)
  self.assertEqual(bdb["genesis_1_release"],"BLOCKED")
  audit=load("data/quality/corpus_audit.json")
  self.assertEqual(audit["editorial_certification"],"NOT_PERFORMED")
  self.assertEqual(audit["token_count"],306785)
  report=load("data/quality/lexicon_join_report.json")
  self.assertEqual(report["all_english_approval"],"NOT_DONE")
  crosswalk=load("data/quality/verified_id_crosswalk_report.json")
  self.assertEqual(crosswalk["release_status"],"BLOCKED_NOT_EDITORIALLY_REVIEWED")

if __name__=="__main__":
 unittest.main()
