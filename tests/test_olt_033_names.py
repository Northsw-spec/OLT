"""OLT-033: owner name-underwords are tracked, but not false lexical facts."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_olt_033_names import verify

class OLT033(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
        cls.p=read("data/policy/olt_name_underword_policy.json")
        cls.r=read("lexicon/name_underwords.json")
        cls.lex=read("lexicon/hebrew.json")
        cls.v=read("data/research/genesis_01_verse_01_alignment_proposal.json")
        cls.old=read("data/policy/olt_underword_overrides.json")

    def check(self,p=None,r=None,lex=None,v=None,old=None):
        return verify(p if p is not None else self.p,r if r is not None else self.r,
                      lex if lex is not None else self.lex,v if v is not None else self.v,
                      old if old is not None else self.old)

    def test_current_registry_and_name_policy_are_uncertified(self):
        self.assertIsNone(self.check())
        self.assertEqual(self.r["record_count"],10)
        self.assertEqual(self.r["publication_status"],"BLOCKED")

    def test_corrections_are_exact_and_old_elohim_phrase_absent(self):
        by_id={x["id"]:x for x in self.r["entries"]}
        self.assertEqual(by_id["elohim-mighty-governance"]["owner_requested_underword"],"Mighty Governance")
        self.assertEqual(by_id["noah-rest"]["owner_requested_underword"],"Rest")
        self.assertNotIn("Mighty Powers",json.dumps(self.r,ensure_ascii=False))
        self.assertEqual(by_id["elohim-mighty-governance"]["verified_olt_source_token_ids"],["01TyA"])

    def test_real_noah_source_distinction_not_lexical_conflation(self):
        noah=next(x for x in self.r["entries"] if x["id"]=="noah-rest")
        self.assertIn("נוח",noah["note"])
        self.assertIn("נחם",noah["note"])
        self.assertFalse(noah["meaning_certified"])

    def test_reject_global_unverified_publication(self):
        x=copy.deepcopy(self.r);x["publication_status"]="PUBLISHED"
        with self.assertRaisesRegex(ValueError,"approval"):self.check(r=x)

    def test_reject_unverified_automatic_rendering(self):
        x=copy.deepcopy(self.r)
        next(a for a in x["entries"] if a["id"]=="noah-rest")["lexical_automatic_render"]=True
        with self.assertRaisesRegex(ValueError,"certified"):self.check(r=x)

    def test_reject_wrong_god_underword_and_old_phrase(self):
        x=copy.deepcopy(self.r)
        next(a for a in x["entries"] if a["id"]=="elohim-mighty-governance")["owner_requested_underword"]="Mighty Powers"
        with self.assertRaisesRegex(ValueError,"owner-specified"):self.check(r=x)

    def test_reject_missing_noah(self):
        x=copy.deepcopy(self.r);x["entries"]=[a for a in x["entries"] if a["id"]!="noah-rest"]
        with self.assertRaisesRegex(ValueError,"initial candidate"):self.check(r=x)

    def test_reject_missing_noah_wordplay_distinction(self):
        x=copy.deepcopy(self.r)
        next(a for a in x["entries"] if a["id"]=="noah-rest")["note"]="Noah means comfort"
        with self.assertRaisesRegex(ValueError,"distinct"):self.check(r=x)

    def test_reject_unpinned_nt_source_marked_verified(self):
        x=copy.deepcopy(self.r);x["nt_source_edition_pinned"]=True
        with self.assertRaisesRegex(ValueError,"NT"):self.check(r=x)

    def test_reject_shiloh_sense_merge(self):
        x=copy.deepcopy(self.r)
        t=next(a for a in x["entries"] if a["id"]=="shiloh-genesis-title")
        p=next(a for a in x["entries"] if a["id"]=="shiloh-place-rest")
        t["lexical_reference_ids"]=p["lexical_reference_ids"]
        with self.assertRaisesRegex(ValueError,"different records"):self.check(r=x)

    def test_reject_missing_elohim_token_anchor(self):
        x=copy.deepcopy(self.v)
        next(a for a in x["source_alignment"] if a["source_token_id"]=="01TyA")["exact_lemma_id"]="WRONG"
        with self.assertRaisesRegex(ValueError,"source token"):self.check(v=x)

    def test_reject_globalized_genesis_in_with(self):
        x=copy.deepcopy(self.old);x["underwords"].append(copy.deepcopy(x["underwords"][0]))
        with self.assertRaisesRegex(ValueError,"unique"):self.check(old=x)

    def test_reject_missing_etymological_evidence(self):
        x=copy.deepcopy(self.r)
        x["entries"][0]["evidence"]=[]
        with self.assertRaisesRegex(ValueError,"evidence"):self.check(r=x)

if __name__=="__main__":unittest.main()
