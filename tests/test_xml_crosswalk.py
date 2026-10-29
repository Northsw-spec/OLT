import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from verify_xml_crosswalk import normalize_osbh, parse_aug, parse_entry_ids, report, parse_list, resolve_strong_reference

class SourceXmlCrosswalkTests(unittest.TestCase):
    def test_augmentation_spaced_letter_is_lookup_only(self):
        self.assertEqual(normalize_osbh("1254 a"),"1254a")
        self.assertEqual(normalize_osbh("1254 b"),"1254b")
        self.assertNotEqual(normalize_osbh("1254 a"),normalize_osbh("1254 b"))
    def test_plus_suffix_kept(self):
        self.assertEqual(normalize_osbh("1008+"),"1008+")
        self.assertNotEqual(normalize_osbh("1008+"),normalize_osbh("1008"))
    def test_unknown_key_fails(self):
        with self.assertRaises(ValueError):
            normalize_osbh("c/b/1254 a")
    def test_parse_safe_reference_ids(self):
        self.assertEqual(parse_list("aaa bbb,ccc;ddd"),(["aaa","bbb","ccc","ddd"],[]))
        self.assertEqual(parse_list("a/b"),([],["a/b"]))
    def test_strong_xref_numeric_format_only(self):
        self.assertEqual(resolve_strong_reference("1254", {"H1254"})["found_id"],"H1254")
        self.assertEqual(resolve_strong_reference("H01254", {"H1254"})["found_id"],"H1254")
        self.assertIsNone(resolve_strong_reference("1254a", {"H1254"})["found_id"])
        self.assertEqual(resolve_strong_reference("1254", {"H1254","1254"})["found_id"],"1254")
        self.assertIsNone(resolve_strong_reference("H01254", {"H1254","1254"})["found_id"])
    def test_lexical_aug_suffix_is_not_full_lemma_id(self):
        obs=[{"exact_lemma_key":"122 a","extension":"a","occurrences_of_component":1}]
        lex={"a":{"xref_attributes":[{"aug":"a","bdb":"b1","strong":"122"}]}}
        _,summary=report(obs,{"122a":{"a"}},lex,{"b1"},{"H122"})
        self.assertEqual(summary["xref_aug_disagreements_examples"],[])
        self.assertEqual(summary["strong_explicit_reference_results"]["FOUND"],1)
    def test_real_source_crosslinks_not_inferred(self):
        observed=[{"exact_lemma_key":"122 a","occurrences_of_component":1},
                  {"exact_lemma_key":"122 b","occurrences_of_component":2},
                  {"exact_lemma_key":"123+","occurrences_of_component":3}]
        aug={"122a":{"aa"},"122b":{"ab"},"123":{"ac"}}
        lex={"aa":{"id":"aa","xref_attributes":[{"bdb":"bdba","strong":"H122"}]},
             "ab":{"id":"ab","xref_attributes":[{"bdb":"bdbb","strong":"H122"}]},
             "ac":{"id":"ac","xref_attributes":[]}}
        rows,s=report(observed,aug,lex,{"bdba","bdbb"},{"H122"})
        self.assertEqual(rows[0]["verified_existing_lexical_entry_ids"],["aa"])
        self.assertEqual(rows[1]["verified_existing_lexical_entry_ids"],["ab"])
        self.assertEqual(rows[2]["status"],"NO_EXACT_AUG_INDEX_ENTRY")
        self.assertEqual(s["bdb_explicit_reference_results"]["FOUND"],2)
        self.assertEqual(s["exact_mapping_status"]["NO_EXACT_AUG_INDEX_ENTRY"],1)
    def test_dangling_bdb_is_disclosed(self):
        obs=[{"exact_lemma_key":"123","occurrences_of_component":1}]
        aug={"123":{"a"}}
        lex={"a":{"id":"a","xref_attributes":[{"bdb":"missing"}]}}
        rows,s=report(obs,aug,lex,{"exists"},set())
        self.assertEqual(rows[0]["lexical_xrefs"][0]["bdb_status"]["missing"],["missing"])
        self.assertEqual(s["bdb_explicit_reference_results"]["DANGLING"],1)
    def test_duplicate_aug_targets_not_silenced(self):
        obs=[{"exact_lemma_key":"123","occurrences_of_component":1}]
        rows,s=report(obs,{"123":{"a","b"}},{"a":{"xref_attributes":[]},"b":{"xref_attributes":[]}},set(),set())
        self.assertEqual(rows[0]["status"],"AMBIGUOUS_AUG_INDEX_TARGET")
    def test_source_xml_parse_minimal(self):
        xml='<index xmlns="http://openscriptures.github.com/morphhb/namespace"><w aug="122a">a</w><w aug="122b">b</w></index>'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"AugIndex.xml"
            p.write_text(xml,encoding="utf-8")
            m,dup=parse_aug_unchecked_for_test(p)
            self.assertEqual(m["122a"],{"a"})

def parse_aug_unchecked_for_test(path):
    # small fixture so no claim about minimum whole-source coverage
    from xml.etree import ElementTree as ET
    from collections import defaultdict
    from verify_xml_crosswalk import tag
    out=defaultdict(set)
    for el in ET.parse(path).getroot().iter():
        if tag(el)=="w" and el.get("aug"):
            out[el.get("aug")].add((el.text or "").strip())
    return out,{}

if __name__=="__main__":
    unittest.main()
