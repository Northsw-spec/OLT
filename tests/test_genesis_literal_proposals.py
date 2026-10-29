import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from genesis_literal_proposals import source_verse_1,candidate_verse_1,priority_queue,VERSE_PRIMARY,GRAMMAR_ONLY,read

class FirstLexicalProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=read(ROOT/"data/quality/genesis_01_source_review_dossier.json")
        cls.seed=read(ROOT/"lexicon/hebrew.json")
        cls.cards=read(ROOT/"data/quality/genesis_01_dictionary_study_cards.json")
    def test_research_candidate_has_exact_source_alignment(self):
        r=candidate_verse_1(source_verse_1(self.source),self.seed)
        self.assertEqual(len(r["source_alignment"]),7)
        self.assertEqual(len({t["source_token_id"] for t in r["source_alignment"]}),7)
        self.assertFalse(r["publication_status"]=="PUBLISHED")
        self.assertIn("God — He shaped",r["main_english_proposal"])
        self.assertEqual(r["source_alignment"][3]["proposed_english_surface"],"")
        self.assertEqual(r["source_alignment"][5]["proposed_english_surface"],"and")
        self.assertEqual(r["source_alignment"][1]["source_morphology"],"HVqp3ms")
    def test_wayyiqtol_mislabel_blocks(self):
        d=copy.deepcopy(self.source)
        t=next(x for x in d["tokens"] if x["verse"]=="Gen.1.1" and x["ordinal"]==2)
        t["source_tagged_wayyiqtol"]=True
        with self.assertRaisesRegex(ValueError,"wayyiqtol"):
            source_verse_1(d)
    def test_wrong_source_token_blocks(self):
        d=copy.deepcopy(self.source)
        t=next(x for x in d["tokens"] if x["verse"]=="Gen.1.1" and x["ordinal"]==1)
        t["source_token_id"]="invented_id"
        with self.assertRaisesRegex(ValueError,"Source/morph mismatch"):
            source_verse_1(d)
    def test_wrong_lemma_or_hebrew_morph_blocks(self):
        d=copy.deepcopy(self.source)
        t=next(x for x in d["tokens"] if x["verse"]=="Gen.1.1" and x["ordinal"]==2)
        t["source_morphology_raw"]="HC/Vqw3ms"
        with self.assertRaisesRegex(ValueError,"Source/morph mismatch"):
            source_verse_1(d)
    def test_owner_lock_change_blocks(self):
        d=copy.deepcopy(self.seed)
        next(x for x in d["entries"] if x["id"]=="bara")["english_base"]="create"
        with self.assertRaisesRegex(ValueError,"Owner bara"):
            candidate_verse_1(source_verse_1(self.source),d)
    def test_source_count_missing_blocks(self):
        d=copy.deepcopy(self.source)
        d["scope"]["source_word_tokens"]=433
        with self.assertRaisesRegex(ValueError,"434"):
            source_verse_1(d)
    def test_intertext_supplement_not_assigned_to_hebrew_token(self):
        obj=candidate_verse_1(source_verse_1(self.source),self.seed)
        supp=next(x for x in obj["supplied_english_items"] if x["surface"]=="[of His Power]")
        self.assertIsNone(supp["source_token_id"])
        self.assertTrue(supp["included_in_main_english"])
        self.assertEqual(supp["footnote_id"],"gen-1-1-power")
        self.assertIn("[of His Power]",obj["main_english_proposal"])
        self.assertNotIn("[of His Power]",obj["unsupplemented_english_baseline_for_source_comparison"])
    def test_power_note_explains_separate_hebrew_lexemes(self):
        obj=candidate_verse_1(source_verse_1(self.source),self.seed)
        note=next(x for x in obj["footnote_drafts"] if x.get("id")=="gen-1-1-power")
        self.assertEqual(note["anchor"],"[of His Power]")
        self.assertEqual(note["reference"],"Gen.1.1")
        self.assertFalse(note["is_independent_hebrew_lexeme"])
        self.assertEqual(note["evidence_references"],["Gen.49.3","Deut.21.17"])
        self.assertIn("ABSENT from Genesis 1:1",note["english"])
        self.assertIn("separate Hebrew noun",note["english"])
        self.assertEqual(obj["publication_status"],"BLOCKED")
    def test_main_brackets_are_mandatory(self):
        import genesis_literal_proposals as g
        from unittest.mock import patch
        with patch.object(g,"VERSE_PRIMARY",g.VERSE_OPTIONAL):
            with self.assertRaisesRegex(ValueError,"bracketed main text"):
                candidate_verse_1(source_verse_1(self.source),self.seed)
    def test_all_seven_grammar_only_items_are_accounted_for(self):
        q=priority_queue(self.cards,self.source)
        self.assertEqual(q["non_numeric_grammar_only_count"],7)
        proposals=q["non_numeric_grammar_only_review_proposals"]
        self.assertTrue(all(not x["treated_as_numeric_dictionary_lemma"] for x in proposals))
        self.assertEqual({x["proposed_english_surface"] for x in proposals},
                         {"in him","to them","to you"})
    def test_grammar_only_source_discrepancy_fails(self):
        d=copy.deepcopy(self.source)
        x=next(x for x in d["tokens"] if x["source_token_id"]=="01SV6")
        x["source_morphology_raw"]="HR/Sp3mp"
        with self.assertRaisesRegex(ValueError,"Grammar-only source morphology"):
            priority_queue(self.cards,d)

    def test_it_in_grammar_only_proposal_fails(self):
        from unittest.mock import patch
        with patch.dict(GRAMMAR_ONLY, {"01SV6":("Gen.1.11","b","HR/Sp3ms","in it","3rd masculine singular")}):
            with self.assertRaisesRegex(ValueError,"Neutral English pronoun"):
                priority_queue(self.cards,self.source)
    def test_ranked_queue_has_no_94_automatic_english_approvals(self):
        q=priority_queue(self.cards,self.source)
        self.assertEqual(q["all_genesis_1_unique_lemma_ids"],97)
        self.assertEqual(q["new_english_decisions_pending"],94)
        self.assertEqual(len(q["queue"]),97)
        self.assertEqual(sum(x["owner_english_family"] is None for x in q["queue"]),94)
        self.assertTrue(all(x["meaning_and_readability"]=="NOT_APPROVED" for x in q["queue"]))
        self.assertEqual(q["lexeme_component_occurrences"],
                         sum(len(x["exact_lexemes"]) for x in self.source["tokens"]))
        self.assertEqual(q["source_word_tokens_without_numeric_lemma_count"],
                         sum(not x["exact_lexemes"] for x in self.source["tokens"]))
        self.assertEqual(q["source_word_tokens_with_multiple_numeric_lemmas_count"],
                         sum(len(x["exact_lexemes"])>1 for x in self.source["tokens"]))
if __name__=="__main__":
    unittest.main()
