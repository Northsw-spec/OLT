"""OLT-SIMPLE-ENGINE-001: keep the owner's simpler architecture authoritative.

Engineering priority only; passing these checks does not approve translation
accuracy, copyrights, source alignments or Bible release.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs/OLT_SIMPLE_ENGINE_001.md"
MASTER = ROOT / "docs/MASTERPROMPT.md"
STATUS = ROOT / "docs/STATUS_CURRENT.md"
ENGLISH_GATE = ROOT / "docs/OLT_ENGLISH_FIRST_OWNER_GATE.md"


class TestOLTSimpleEngineOwnerPriority(unittest.TestCase):
    def test_masterprompt_begins_with_binding_simple_engine_before_old_roadmap(self):
        text = MASTER.read_text(encoding="utf-8")
        self.assertIn("## OLT-SIMPLE-ENGINE-001", text[:150])
        self.assertLess(text.index("## OLT-SIMPLE-ENGINE-001"),
                        text.index("## OLT-035D"))
        self.assertIn("DO NOT REBUILD THE FORMER THOUSANDS-OF-HOURS", text[:900])
        self.assertIn("OLT_SIMPLE_ENGINE_001.md", text[:4000])
        self.assertIn("The NT is a **separate Greek-source path**", text[:4500])

    def test_lean_policy_excludes_full_lexicon_rebuild_and_blanket_manual_review(self):
        text = POLICY.read_text(encoding="utf-8")
        self.assertIn("## Cost and complexity control", text)
        self.assertIn("Exception-based review", text)
        self.assertIn("not** a requirement", text)
        self.assertIn("Do not resume the former full standalone engine", text)
        self.assertIn("PDF green *text span*", text)
        self.assertIn("public GitHub may retain importer code", text)

    def test_no_false_import_or_linguistic_approval_and_english_still_only(self):
        policy = POLICY.read_text(encoding="utf-8")
        master = MASTER.read_text(encoding="utf-8")[:4400]
        status = STATUS.read_text(encoding="utf-8")[:4200]
        self.assertIn("929-chapter import has **NOT** yet been executed", policy)
        self.assertIn("publication remains **BLOCKED**", master)
        self.assertIn("English is the only active target", policy)
        self.assertIn("OLT-SIMPLE-ENGINE-001", status)
        self.assertIn("English-only", status)
        self.assertIn("entire", ENGLISH_GATE.read_text(encoding="utf-8").lower())

    def test_blank_readme_history_and_provenance_remain_preserved(self):
        self.assertEqual((ROOT / "README.md").read_bytes(), b"")
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("Retain the existing Git commit history", policy)
        self.assertIn("Do not force-push a rewritten history", policy)
        self.assertIn("accurate attribution", MASTER.read_text(encoding="utf-8")[:4300])
        self.assertTrue((ROOT / "docs/OLT_CHES_PRIVATE_INGEST.md").is_file())


if __name__ == "__main__":
    unittest.main()
