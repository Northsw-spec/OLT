#!/usr/bin/env python3
"""OLT reusable source-first Hebrew verse research engine, NOT translation certification.

The *only* authority for source words/IDs/lemmas/morphology is the pinned
OSHB-derived dossier. Editorial plan supplies unapproved English research
fragments, not invented Hebrew tokens. All source fields are copied verbatim.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/quality/genesis_01_source_review_dossier.json"
CARDS=ROOT/"data/quality/genesis_01_dictionary_study_cards.json"
SEEDS=ROOT/"lexicon/hebrew.json"
PRESENTATION="UNDER_ENGLISH_WORD"

def load(p:Path):
    return json.loads(p.read_text(encoding="utf-8"))

def source_verb_form(raw):
    for part in raw.split("/"):
        if part.startswith(("H","A")):part=part[1:]
        if part.startswith("V") and len(part)>=3:return part[2]
    return None

def untrusted_faux_pass(value):
    return value in {"APPROVED","PUBLISHED","CERTIFIED","VERIFIED_TRANSLATION"}

def check_text(text):
    if re.search(r"\b(?:it|its|itself)\b",text,re.I):
        raise ValueError("OLT prohibition of neutral it in main English text")

def build(plan,original,lexicon,seed):
    begin,end=plan["start_verse"],plan["end_verse"]
    if original["scope"]["source_word_tokens"]!=434 or original["scope"]["unique_exact_lemma_ids"]!=97:
        raise ValueError("Pinned Genesis original-source scope changed")
    if plan.get("status")!="RESEARCH_NOT_APPROVED" or plan.get("publishable") is not False:
        raise ValueError("Plan cannot self-approve or publish")
    if plan.get("presentation")!=PRESENTATION:
        raise ValueError("Homonyms must be below English words, never inline /")
    by_lemma={r["source_exact_lemma_id"]:r for r in lexicon["cards"]}
    if len(by_lemma)!=97:raise ValueError("Source dictionary card inventory changed")
    owner={r["id"]:r["english_base"] for r in seed["entries"] if r.get("status")=="OWNER_LOCKED"}
    for k,value in {"bara":"shape","asah":"make","raqia":"firmament","waw.conj":"and"}.items():
        if owner.get(k)!=value:raise ValueError("Owner word-family lock corrupted: "+k)
    verses_expected=[f"Gen.1.{v}" for v in range(begin,end+1)]
    if [v["reference"] for v in plan["verses"]]!=verses_expected:
        raise ValueError("Unexpected, missing or reordered source verse")
    results=[];num_words=0;num_way=0;non_numeric=[];lemma_seen=set()
    for pv in plan["verses"]:
        ref=pv["reference"]
        tokens=sorted([w for w in original["tokens"] if w["verse"]==ref],key=lambda w:w["ordinal"])
        proposed=pv["proposals"]
        if len(proposed)!=len(tokens):raise ValueError("Original source-token count differs at "+ref)
        check_text(pv["english_research_draft"])
        if untrusted_faux_pass(pv.get("review_status")):raise ValueError("Unauthorized verse approval")
        aligned=[]
        for n,(src,item) in enumerate(zip(tokens,proposed),1):
            if item["source_token_id"]!=src["source_token_id"] or src["ordinal"]!=n:
                raise ValueError(f"Source token ID/order mismatch {ref} token {n}")
            if any(untrusted_faux_pass(item.get(k)) for k in ("status","lexical_review","review_status")):
                raise ValueError("Unauthorized token-level approval")
            gloss=item["english_fragment"]
            check_text(gloss)
            form=source_verb_form(src["source_morphology_raw"])
            if item.get("expect_raw_morph") is not None and item["expect_raw_morph"]!=src["source_morphology_raw"]:
                raise ValueError(f"Exact source morphology changed for {src['source_token_id']}")
            if item.get("expect_lemma") is not None and item["expect_lemma"]!=src["source_lemma_raw"]:
                raise ValueError(f"Exact source lemma changed for {src['source_token_id']}")
            wy=form=="w"
            if wy!=src["source_tagged_wayyiqtol"]:raise ValueError("Source morphological wayyiqtol tag inconsistency")
            if wy:
                if not re.search(r"\b(?:said|was|brought|saw|made|called|separated|set|gave|shaped|blessed)\b",gloss,re.I):
                    raise ValueError("Source wayyiqtol requires English simple-past surface")
                if re.search(r"\b(?:hath|has|had|shall|will)\b",gloss,re.I):
                    raise ValueError("Wayyiqtol wrongly perfect or future")
            if item.get("expect_verb_form") is not None and form!=item["expect_verb_form"]:
                raise ValueError(f"Expected source verb-form differs for {src['source_token_id']}")
            if src["source_lemma_raw"].startswith("c/") and not re.search(r"\band\b",gloss,re.I):
                raise ValueError("Source conjunction was dropped: "+src["source_token_id"])
            exact=src["exact_lexemes"]
            for lem in exact:
                if lem not in by_lemma:raise ValueError("Unlinked original Hebrew lemma "+lem)
                lemma_seen.add(lem)
            if not exact:
                if src["source_lemma_raw"] not in ("b","l") or "Sp" not in src["source_morphology_raw"]:
                    raise ValueError("Unexpected original word without numeric lemma")
                non_numeric.append(src["source_token_id"])
            if "6213 a" in exact and not re.search(r"\b(?:mak(?:e|es|ing)|made)\b",gloss,re.I):
                raise ValueError("Owner asah → make/made enforced even for participles")
            if "7549" in exact and not re.search(r"\bfirmament\b",gloss,re.I):
                raise ValueError("Owner raqia → firmament enforced")
            if "1254 a" in exact and not re.search(r"\b(?:shape|shaped|shaping)\b",gloss,re.I):
                raise ValueError("Owner bara → shape enforced")
            if "853" in exact and src["source_morphology_raw"].endswith("To") and not src["source_morphology_raw"].endswith("Sp3mp") and gloss.strip() and "and" not in gloss.lower():
                raise ValueError("Object-marker source token must have zero independent gloss")
            if src["source_token_id"] in ("01SV6","01J9J") and gloss!="in him":
                raise ValueError("Preposition with 3ms suffix must be kept as in him, never it")
            num_way+=int(wy);num_words+=1
            aligned.append({
                "reference":ref,"ordinal":n,"source_token_id":src["source_token_id"],
                "pointed_hebrew":src["pointed_source_word"],
                "source_lemma_raw":src["source_lemma_raw"],
                "source_morphology_raw":src["source_morphology_raw"],
                "source_verb_form":form,"is_source_tagged_wayyiqtol":wy,
                "original_exact_lemma_ids":exact,
                "dictionary_ids":[{"source_lemma":lem,
                      "strong_ids":[x["id"] for x in by_lemma[lem]["dictionary_refs"]["strong"]],
                      "bdb_ids":[x["id"] for x in by_lemma[lem]["dictionary_refs"]["bdb"]]} for lem in exact],
                "english_fragment_research_only":gloss,
                "independent_morphology_approval":False,
                "english_lexical_approval":False,
                "below_word_homonym_links":{"presentation":PRESENTATION,"approved_links":[]},
                "token_status":"ORIGINAL_SOURCE_ANCHORED_NOT_INDEPENDENTLY_APPROVED"})
        results.append({
            "reference":ref,"source_token_count":len(aligned),
            "source_wayyiqtol_count":sum(x["is_source_tagged_wayyiqtol"] for x in aligned),
            "english_main_research_proposal":pv["english_research_draft"],
            "original_word_alignments":aligned,
            "status":"DRAFT_NOT_PUBLISHED",
        })
    if num_words!=plan["expected_source_words"] or num_way!=plan["expected_wayyiqtol"]:
        raise ValueError("Observed source count or wayyiqtol count changed")
    if sorted(non_numeric)!=sorted(plan.get("expected_non_numeric_source_tokens",[])):
        raise ValueError("Grammar-only original source words unaccounted")
    for note in plan.get("research_notes",[]):
        if note["lemma"] not in lemma_seen or note["reference"] not in verses_expected:
            raise ValueError("Research note lacking source verse or lexical anchor")
        if note["status"] not in ("RESEARCH_ONLY","SOURCE_MORPHOLOGY_UNREVIEWED","OWNER_LOCK"):
            raise ValueError("Claimed certainty in unreviewed research note")
        if note.get("is_homonym") is True and note["status"]!="RESEARCH_ONLY":
            raise ValueError("Unverified homonym falsely promoted")
    return {
        "checkpoint":plan["checkpoint"],"status":"SOURCE_ALIGNED_ENGLISH_RESEARCH_ONLY",
        "project":"Olund's Linked Translation",
        "start_verse":begin,"end_verse":end,
        "source_token_count":num_words,
        "source_wayyiqtol_count":num_way,
        "observed_exact_lemma_ids":len(lemma_seen),
        "non_numeric_grammar_token_ids":non_numeric,
        "owner_lock_checks":["bara=shape","asah=make","raqia=firmament","waw=and"],
        "under_word_homonym_presentation":PRESENTATION,
        "verse_research":results,"research_notes":plan.get("research_notes",[]),
        "full_english_lexicon_approved":False,
        "independent_hebrew_morphology_signed_off":False,
        "publication_status":"BLOCKED",
        "provenance":"Pinned OSHB/WLC original source words and source-linked BDB/Strong dictionary cards; proposal is editorial and unapproved.",
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    data=build(load(args.plan),load(SOURCE),load(CARDS),load(SEEDS))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"checkpoint":data["checkpoint"],"words":data["source_token_count"],
                      "wayyiqtol":data["source_wayyiqtol_count"],
                      "lexemes":data["observed_exact_lemma_ids"],
                      "release":data["publication_status"]},sort_keys=True))
if __name__=="__main__":
    main()
