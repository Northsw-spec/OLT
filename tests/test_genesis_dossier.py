import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from genesis_review_dossier import generate

class GenesisDossierTests(unittest.TestCase):
    def sample(self):
        verses=[{"verse":"Gen.1."+str(i),"tokens":[]} for i in range(1,32)]
        return {"status":"IMPORTED_SOURCE_MORPHOLOGY_NOT_INDEPENDENTLY_REVIEWED","verses":verses}
    def test_missing_tokens_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"Source word count changed"):
            generate(self.sample(),[])
    def test_missing_chapter_verse_is_rejected(self):
        s=self.sample()
        s["verses"][0]["verse"]="Gen.1.2"
        with self.assertRaisesRegex(ValueError,"missing"):
            generate(s,[])
    def test_falsely_claimed_independent_source_is_rejected(self):
        s=self.sample()
        s["status"]="INDEPENDENTLY_VERIFIED"
        with self.assertRaisesRegex(ValueError,"false verified"):
            generate(s,[])
    def test_duplicate_source_crosswalk_is_rejected(self):
        s=self.sample()
        r={"source_exact_lemma":"1254 a"}
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            generate(s,[r,r])
if __name__=="__main__":unittest.main()
