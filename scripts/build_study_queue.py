#!/usr/bin/env python3
"""OLT-006: source-first exception triage + Genesis 1 dictionary research cards.

This tool NEVER grants an English translation approval or changes owner locks.
A '+' annotation is kept distinct; a possible base-number link is a lead only.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "quality"
IMPORT = ROOT / "data" / "imported"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def rows(path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
                    encoding="utf-8")

def source_samples(books, exact_keys, cap=6):
    """Collect actual original-script instances, never fabricate an example."""
    from audit_corpus import lemma_parts
    samples=defaultdict(list)
    counts=Counter()
    for p in sorted(books.glob("*.json")):
        book=load(p)
        for v in book["verses"]:
            for word in v["words"]:
                exacts={part["exact_key"] for part in lemma_parts(word.get("lemma_raw",""))
                        if part["kind"] in ("LEXEME","LEXEME_FLAGGED")}
                for exact in exacts.intersection(exact_keys):
                    counts[exact]+=1
                    if len(samples[exact])<cap:
                        samples[exact].append({
                            "verse":v["reference"],
                            "token_id":word["source_id"],
                            "hebrew":word["hebrew"],
                            "lemma_raw":word["lemma_raw"],
                            "morph_raw":word["morph_raw"],
                        })
    return samples,counts

def classify_missing(x, crosswalk_by_key, samples, counts):
    key=x["source_exact_lemma"]
    flagged=key.endswith("+")
    base=key[:-1] if flagged else x["aug_index_key"]
    other=crosswalk_by_key.get(base)
    return {
        "source_exact_lemma":key,
        "source_occurrences_count":x["source_occurrences"],
        "confirmed_source_occurrences":counts.get(key,0),
        "status":"PLUS_MARKER_UNEXPLAINED" if flagged else "AUG_INDEX_KEY_NOT_PRESENT",
        "unresolved_raw_original":key,
        "potential_base_lemma":base if flagged else None,
        "potential_base_source_crosswalk": {
            "source_exact_lemma":base,
            "xref_status":other["status"],
            "lexical_ids":other["verified_existing_lexical_entry_ids"],
        } if flagged and other else None,
        "automatic_merger_permitted":False,
        "requires_original_source_documentation":True,
        "examples":samples.get(key,[]),
        "editorial_status":"RESEARCH_REQUIRED",
    }

def make_card(lemma, xref, strong_by_id, bdb_by_id, owner_map):
    key=lemma["source_exact_lemma"]
    if xref is None:
        raise ValueError("Genesis lemma without verified XML crosswalk: "+key)
    if xref["status"]!="EXACT_AUG_TO_LEXICAL_INDEX":
        raise ValueError("Genesis lemma has unresolved lexical target: "+key)
    strong_ids=sorted({ident for y in xref["lexical_xrefs"]
                        for ident in y["strong_status"]["found"]})
    bdb_ids=sorted({ident for y in xref["lexical_xrefs"]
                     for ident in y["bdb_status"]["found"]})
    missing=[("Strong",i) for i in strong_ids if i not in strong_by_id]
    missing += [("BDB",i) for i in bdb_ids if i not in bdb_by_id]
    if missing:
        raise ValueError("Dictionary references missing actual source entries: "+str(missing[:5]))
    standard_data={
        "strong": [
            {"id":i,"headword":strong_by_id[i]["headword"],
             "transliteration":strong_by_id[i].get("transliteration",""),
             "pos":strong_by_id[i].get("pos",""),
             "source_fields":strong_by_id[i].get("fields",{})}
            for i in strong_ids],
        "bdb":[
            {"id":i,"headword":bdb_by_id[i]["headword"],
             "pos":bdb_by_id[i].get("pos",""),
             "source_fields":bdb_by_id[i].get("fields",{})}
            for i in bdb_ids],
    }
    locked=owner_map.get(key)
    return {
        "source_exact_lemma_id":key,
        "genesis_occurrences":lemma["genesis_1_occurrence_count"],
        "actual_verse_refs":lemma["verse_references"],
        "actual_word_token_ids":lemma["source_word_token_ids"],
        "actual_original_spellings":lemma["observed_pointed_spellings"],
        "source_morphological_wayyiqtol_count":lemma["source_tagged_wayyiqtol_count"],
        "lexical_index_entry_ids":xref["verified_existing_lexical_entry_ids"],
        "dictionary_refs":standard_data,
        "owner_english_family":locked["english_base"] if locked else None,
        "owner_lock_id":locked["id"] if locked else None,
        "candidate_english_from_dictionary":None,
        "editorial_status":"OWNER_LEXICAL_FAMILY_LOCKED_MORPH_REVIEW_PENDING" if locked
                           else "LEXICAL_RESEARCH_REQUIRED",
        "independent_morphology_review":"NOT_DONE",
        "wordplay_homonym_review":"NOT_DONE",
        "canonical_christological_review":"NOT_DONE",
        "modern_readability_review":"NOT_DONE",
        "source_verse_english_alignment":"NOT_DONE",
        "source_dictionary_meaning_is_OLT_translation":False,
    }

def build(root=ROOT, out=None):
    data=root/"data"/"quality"
    imported=root/"data"/"imported"
    out=out or data
    full_crosswalk=list(rows(data/"verified_id_crosswalk.jsonl"))
    indexed={x["source_exact_lemma"]:x for x in full_crosswalk}
    if len(indexed)!=len(full_crosswalk):
        raise ValueError("Duplicate exact lemma ID in verified XML crosswalk")
    unresolved=[x for x in full_crosswalk if x["status"]!="EXACT_AUG_TO_LEXICAL_INDEX"]
    exact={x["source_exact_lemma"] for x in unresolved}
    samples,counts=source_samples(imported/"books",exact)
    cases=[classify_missing(x,indexed,samples,counts) for x in unresolved]
    bad_counts=[x for x in cases
                if x["confirmed_source_occurrences"]!=x["source_occurrences_count"]]
    if bad_counts:
        raise ValueError("Original-text coverage mismatch for "+str(bad_counts[:3]))
    report={
        "scope":"ALL_UNRESOLVED_OBSERVED_SOURCE_LEMMA_KEYS",
        "exact_lemma_keys_total":len(full_crosswalk),
        "exact_identifier_links":len(full_crosswalk)-len(cases),
        "unresolved_count":len(cases),
        "plus_marker_count":sum(1 for x in cases if x["status"]=="PLUS_MARKER_UNEXPLAINED"),
        "missing_aug_count":sum(1 for x in cases if x["status"]=="AUG_INDEX_KEY_NOT_PRESENT"),
        "has_potential_base_lookup_only":sum(1 for x in cases if x["potential_base_source_crosswalk"]),
        "source_examples_recorded":sum(len(x["examples"]) for x in cases),
        "readout_status":"AUTOMATIC_ID_TRIAGE_NOT_DICTIONARY_APPROVAL",
        "plus_marker_semantics":"NOT_YET_DOCUMENTED_IN_PRIMARY_SOURCE",
        "special_lemma_merging_allowed":False,
        "cases":cases,
    }
    if report["exact_lemma_keys_total"]<9000 or report["unresolved_count"]<1:
        raise ValueError("Unexpected corpus/crosswalk source scope")
    genesis=load(data/"genesis_01_source_review_dossier.json")
    if genesis.get("publishable") is not False:
        raise ValueError("Cannot promote a draft to publishable")
    strong={x["id"]:x for x in rows(imported/"lexicon"/"strongs.jsonl")}
    bdb={x["id"]:x for x in rows(imported/"lexicon"/"bdb.jsonl")}
    owner_seeds=load(root/"lexicon"/"hebrew.json")["entries"]
    owner_by_id={x["id"]:x for x in owner_seeds if x["status"]=="OWNER_LOCKED"}
    owner_keys={"1254 a":"bara","6213 a":"asah","7549":"raqia"}
    owner_map={}
    for key,seed in owner_keys.items():
        if seed not in owner_by_id:
            raise ValueError("Missing owner seed "+seed)
        owner_map[key]=owner_by_id[seed]
    cards=[make_card(v,indexed.get(v["source_exact_lemma"]),strong,bdb,owner_map)
           for v in genesis["lexemes"]]
    card_count=Counter(x["editorial_status"] for x in cards)
    if len(cards)!=len({x["source_exact_lemma_id"] for x in cards}):
        raise ValueError("Duplicate Genesis 1 lexeme card")
    result={
        "status":"DICTIONARY_RESEARCH_CARDS_NOT_OLT_ENGLISH_APPROVAL",
        "source":"OSHB exact lemma + source LexicalIndex xrefs to Strong/BDB",
        "verses":genesis["scope"]["verses"],
        "word_tokens":genesis["scope"]["source_word_tokens"],
        "source_lemma_cards":len(cards),
        "review_status_counts":dict(card_count),
        "owner_locks_only":sorted(owner_map),
        "non_owner_english_decisions":"ALL_PENDING",
        "genesis_chapter_publication":"BLOCKED",
        "cards":cards,
    }
    save(out/"unresolved_lexeme_triage.json",report)
    save(out/"genesis_01_dictionary_study_cards.json",result)
    print(json.dumps({
        "all_OT_source_lemma_keys":len(full_crosswalk),
        "unresolved":len(cases),
        "plus_marked":report["plus_marker_count"],
        "missing_aug":report["missing_aug_count"],
        "genesis_1_cards":len(cards),
        "card_types":dict(card_count),
        "english_approved":"OWNER_LOCKS_ONLY",
    },ensure_ascii=False,sort_keys=True))
    return report,result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--out",type=Path,default=None)
    args=ap.parse_args()
    build(args.root,args.out)
