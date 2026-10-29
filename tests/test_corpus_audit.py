import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_corpus import lemma_parts,morphology_parts

class MorphologyTests(unittest.TestCase):
    def test_augmented_lemma_keeps_letter(self):
        self.assertEqual(lemma_parts("1254 a")[0]["exact_key"],"1254 a")
        self.assertEqual(lemma_parts("1254 b")[0]["exact_key"],"1254 b")
        self.assertNotEqual(lemma_parts("1254 a")[0]["exact_key"],lemma_parts("1254 b")[0]["exact_key"])
    def test_prefix_retained(self):
        parts=lemma_parts("c/b/1004 b")
        self.assertEqual([x["kind"] for x in parts],["PREFIX_OR_OTHER","PREFIX_OR_OTHER","LEXEME"])
        self.assertEqual(parts[-1]["exact_key"],"1004 b")
    def test_wayyiqtol_detect(self):
        parts=morphology_parts("HC/Vqw3ms")
        self.assertEqual(parts[1]["verb_form"],"WAYYIQTOL")
        self.assertEqual(parts[1]["language"],"H")
    def test_qatal_not_wayyiqtol(self):
        self.assertEqual(morphology_parts("HVqp3ms")[0]["verb_form"],"QATAL")
        self.assertEqual(morphology_parts("HC/Vqq3cp")[1]["verb_form"],"SEQUENTIAL_PERFECT")
    def test_aramaic_not_hebrew(self):
        self.assertEqual(morphology_parts("AVqp3ms")[0]["language"],"A")
    def test_suffix_morph_retained(self):
        m=morphology_parts("HNcmsc/Sp3ms")
        self.assertEqual(m[1]["part_of_speech"],"S")
    def test_combined_causative_wayyiqtol(self):
        self.assertEqual(morphology_parts("HC/Vhw3ms")[1]["verb_form"],"WAYYIQTOL")

if __name__=="__main__":
    unittest.main()
