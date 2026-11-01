"""Legacy policy retirement safety check. DANMEK-039 alone is active."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RETIRED = ROOT / "data/policy/danmek_024_english_comprehensibility_owner_priority.json"
CURRENT = ROOT / "data/policy/danmek_039_english_subject_verb_only.json"


class TestRetiredDanMek024Policy(unittest.TestCase):
    def test_024_cannot_silently_override_owner_039(self):
        previous = json.loads(RETIRED.read_text(encoding="utf-8"))
        current = json.loads(CURRENT.read_text(encoding="utf-8"))
        self.assertEqual(previous["status"], "SUPERSEDED")
        self.assertFalse(previous["is_active"])
        self.assertEqual(previous["superseded_by"], current["policy_id"])
        self.assertEqual(current["status"], "ACTIVE")
        self.assertTrue(current["english_grammatical_subject_must_precede_related_verb"])
        self.assertFalse(current["original_language_comparison_permitted"])
        self.assertFalse(current["old_danmek_scripts_are_active_grammar_authority"])


if __name__ == "__main__":
    unittest.main()
