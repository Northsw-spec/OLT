#!/usr/bin/env python3
"""OLT-016: source-based English lemma review, never independent approval."""
import json
from collections import defaultdict
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data"
def load(p):
    return json.loads(p.read_text(encoding="utf-8"))
def generate(alignment,source_cards,seed):
    if alignment["original_source_word_tokens"]!=434 or alignment["source_verses"]!=31:
        raise ValueError("Whole-chapter original source coverage is missing")
    if alignment["publication_status"]!="BLOCKED":
        raise ValueError("Research falsely marked published")
    cards={x["source_exact_lemma_id"]:x for x in source_cards["cards"]}
    if len(cards)!=97:raise ValueError("Original source card count mismatch")
    approved={x["id"]:x["english_base"] for x in seed["entries"] if x.get("status")=="OWNER_LOCKED"}
    for key,val in {"bara":"shape","asah":"make","raqia":"firmament","waw.conj":"and"}.items():
        if approved.get(key)!=val:raise ValueError("Owner lock corrupted")
    owners={"1254 a":"shape","6213 a":"make","7549":"firmament"}
    groups=defaultdict(list)
    counted=set()
    for v in alignment["genesis_1_research_verses"]:
        for token in v["original_token_alignment"]:
            tid=token["source_token_id"]
            if tid in counted:raise ValueError("Duplicate original word")
            counted.add(tid)
            for lid in token["source_exact_lemma_ids"]:
                if lid not in cards:raise ValueError("Unknown source lemma")
                groups[lid].append({
                    "reference":v["reference"],
                    "token_id":tid,
                    "hebrew":token["original_hebrew"],
                    "raw_morphology":token["original_morphology"],
                    "english_research_fragment":token["english_fragment_research_only"],
                })
    if len(counted)!=434 or len(groups)!=97:
        raise ValueError("Original word and lexical source identity coverage incomplete")
    entries=[]
    for lid,instances in sorted(groups.items(),key=lambda x:(-len(x[1]),x[0])):
        card=cards[lid]
        owner=owners.get(lid)
        if card["owner_english_family"]!=owner:
            raise ValueError("Owner English family does not match lexical source card")
        variants=sorted(set(t["english_research_fragment"] for t in instances))
        entries.append({
            "source_lemma_id":lid,
            "source_token_count":len(instances),
            "source_words":instances,
            "bdb_ids":[x["id"] for x in card["dictionary_refs"]["bdb"]],
            "strong_ids":[x["id"] for x in card["dictionary_refs"]["strong"]],
            "proposed_english_fragments":variants,
            "fragment_variation_may_be_inflection_not_distinct_meaning":len(variants)>1,
            "owner_english_family":owner,
            "english_family_approval":"OWNER_FAMILY_ONLY" if owner else "REQUIRES_EDITORIAL_REVIEW",
            "source_morphology_independent_review":False,
            "homonym_identity_approved":False,
            "homonym_slot":{"placement":"BELOW_ENGLISH_WORD","approved_alternatives":[]},
            "christological_research":"CHECK_WHEN_SOURCE_AND_CANON_SUPPORT",
            "sense_review":"BDB_NESTED_SENSE_SELECTION_PENDING",
        })
    return {
        "checkpoint":"OLT-016",
        "scope":"97_GENESIS_SOURCE_LEMMA_EDITORIAL_QUEUE",
        "source_word_tokens":434,
        "source_lemma_ids":97,
        "owner_locked_families":3,
        "new_english_families_pending":94,
        "lemma_ids_with_multiple_english_fragments":sum(x["fragment_variation_may_be_inflection_not_distinct_meaning"] for x in entries),
        "distinct_english_fragments_do_not_prove_homonyms":True,
        "approved_homonym_links":0,
        "homonym_presentation":"BELOW_ENGLISH_WORD",
        "english_verse_approval":False,
        "all_OT_lexicon_complete":False,
        "publication_status":"BLOCKED",
        "entries":entries,
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=BASE/"research/genesis_01_lexeme_editorial_queue.json")
    a=ap.parse_args()
    obj=generate(load(BASE/"research/genesis_01_complete_research_alignment.json"),
                 load(BASE/"quality/genesis_01_dictionary_study_cards.json"),
                 load(ROOT/"lexicon/hebrew.json"))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:obj[k] for k in ("source_lemma_ids","new_english_families_pending","lemma_ids_with_multiple_english_fragments","publication_status")},sort_keys=True))
if __name__=="__main__":main()
