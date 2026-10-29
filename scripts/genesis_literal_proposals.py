#!/usr/bin/env python3
"""OLT-008: source-aligned lexical review, Genesis 1:1; ranked review queue.

Builds a RESEARCH PROPOSAL only. Never calls a verse published or independently
reviewed. Actual token IDs, lemma IDs and morph tags are validated against the
already pinned OSHB/WLC source dossier. Owner locks are never overwritten.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]

# Independently investigated against full OSHB source and Hebrew grammar:
GEN_1_1 = [
    ("01xeN", 1, "7225", "b/7225", "HR/Ncfsa", "In the Beginning",
     "RESEARCH_PROPOSAL"),
    ("01Nvk", 2, "1254 a", "1254 a", "HVqp3ms", "shaped",
     "OWNER_LOCKED_ENGLISH_FAMILY"),
    ("01TyA", 3, "430", "430", "HNcmpa", "God",
     "RESEARCH_PROPOSAL"),
    ("01vuQ", 4, "853", "853", "HTo", "",
     "NO_ENGLISH_SURFACE_DIRECT_OBJECT_MARKER"),
    ("01TSc", 5, "8064", "d/8064", "HTd/Ncmpa", "the Heavens",
     "RESEARCH_PROPOSAL"),
    ("01k5P", 6, "853", "c/853", "HC/To", "and",
     "PREFIX_AND_OBJECT_MARKER_WITH_ZERO_ENGLISH_OBJECT_MARKER"),
    ("01nPh", 7, "776", "d/776", "HTd/Ncbsa", "the Earth",
     "RESEARCH_PROPOSAL"),
]
VERSE_PRIMARY = "In the Beginning God — He shaped the Heavens and the Earth."
VERSE_OPTIONAL = "In the Beginning [of His Power] God — He shaped the Heavens and the Earth."
EXPECTED_GENESIS_LEMMAS = 97
EXPECTED_GENESIS_TOKENS = 434

# Grammatical tokens without a numeric Strong/augmented lemma. The original
# source annotates these as preposition + pronominal suffix, never omitted words.
GRAMMAR_ONLY = {
    "01SV6":("Gen.1.11","b","HR/Sp3ms","in him","3rd masculine singular"),
    "01J9J":("Gen.1.12","b","HR/Sp3ms","in him","3rd masculine singular"),
    "01ypu":("Gen.1.28","l","HR/Sp3mp","to them","3rd masculine plural"),
    "01pAw":("Gen.1.29","l","HR/Sp2mp","to you","2nd masculine plural"),
    "01884":("Gen.1.29","b","HR/Sp3ms","in him","3rd masculine singular"),
    "01wEr":("Gen.1.29","l","HR/Sp2mp","to you","2nd masculine plural"),
    "01teU":("Gen.1.30","b","HR/Sp3ms","in him","3rd masculine singular"),
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def source_verse_1(dossier):
    if dossier.get("scope",{}).get("source_word_tokens")!=EXPECTED_GENESIS_TOKENS:
        raise ValueError("Incomplete source dossier: expected 434 Genesis 1 word tokens")
    rows=[x for x in dossier["tokens"] if x["verse"]=="Gen.1.1"]
    if len(rows)!=7:raise ValueError("Gen 1:1 source token count changed")
    rows=sorted(rows,key=lambda x:x["ordinal"])
    for actual,expected in zip(rows,GEN_1_1):
        sid,num,lemma,raw,morph,gloss,status=expected
        if (actual["source_token_id"]!=sid or actual["ordinal"]!=num or
            actual["source_lemma_raw"]!=raw or actual["source_morphology_raw"]!=morph or
            actual["exact_lexemes"]!=[lemma]):
            raise ValueError(f"Source/morph mismatch for Genesis 1:1 token {num}: {actual['source_token_id']}")
        if actual["source_review"]!="UNREVIEWED":
            raise ValueError("Unexpected prior human signoff in source-dossier record")
    if rows[1]["source_tagged_wayyiqtol"]:
        raise ValueError("Genesis 1:1 bara was incorrectly labelled wayyiqtol")
    return rows

def candidate_verse_1(source, seed):
    owner={x["id"]:x for x in seed["entries"] if x["status"]=="OWNER_LOCKED"}
    if owner["bara"]["english_base"]!="shape":
        raise ValueError("Owner bara=shape lexical family was changed")
    if owner["waw.conj"]["english_base"]!="and":
        raise ValueError("Conjunctional waw lock was changed")
    if re.search(r"\b(?:it|its|itself)\b", VERSE_PRIMARY, re.I):
        raise ValueError("Neutral pronoun in main translation")
    if re.search(r"\b(?:it|its|itself)\b", VERSE_OPTIONAL, re.I):
        raise ValueError("Neutral pronoun in optional candidate")
    if "God — He shaped" not in VERSE_PRIMARY:
        raise ValueError("Mandatory visible named-subject verbal-person form absent")
    aligned=[]
    for r,(_,position,lemma,raw,morph,gloss,status) in zip(source,GEN_1_1):
        d={
            "source_token_id":r["source_token_id"], "ordinal":position,
            "pointed_hebrew":r["pointed_source_word"],
            "source_raw_lemma":raw,"source_morphology":morph,
            "exact_lemma_id":lemma,"proposed_english_surface":gloss,
            "english_choice_status":status,
            "source_morphology_verification":"OSHB_TAG_IMPORTED_NOT_INDEPENDENTLY_SIGNED_OFF",
            "lexical_review":"RESEARCH_DRAFT",
        }
        if position==1:
            d["commentary"]="The prefix b is in; the English article the is idiomatic and not an independent Hebrew definite article in b/reshit. Whether Genesis 1:1 is a temporal dependent clause is debated."
        if position==2:
            d["commentary"]="Qal qatal 3ms (HVqp3ms), not wayyiqtol. OLT owner-lock shaped; English He below is morphological-person visibility, not a second independent pronoun in Hebrew."
        if position==3:
            d["commentary"]="Elohim is morphologically masculine plural; here the finite verb is 3ms, a singular governing construction. God is subject following the verb in Hebrew order."
        if position in (4,6):
            d["commentary"]="The particle et marks a definite direct object; no standalone English word is added for this marker."
        if position==6:
            d["commentary"]+=" The c prefix is conjunction and, as owner-locked."
        aligned.append(d)
    return {
        "reference":"Gen.1.1",
        "status":"SOURCE_ALIGNED_RESEARCH_CANDIDATE_NOT_INDEPENDENTLY_REVIEWED",
        "source_edition":"OSHB_WLC_PINNED",
        "original_hebrew_token_sequence":[x["pointed_hebrew"] for x in aligned],
        "source_token_count":7,
        "source_alignment":aligned,
        "main_english_proposal":VERSE_PRIMARY,
        "owner_intertextual_variant_UNAPPROVED":VERSE_OPTIONAL,
        "supplied_english_items":[
            {"surface":"He","reason":"English exposure of third-person masculine singular inflection in bara","source_token_id":"01Nvk","is_separate_hebrew_word":False},
            {"surface":"the (in the Beginning)","reason":"Idiomatic English determination; Hebrew b/reshit has no independent definite article","source_token_id":"01xeN","is_separate_hebrew_word":False},
            {"surface":"[of His Power]","reason":"INTERTEXTUAL_THEOLOGICAL_SUPPLEMENT; no lexical counterpart in Gen 1:1; investigate Gen 49:3 and Deut 21:17","source_token_id":None,"only_in_optional_variant":True,"is_separate_hebrew_word":False}
        ],
        "english_source_word_order_explanation":"Hebrew verb precedes God; OLT recasts as God — He shaped to expose subject-person while prioritizing the owner's approved typography.",
        "grammatical_issues":[
            "Qatal 3ms in bara, not wayyiqtol. OLT-TENSE-001 is not the grammatical reason for this verse's English past.",
            "Reshit temporal-clause interpretation remains disputed; source annotation alone does not settle the literary syntax.",
            "Elohim noun is morphologically plural; the finite verb is singular.",
            "Et has no independent English lexical surface.",
            "The additional [of His Power] belongs to an INTERPRETIVE NOTES variant, not to the Hebrew base text."
        ],
        "philological_sources":[
            {"url":"https://github.com/openscriptures/morphhb","kind":"PINNED_PRIMARY_WLC_OSHB"},
            {"url":"https://uhg.readthedocs.io/en/latest/particle_direct_object_marker.html","kind":"HEBREW_GRAMMAR"},
            {"url":"https://www.repository.cam.ac.uk/items/bce448c5-e43e-416d-89da-5876ead16bc3","kind":"PEER_REVIEWED_ABSTRACT_RESHIT_SYNTAX"},
            {"url":"https://translation.bible/wp-content/uploads/2024/06/hasel-1971-recent-translations-of-genesis-1-1-a-critical-look.pdf","kind":"PUBLISHED_SYNTAX_DISCUSSION"},
        ],
        "footnote_drafts":[
            {"category":"GRAMMAR","english":"The Hebrew bara is Qal qatal, third-person masculine singular, with its subject Elohim written after the verb. The separate English He makes the inflected subject visible and is not an independent Hebrew word.","editorial_status":"RESEARCH_DRAFT"},
            {"category":"GRAMMAR","english":"The two instances of et mark definite direct objects and do not require independent English lexical equivalents.","editorial_status":"RESEARCH_DRAFT"},
            {"category":"INTERTEXTUAL_HYPOTHESIS","english":"The optional bracketed phrase [of His Power] is absent from Gen 1:1. Compare the separate use of reshit alongside strength/power in Gen 49:3 and Deut 21:17. The relationship is interpretive, not a literal gloss.","editorial_status":"RESEARCH_DRAFT"},
        ],
        "independent_scholarly_review":"NOT_DONE",
        "publication_status":"BLOCKED",
    }

def priority_queue(study_cards,source_dossier):
    cards=study_cards["cards"]
    if len(cards)!=EXPECTED_GENESIS_LEMMAS:
        raise ValueError("Unexpected Genesis unique-lemma scope")
    tok_total=sum(len(x["actual_word_token_ids"]) for x in cards)
    # Numeric lemma COMPONENT count is NOT the number of source words:
    # source-only particles can have empty numerical annotations, and some
    # tokens can contain multiple independent numeric components.
    if source_dossier["scope"]["source_word_tokens"]!=EXPECTED_GENESIS_TOKENS:
        raise ValueError("Actual word tokens have changed")
    all_source_tokens=source_dossier["tokens"]
    if len(all_source_tokens)!=EXPECTED_GENESIS_TOKENS:
        raise ValueError("Actual source word list incomplete")
    lemmas_missing=[{
        "verse":x["verse"],
        "source_token_id":x["source_token_id"],
        "pointed_source_word":x["pointed_source_word"],
        "source_lemma_raw":x["source_lemma_raw"],
        "source_morphology_raw":x["source_morphology_raw"],
        "review_status":"WORD_WITHOUT_NUMERIC_LEMMA_REQUIRES_EXPLICIT_REVIEW"
    } for x in all_source_tokens if not x["exact_lexemes"]]
    multi_lexeme=[{
        "verse":x["verse"],"source_token_id":x["source_token_id"],
        "exact_lexemes":x["exact_lexemes"]
    } for x in all_source_tokens if len(x["exact_lexemes"])>1]
    actual_components=sum(len(x["exact_lexemes"]) for x in all_source_tokens)
    if actual_components!=tok_total:
        raise ValueError("Genesis numeric source component coverage differs from study cards")
    if {x["source_token_id"] for x in lemmas_missing}!=set(GRAMMAR_ONLY):
        raise ValueError("Grammar-only source IDs changed or omitted")
    grammar_only=[]
    for row in lemmas_missing:
        ref,preposition,morph,surface,suffix=GRAMMAR_ONLY[row["source_token_id"]]
        if (row["verse"]!=ref or row["source_lemma_raw"]!=preposition
            or row["source_morphology_raw"]!=morph):
            raise ValueError("Grammar-only source morphology changed for "+row["source_token_id"])
        grammar_only.append({
            **row,
            "grammatical_preposition":"in" if preposition=="b" else "to",
            "pronominal_suffix_morphology":suffix,
            "proposed_english_surface":surface,
            "proposed_english_status":"GRAMMAR_PROPOSAL_NOT_INDEPENDENTLY_APPROVED",
            "treated_as_numeric_dictionary_lemma":False,
            "not_an_omitted_word":True,
        })
    if any(re.search(r"\\b(?:it|its|itself)\\b",r["proposed_english_surface"],re.I)
           for r in grammar_only):
        raise ValueError("Neutral English pronoun in grammar-only source token")

    result=[]
    for x in sorted(cards,key=lambda v:(v["owner_english_family"] is not None,
                                         -v["genesis_occurrences"],
                                         v["source_exact_lemma_id"])):
        key=x["source_exact_lemma_id"]
        result.append({
            "lemma_id":key,
            "genesis_occurrences":x["genesis_occurrences"],
            "source_token_ids":x["actual_word_token_ids"],
            "first_occurrence":x["actual_verse_refs"][0],
            "source_spellings_sample":x["actual_original_spellings"][:5],
            "bdb_ref_ids":[b["id"] for b in x["dictionary_refs"]["bdb"]],
            "strong_ref_ids":[b["id"] for b in x["dictionary_refs"]["strong"]],
            "owner_english_family":x["owner_english_family"],
            "review_status":"OWNER_LOCKED_FAMILY_MORPH_AND_CONTEXT_PENDING" if x["owner_english_family"]
                           else "ENGLISH_LEXICAL_DECISION_PENDING",
            "meaning_and_readability":"NOT_APPROVED",
            "homonym_and_christological_review":"NOT_APPROVED",
        })
    pending=sum(x["owner_english_family"] is None for x in cards)
    if pending!=94:raise ValueError(f"Unexpected non-owner lexical decisions: {pending}")
    return {
        "status":"RESEARCH_QUEUE_NOT_LEXICAL_APPROVAL",
        "all_genesis_1_unique_lemma_ids":len(cards),
        "new_english_decisions_pending":pending,
        "owner_locked_family_lemma_ids":len(cards)-pending,
        "all_actual_genesis_1_word_tokens":EXPECTED_GENESIS_TOKENS,
        "lexeme_component_occurrences":tok_total,
        "source_word_tokens_without_numeric_lemma":lemmas_missing,
        "non_numeric_grammar_only_review_proposals":grammar_only,
        "non_numeric_grammar_only_count":len(grammar_only),
        "source_word_tokens_without_numeric_lemma_count":len(lemmas_missing),
        "source_word_tokens_with_multiple_numeric_lemmas":multi_lexeme,
        "source_word_tokens_with_multiple_numeric_lemmas_count":len(multi_lexeme),
        "all_original_source_token_ids_covered_by_ledger":True,
        "queue":result,
        "notes":"Ranked by observed source-lemma frequency. No dictionary sense automatically becomes an owner-approved English word."
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    args=parser.parse_args()
    root=args.root
    source=read(root/"data/quality/genesis_01_source_review_dossier.json")
    cards=read(root/"data/quality/genesis_01_dictionary_study_cards.json")
    seed=read(root/"lexicon/hebrew.json")
    proposal=candidate_verse_1(source_verse_1(source),seed)
    queue=priority_queue(cards,source)
    out=root/"data/research"
    save(out/"genesis_01_verse_01_alignment_proposal.json",proposal)
    save(out/"genesis_01_97_lemma_review_queue.json",queue)
    print(json.dumps({"source_tokens_verse_1":proposal["source_token_count"],
                      "genesis_1_lemma_ids":queue["all_genesis_1_unique_lemma_ids"],
                      "new_english_families_still_pending":queue["new_english_decisions_pending"],
                      "approval":"NOT_GRANTED","verse_1":"RESEARCH_CANDIDATE"},sort_keys=True))

if __name__=="__main__":
    main()
