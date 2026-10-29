import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_lexicon_candidates import exact_number_candidate

class LexicalJoinTests(unittest.TestCase):
    def test_exact_numeric_dictionary_id(self):
        self.assertEqual(exact_number_candidate("H01254"),"1254")
        self.assertEqual(exact_number_candidate("1254"),"1254")
    def test_homonym_not_silently_collapsed(self):
        self.assertIsNone(exact_number_candidate("1254 a"))
        self.assertIsNone(exact_number_candidate("1254 b"))
    def test_inexact_refs_not_guessed(self):
        self.assertIsNone(exact_number_candidate("strong-1254"))
        self.assertIsNone(exact_number_candidate("1254+"))
        self.assertIsNone(exact_number_candidate("prefix-b"))
