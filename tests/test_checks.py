import copy,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"scripts"))
from check import data,validate,blockers
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lex=data("lexicon/hebrew.json");cls.links=data("links/registry.json");cls.v=data("samples/Gen_1_4.json");cls.css=(R/"style/links.css").read_text()
 def chk(self,l=None,k=None,v=None,c=None):
  return validate(self.lex if l is None else l,self.links if k is None else k,self.v if v is None else v,self.css if c is None else c)
 def test_clean_fixture(self): self.assertEqual(self.chk(),[])
 def test_asah_not_shaped(self):
  l=copy.deepcopy(self.lex);next(x for x in l["entries"] if x["id"]=="asah")["english_base"]="shape";self.assertIn("LOCK:asah",self.chk(l=l))
 def test_bara_not_made(self):
  l=copy.deepcopy(self.lex);next(x for x in l["entries"] if x["id"]=="bara")["english_base"]="make";self.assertIn("LOCK:bara",self.chk(l=l))
 def test_no_it(self):
  v=copy.deepcopy(self.v);v["translation"]="And God — He saw the light that it was good.";self.assertIn("NEUTER",self.chk(v=v))
 def test_wrong_tense(self):
  v=copy.deepcopy(self.v);v["morphology"][0]["english_tense"]="PRESENT";self.assertIn("WRONG_WAYYIQTOL_TENSE",self.chk(v=v))
 def test_hath_seen_not_simple_past(self):
  v=copy.deepcopy(self.v);v["morphology"][0]["english"]="hath seen";self.assertIn("WRONG_WAYYIQTOL_TENSE",self.chk(v=v))
 def test_slash_fails(self):
  l=copy.deepcopy(self.links);l["entries"][0]["below"]="Noah/Rest";self.assertIn("INLINE_SLASH",self.chk(k=l))
 def test_below_required(self):
  l=copy.deepcopy(self.links);l["entries"][0]["position"]="inline";self.assertTrue(any(x.startswith("POSITION:") for x in self.chk(k=l)))
 def test_homonym_type_required(self):
  l=copy.deepcopy(self.links);l["entries"][0]["relation"]="ALL_SAME";self.assertTrue(any(x.startswith("REL:") for x in self.chk(k=l)))
 def test_footnote_required(self):
  l=copy.deepcopy(self.links);l["entries"][0]["note"]="";self.assertIn("MISSING_NOTE",self.chk(k=l))
 def test_vertical_css(self):
  self.assertIn("NONVERTICAL_CSS",self.chk(c=self.css.replace("flex-direction:column","flex-direction:row")))
 def test_release_blocked(self): self.assertGreaterEqual(len(blockers(self.lex,self.v)),5)
if __name__=="__main__":unittest.main()
