"""OLT-029: changing derived research alone must invoke its source verifier."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUTS={
    "olt-015.yml":(
        "data/research/genesis_01_complete_research_alignment.json",
        "genesis/GENESIS_01_SOURCE_RESEARCH_PREVIEW.md",
    ),
    "olt-011.yml":("data/research/olt_011_genesis_11_15.json",),
    "olt-012.yml":("data/research/olt_012_genesis_16_20.json",),
    "olt-013.yml":("data/research/olt_013_genesis_21_25.json",),
    "olt-014.yml":("data/research/olt_014_genesis_26_31.json",),
    "olt-016.yml":("data/research/genesis_01_lexeme_editorial_queue.json",),
}

class OLT029(unittest.TestCase):
    def test_output_only_pr_also_triggers_reproducibility_check(self):
        for workflow, outputs in OUTPUTS.items():
            with self.subTest(workflow=workflow):
                text=(ROOT/".github/workflows"/workflow).read_text(encoding="utf-8")
                self.assertEqual(text.count("  pull_request:\n"),1)
                push=text.split("  push:\n",1)[1].split("  pull_request:\n",1)[0]
                pr=text.split("  pull_request:\n",1)[1].split("  workflow_dispatch:",1)[0]
                for output in outputs:
                    quoted='      - "'+output+'"\n'
                    self.assertIn(quoted,push)
                    self.assertIn(quoted,pr)
                    self.assertTrue((ROOT/output).is_file())
                self.assertIn('      - "tests/test_olt_029_derived_trigger_coverage.py"',pr)
                self.assertIn("permissions:\n  contents: read\n",text)
                self.assertIn("persist-credentials: false",text)
                self.assertIn("git diff --exit-code --",text)
                self.assertNotIn("contents: write",text)
                self.assertNotIn("git push",text)

if __name__=="__main__":
    unittest.main()
