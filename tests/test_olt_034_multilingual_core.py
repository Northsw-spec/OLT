"""OLT-034 multilingual engine: source provenance before all locale choices."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from olt_core import (
    ENGINE_VERSION, CONTRACT_VERSION, SourceContractError,
    validate_source, validate_locale, from_genesis_1_verse,
    make_research_packet, build_genesis_1_1_research_packets,
)

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class TestOLT034(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verse=load("data/research/genesis_01_verse_01_alignment_proposal.json")
        cls.names=load("lexicon/name_underwords.json")
        cls.arch=load("data/engine/olt_034_architecture.json")
        cls.master=load("lexicon/english_master_manifest.json")
        cls.locales={x:load("locales/"+x+".json") for x in (
            "en","am","ja","is","zh-Hans","zh-Hant"
        )}
        cls.tokens=from_genesis_1_verse(cls.verse)

    def packet(self,source=None,locale="ja",verse=None,names=None):
        return make_research_packet(source if source is not None else self.tokens[2],
                                    self.locales[locale],verse or self.verse,
                                    names if names is not None else self.names)

    def test_architecture_owner_bound_and_english_never_source(self):
        a=self.arch
        self.assertEqual(a["checkpoint"],"OLT-034")
        self.assertTrue(a["owner_binding_architecture"])
        self.assertEqual(a["canonical_core_repo"],"Northsw-spec/OLT")
        self.assertEqual(a["target_repository_strategy"],"SEPARATE_REPOSITORY_PER_TARGET_LANGUAGE")
        self.assertFalse(a["english_reference_may_fall_back_to_target_translation"])
        self.assertFalse(a["source_original_may_be_replaced_by_english"])
        self.assertIn("ORIGINAL_ARAMAIC_ARC_WHERE_PRESENT_IN_OT",a["source_priority"])
        self.assertEqual(a["bible_release_status"],"BLOCKED")
        self.assertEqual(ENGINE_VERSION,"0.1.0")
        self.assertEqual(CONTRACT_VERSION,"1.0")

    def test_real_source_verse_seven_word_ids_retained_without_english_intermediary(self):
        self.assertEqual(len(self.tokens),7)
        self.assertEqual([r["token_id"] for r in self.tokens],
           ["01xeN","01Nvk","01TyA","01vuQ","01TSc","01k5P","01nPh"])
        self.assertEqual(self.tokens[2]["original_script"],"אֱלֹהִ֑ים")
        self.assertEqual(self.tokens[2]["lemma_id"],"430")
        self.assertEqual(self.tokens[2]["raw_morphology"],"HNcmpa")
        self.assertEqual(self.tokens[2]["edition_status"],"IMPORTED_NOT_INDEPENDENTLY_REVIEWED")

    def test_six_real_locale_profiles_are_untranslated_and_unapproved(self):
        for tag,locale in self.locales.items():
            with self.subTest(tag=tag):
                self.assertEqual(locale["language_tag"],tag)
                self.assertEqual(locale["publication_status"],"BLOCKED")
                self.assertEqual(locale["token_choices"],[])
                self.assertEqual(locale["bible_chapters_translated"],0)
                self.assertTrue(locale["english_is_reference_only"])
                self.assertTrue(locale["source_first"])
                validate_locale(locale)

    def test_packet_contains_english_only_as_optional_reference_not_target_translation(self):
        for tag in self.locales:
            with self.subTest(tag=tag):
                packet=self.packet(locale=tag)
                self.assertEqual(packet["target_language_tag"],tag)
                self.assertEqual(packet["source"]["token_id"],"01TyA")
                self.assertEqual(packet["english_reference"]["candidate_surface"],"God")
                self.assertFalse(packet["english_is_intermediate_source"])
                self.assertIsNone(packet["locale_proposal"])
                self.assertEqual(packet["locale_proposal_status"],"UNTRANSLATED")
                self.assertEqual(packet["publication_status"],"BLOCKED")

    def test_name_underword_is_non_authoritative_and_language_specific_work_remains(self):
        p=self.packet()
        self.assertEqual(p["name_meaning_research"]["name_registry_id"],"elohim-mighty-governance")
        self.assertEqual(p["name_meaning_research"]["english_underword_proposal"],"Mighty Governance")
        self.assertEqual(p["name_meaning_research"]["evidence_category"],
                         "OWNER_CANONICAL_THEOLOGICAL_INTERPRETATION")
        self.assertFalse(p["name_meaning_research"]["lexical_meaning_certified"])
        self.assertIsNone(p["name_meaning_research"]["target_language_word"])
        self.assertFalse(p["name_meaning_research"]["is_a_target_translation"])

    def test_full_genesis_one_research_packets_do_not_claim_verse_translated(self):
        for lang,prof in self.locales.items():
            result=build_genesis_1_1_research_packets(self.verse,prof,self.names)
            with self.subTest(lang=lang):
                self.assertEqual(len(result["packets"]),7)
                self.assertEqual(result["name_underword_candidates"],1)
                self.assertFalse(result["is_translated_scripture"])
                self.assertEqual(result["publication_status"],"BLOCKED")
                self.assertEqual(sum(p["locale_proposal"] is None for p in result["packets"]),7)

    def test_english_master_is_reference_with_olund_locks(self):
        m=self.master
        self.assertEqual(m["language_tag"],"en")
        self.assertFalse(m["all_ot_english_master_lexicon_complete"])
        self.assertFalse(m["nt_greek_master_lexicon_complete"])
        self.assertFalse(m["independent_english_lexicon_approved"])
        self.assertEqual(m["owner_requested_name_meaning_examples"]["God/Elohim"],"Mighty Governance")
        self.assertEqual(m["owner_requested_name_meaning_examples"]["Noah"],"Rest")
        self.assertEqual(m["owner_locked_hebrew_english_families"]["bara"],"shape")
        self.assertEqual(m["publication_status"],"BLOCKED")

    def test_reject_english_as_intermediate_translation_source(self):
        d=copy.deepcopy(self.locales["ja"])
        d["english_is_reference_only"]=False
        with self.assertRaisesRegex(SourceContractError,"intermediate"):validate_locale(d)
        d=copy.deepcopy(self.tokens[2]);d["english"]="God"
        with self.assertRaisesRegex(SourceContractError,"English"):validate_source(d)

    def test_reject_premature_target_locale_publication(self):
        d=copy.deepcopy(self.locales["am"]);d["publication_status"]="PUBLISHED"
        with self.assertRaisesRegex(SourceContractError,"preapproved"):validate_locale(d)
        d=copy.deepcopy(self.tokens[2]);d["publication_status"]="PUBLISHED"
        with self.assertRaisesRegex(SourceContractError,"published"):validate_source(d)

    def test_reject_mixed_original_language_and_corpus(self):
        d=copy.deepcopy(self.tokens[2]);d["source_language"]="grc"
        with self.assertRaisesRegex(SourceContractError,"Incompatible"):validate_source(d)
        d=copy.deepcopy(self.tokens[2]);d["source_language"]="arc";d["corpus"]="NT"
        with self.assertRaisesRegex(SourceContractError,"Incompatible"):validate_source(d)

    def test_nt_greek_requires_actual_pin_before_packets(self):
        d=copy.deepcopy(self.tokens[2])
        d.update(source_language="grc",corpus="NT")
        with self.assertRaisesRegex(SourceContractError,"Greek must be pinned"):validate_source(d)
        # Synthetic input validates structural contract only; it is not a real RP2018 token.
        d["edition_status"]="PINNED_UNDER_REVIEW"
        validate_source(d)

    def test_reject_wrong_original_token_and_lemma_english_reference(self):
        d=copy.deepcopy(self.tokens[2]);d["lemma_id"]="999999"
        with self.assertRaisesRegex(SourceContractError,"exact original source"):self.packet(source=d)

    def test_reject_name_underword_without_source_or_false_signoff(self):
        d=copy.deepcopy(self.names)
        e=next(x for x in d["entries"] if x["id"]=="elohim-mighty-governance")
        e["meaning_certified"]=True
        with self.assertRaisesRegex(SourceContractError,"match or approval"):self.packet(names=d)
        d=copy.deepcopy(self.names)
        e=next(x for x in d["entries"] if x["id"]=="elohim-mighty-governance")
        e["lexical_reference_ids"]=["H999"]
        with self.assertRaisesRegex(SourceContractError,"match or approval"):self.packet(names=d)

    def test_reject_changed_original_hebrew_spelling(self):
        d=copy.deepcopy(self.verse)
        d["source_alignment"][2]["pointed_hebrew"]="WRONG"
        with self.assertRaisesRegex(SourceContractError,"sequence"):from_genesis_1_verse(d)

    def test_reject_source_token_duplication_and_partial_verse(self):
        d=copy.deepcopy(self.verse)
        d["source_alignment"][1]["source_token_id"]=d["source_alignment"][0]["source_token_id"]
        with self.assertRaisesRegex(SourceContractError,"Duplicate"):from_genesis_1_verse(d)
        d=copy.deepcopy(self.verse);d["source_alignment"].pop()
        with self.assertRaisesRegex(SourceContractError,"seven"):from_genesis_1_verse(d)

    def test_reject_false_independent_morphology_certification(self):
        d=copy.deepcopy(self.verse)
        d["source_alignment"][0]["source_morphology_verification"]="INDEPENDENTLY_SIGNED_OFF"
        with self.assertRaisesRegex(SourceContractError,"independently certified"):from_genesis_1_verse(d)

    def test_locale_choice_can_only_be_exact_source_token_bound_draft(self):
        choice={
          "verse_id":"Gen.1.1", "token_id":"01TyA","source_language":"hbo",
          "lemma_id":"430","original_script":"אֱלֹהִ֑ים",
          "language_tag":"ja","target_surface":"RESEARCH PLACEHOLDER","status":"UNREVIEWED_LOCALE_DRAFT"
        }
        d=copy.deepcopy(self.locales["ja"]);d["token_choices"]=[choice]
        p=make_research_packet(self.tokens[2],d,self.verse,self.names)
        self.assertEqual(p["locale_proposal"]["text"],"RESEARCH PLACEHOLDER")
        self.assertEqual(p["locale_proposal_status"],"UNREVIEWED_LOCALE_DRAFT")
        self.assertEqual(p["publication_status"],"BLOCKED")
        d["token_choices"][0]["lemma_id"]="9999"
        with self.assertRaisesRegex(SourceContractError,"original-language token"):
            make_research_packet(self.tokens[2],d,self.verse,self.names)

    def test_reject_duplicate_token_choices_and_wrong_target_tag(self):
        choice={
          "verse_id":"Gen.1.1","token_id":"01TyA","source_language":"hbo",
          "lemma_id":"430","original_script":"אֱלֹהִ֑ים",
          "language_tag":"ja","target_surface":"RESEARCH PLACEHOLDER","status":"UNREVIEWED_LOCALE_DRAFT"
        }
        d=copy.deepcopy(self.locales["ja"]);d["token_choices"]=[choice,copy.deepcopy(choice)]
        with self.assertRaisesRegex(SourceContractError,"Multiple conflicting"):
            make_research_packet(self.tokens[2],d,self.verse,self.names)
        d["token_choices"]=[choice];d["token_choices"][0]["language_tag"]="am"
        with self.assertRaisesRegex(SourceContractError,"language tag"):
            make_research_packet(self.tokens[2],d,self.verse,self.names)

    def test_reject_unverified_locale_approval(self):
        d=copy.deepcopy(self.locales["ja"])
        d["token_choices"]=[{
          "verse_id":"Gen.1.1","token_id":"01TyA","source_language":"hbo",
          "lemma_id":"430","original_script":"אֱלֹהִ֑ים",
          "language_tag":"ja","target_surface":"TEXT","status":"PUBLISHED"
        }]
        with self.assertRaisesRegex(SourceContractError,"independent locale approval"):
            make_research_packet(self.tokens[2],d,self.verse,self.names)

    def test_no_generated_scripts_or_english_mediation_in_cli(self):
        run=subprocess.run([sys.executable,"-m","olt_core.cli","--locale","am"],
            cwd=ROOT,capture_output=True,text=True,check=True)
        payload=json.loads(run.stdout)
        self.assertEqual(payload["target_language_tag"],"am")
        self.assertEqual(payload["source_word_token_count"],7)
        self.assertTrue(all(not p["english_is_intermediate_source"] for p in payload["packets"]))
        self.assertTrue(all(p["locale_proposal"] is None for p in payload["packets"]))
        self.assertEqual(payload["publication_status"],"BLOCKED")

if __name__ == "__main__":
    unittest.main()
