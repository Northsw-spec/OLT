"""OLT-025: fail-closed CI permissions and publication boundary checks."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github/workflows/olt-015.yml"
SOURCE=ROOT/"data/research/genesis_01_complete_research_alignment.json"
POLICY=ROOT/"data/policy/olt_underword_overrides.json"

class OLT025(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow=WORKFLOW.read_text(encoding="utf-8")
        cls.source=json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.policy=json.loads(POLICY.read_text(encoding="utf-8"))

    def test_015_is_read_only_and_has_no_direct_branch_push(self):
        self.assertIn("permissions:\n  contents: read\n",self.workflow)
        for forbidden in ("contents: write","git push","git commit","git add ",
                          "persist-credentials: true"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,self.workflow)
        self.assertIn("persist-credentials: false",self.workflow)

    def test_015_runs_on_pr_and_checks_fresh_regeneration(self):
        self.assertIn("  pull_request:\n",self.workflow)
        self.assertIn('      - ".github/workflows/olt-015.yml"',self.workflow)
        self.assertIn("git ls-files --error-unmatch",self.workflow)
        self.assertIn("git diff --exit-code --",self.workflow)
        self.assertIn("exit 1",self.workflow)
        self.assertIn("submit a pull request; CI cannot push to main",self.workflow)
        self.assertIn("python scripts/audit_full_genesis_research.py",self.workflow)

    def test_015_remains_a_research_data_check_not_publication(self):
        self.assertEqual(self.source["original_source_word_tokens"],434)
        self.assertEqual(self.source["source_verses"],31)
        self.assertEqual(self.source["publication_status"],"BLOCKED")
        self.assertEqual(self.source["authoritatively_approved_english_verses"],0)
        self.assertEqual(self.policy["publication_status"],"BLOCKED")
        self.assertEqual(self.policy["scope"],"ONE_EXCEPTION_GENESIS_1_1_ONLY")

if __name__=="__main__":
    unittest.main()
