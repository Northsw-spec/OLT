import tempfile,unittest
from pathlib import Path
from xml.etree import ElementTree as ET
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from import_bdb_nested import preserve,walk_tree,index_genesis

class BdbHierarchyTests(unittest.TestCase):
 def test_nested_sense_and_interleaved_text_are_preserved(self):
  x=ET.fromstring('<entry id="x">begin<sense n="1">inner<def>meaning</def>tail</sense>end</entry>')
  n=preserve(x)
  self.assertEqual(n["text"],"begin")
  self.assertEqual(n["children"][0]["tail"],"end")
  self.assertEqual(n["children"][0]["children"][0]["tail"],"tail")
  self.assertEqual(n["children"][0]["attrs"]["n"],"1")
  self.assertEqual(sum(1 for t in walk_tree(n) if t["tag"]=="sense"),1)
 def test_deep_nested_xml_keeps_order(self):
  x=ET.fromstring('<entry id="x"><sense n="1"><sense n="a"><ref r="Gen.1.1">1:1</ref></sense></sense></entry>')
  node=preserve(x)
  self.assertEqual([t["tag"] for t in walk_tree(node)],["entry","sense","sense","ref"])
  self.assertEqual(node["children"][0]["children"][0]["children"][0]["attrs"]["r"],"Gen.1.1")
 def test_missing_bdb_target_fails(self):
  cards={"cards":[{"source_exact_lemma_id":"1","dictionary_refs":{"bdb":[{"id":"missing"}]},
                   "genesis_occurrences":1,"owner_english_family":None}]}
  with self.assertRaisesRegex(ValueError,"target not found"):
   index_genesis(cards,[])
 def test_incomplete_genesis_cards_rejected(self):
  cards={"cards":[]}
  with self.assertRaisesRegex(ValueError,"97"):
   index_genesis(cards,[])
if __name__=="__main__":
 unittest.main()
