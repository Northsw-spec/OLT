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

 def test_021_eternal_uncreated_son_and_one_god(self):
  p=json.loads((R/"data/policy/olt_theological_framework.json").read_text(encoding="utf-8"))
  self.assertEqual(p["clarification_id"],"OLT-021")
  self.assertGreaterEqual(p["version"],2)
  self.assertTrue(p["clarification_supersedes_first_created_inference"])
  d=p["dogmatic_confession"]
  self.assertEqual(d["unity"],"ONE_GOD")
  self.assertEqual(d["father_and_son"],"ONE_IN_GODHEAD")
  self.assertTrue(d["one_faith"])
  self.assertEqual(d["one_lord"],"JESUS_CHRIST")
  self.assertTrue(d["binitarian"])
  self.assertFalse(d["trinitarian"])
  self.assertTrue(d["jesus_is_the_spirit"])
  self.assertTrue(d["son_eternal"])
  self.assertTrue(d["son_uncreated"])
  self.assertTrue(d["son_existed_with_father_before_world_foundation"])
  self.assertEqual(d["creation"],"JOINT_WORK_OF_FATHER_AND_SON_BEFORE_INCARNATION")

 def test_021_incarnation_is_not_start_of_sons_existence(self):
  p=json.loads((R/"data/policy/olt_theological_framework.json").read_text(encoding="utf-8"))
  d=p["dogmatic_confession"]
  self.assertTrue(d["son_preexisted_human_birth"])
  self.assertEqual(d["son_became_human_through"],"MARY")
  self.assertFalse(d["human_birth_started_eternal_sons_existence"])
  self.assertFalse(d["firstborn_son_is_first_created_being"])
  self.assertIn("ETERNAL_UNCREATED_FIRSTBORN_SON",d["revelation_3_14_owner_reading"])
  self.assertFalse(d["revelation_3_14_is_mandatory_greek_lexical_gloss"])

 def test_021_binding_documents_repeat_corrected_creed(self):
  checks={
   "docs/MASTERPROMPT.md": ["THE SON IS ETERNAL AND UNCREATED","FATHER AND SON'S JOINT WORK","FIRSTBORN IS NOT FIRST CREATED","BECAME HUMAN"],
   "docs/DOCTRINAL_FRAMEWORK.md":["The Son is eternal and uncreated","created the world together","through Mary","first created"],
   "docs/DECISIONS.md":["THE SON IS ETERNAL AND UNCREATED","CREATED THE WORLD TOGETHER","became human through Mary","first created"],
   "docs/OLT-021_BINITARIAN_CREED_CLARIFICATION.md":["THE SON IS ETERNAL AND UNCREATED","joint Father–Son work","through Mary","first created"],
  }
  for path,phrases in checks.items():
   text=(R/path).read_text(encoding="utf-8")
   for phrase in phrases:
    with self.subTest(path=path,phrase=phrase):
     self.assertIn(phrase.casefold(),text.casefold())

 def test_021_doctrine_is_not_forced_as_hebrew_or_greek(self):
  p=json.loads((R/"data/policy/olt_theological_framework.json").read_text(encoding="utf-8"))
  e=p["evidence_policy"]
  self.assertEqual(e["interpretive_layer"],"BINITARIAN_CANONICAL_INTERPRETATION")
  self.assertTrue(e["doctrine_does_not_override_original_hebrew_or_greek"])
  self.assertTrue(e["do_not_mechanically_map_ruach_pneuma_to_jesus"])
  self.assertTrue(e["beginning_genesis_1_1_not_automatically_instrumental_bet"])
  self.assertTrue(e["disputed_greek_arche_requires_source_review"])
  self.assertEqual(e["independent_philological_signoff"],"NOT_DONE")
  self.assertEqual(p["publication_status"],"BLOCKED")
if __name__=="__main__":
 unittest.main()
