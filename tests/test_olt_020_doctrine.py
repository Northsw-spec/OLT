import unittest,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class OLT020(unittest.TestCase):
 def test_binding_owner_doctrine_and_firewall(self):
  p=json.loads((R/"data/policy/olt_theological_framework.json").read_text())
  self.assertEqual(p["source"],"EXPLICIT_OWNER_DECISION")
  self.assertEqual(p["theology"],"BINITARIAN")
  self.assertEqual(p["not_theology"],"TRINITARIAN")
  self.assertEqual(p["owner_affirmation"],"THE LORD JESUS IS THE SPIRIT")
  self.assertTrue(p["source_lexicon_distinct_from_doctrine"])
  self.assertTrue(p["spirit_referent_requires_context"])
  self.assertIn("BINITARIAN", (R/"docs/MASTERPROMPT.md").read_text())
  self.assertIn("THE LORD JESUS IS THE SPIRIT",(R/"docs/DECISIONS.md").read_text())
 def test_contextual_bet_and_existing_locks(self):
  p=json.loads((R/"data/policy/olt_theological_framework.json").read_text())
  self.assertTrue(p["b_prefix"]["render_by_context"])
  self.assertFalse(p["b_prefix"]["automatic_with_under_every_in"])
  self.assertEqual(p["b_prefix"]["secondary_gloss"],"DIRECTLY_BELOW_ENGLISH_ANCHOR")
  self.assertEqual(p["b_prefix"]["uncertain"],"REVIEW_REQUIRED")
  self.assertEqual(p["owner_locks"]["bara"],"shape")
  self.assertEqual(p["owner_locks"]["asah"],"make")
  self.assertEqual(p["owner_locks"]["raqia"],"firmament")
  self.assertEqual(p["owner_locks"]["wayyiqtol"],"SIMPLE_PAST")
  self.assertIn("[of His Power]",p["owner_locks"]["genesis_1_1"])
  self.assertEqual(p["publication_status"],"BLOCKED")
if __name__=="__main__":
 unittest.main()
