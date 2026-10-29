#!/usr/bin/env python3
"""OLT-005: Genesis 1 source-first token and lemma review dossier.

Does not generate an unverified English translation. All 434 source tokens and
their imported morphology remain visible, including prefixes and special IDs.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/quality"

OWNER_LOCKS={"1254 a":("bara","shape"),"6213 a":("asah","make"),"7549":("raqia","firmament")}
EXPECTED={"bara":5,"asah":7,"raqia":9}
GATE_STATUS="SOURCE_CROSSWALKED_ENGLISH_NOT_INDEPENDENTLY_REVIEWED"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def stream(path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():yield json.loads(line)

def generate(genesis, crosswalks):
    if genesis["status"]!="IMPORTED_SOURCE_MORPHOLOGY_NOT_INDEPENDENTLY_REVIEWED":
        raise ValueError("Unexpected source scope or false verified claim")
    verse_ids=[v["verse"] for v in genesis["verses"]]
    if verse_ids!=["Gen.1."+str(n) for n in range(1,32)]:
        raise ValueError("Genesis 1 verses missing or reordered")
    index={r["source_exact_lemma"]:r for r in crosswalks}
    if len(index)!=len(crosswalks):
        raise ValueError("Duplicate crosswalk source IDs")
    token_rows=[]
    unique=defaultdict(lambda:{"tokens":[],"verse_refs":set(),"source_forms":set(),
                                "wayyiqtol_occurrences":0})
    counts=Counter()
    wa=0
    nonlexical=Counter()
    unknown=[]
    for verse in genesis["verses"]:
        for tok in verse["tokens"]:
            keys=[p["exact_key"] for p in tok["lemma_parts"]
                  if p["kind"] in ("LEXEME","LEXEME_FLAGGED")]
            nonlex=[p["raw"] for p in tok["lemma_parts"]
                    if p["kind"] not in ("LEXEME","LEXEME_FLAGGED")]
            for p in nonlex:nonlexical[p]+=1
            xrefs=[]
            for key in keys:
                record=index.get(key)
                if record is None:
                    unknown.append({"token":tok["id"],"lemma":key})
                else:
                    xrefs.append({"key":key,"index_status":record["status"],
                                  "lexical_index_ids":record["verified_existing_lexical_entry_ids"],
                                  "bdb_ref_ids":sorted({id_ for x in record["lexical_xrefs"] for
                                                         id_ in x["bdb_status"]["found"]}),
                                  "strong_ref_ids":sorted({id_ for x in record["lexical_xrefs"] for
                                                            id_ in x["strong_status"]["found"]})})
                d=unique[key]
                d["tokens"].append(tok["id"])
                d["verse_refs"].add(verse["verse"])
                d["source_forms"].add(tok["hebrew"])
                if tok["wayyiqtol"]:d["wayyiqtol_occurrences"]+=1
                if key in OWNER_LOCKS:
                    counts[OWNER_LOCKS[key][0]]+=1
            wa+=int(tok["wayyiqtol"])
            token_rows.append({
                "verse":verse["verse"],
                "source_token_id":tok["id"],
                "ordinal":tok["ordinal"],
                "pointed_source_word":tok["hebrew"],
                "source_lemma_raw":tok["lemma_raw"],
                "source_morphology_raw":tok["morph_raw"],
                "exact_lexemes":keys,
                "nonlexical_prefix_or_other":nonlex,
                "source_tagged_wayyiqtol":tok["wayyiqtol"],
                "direct_source_xrefs":xrefs,
                "approved_english_base_candidates":[{"seed_id":OWNER_LOCKS[key][0],
                                                     "english_base":OWNER_LOCKS[key][1]}
                                                    for key in keys if key in OWNER_LOCKS],
                "approved_english_surface":None,
                "source_review":"UNREVIEWED",
                "word_alignment":"NOT_TRANSLATED",
                "cross_reference_links":"NOT_REVIEWED",
            })
    if len(token_rows)!=434:raise ValueError("Source word count changed "+str(len(token_rows)))
    if wa!=50:raise ValueError("Wayyiqtol count changed "+str(wa))
    if dict(counts)!=EXPECTED:raise ValueError("Owner seed mismatch: "+str(dict(counts)))
    if unknown:raise ValueError("Source ID crosswalk coverage incomplete: "+str(unknown[:10]))
    lexemes=[]
    for key,rec in sorted(unique.items(),key=lambda r:(-len(r[1]["tokens"]),r[0])):
        c=index[key]
        lexemes.append({
            "source_exact_lemma":key,
            "genesis_1_occurrence_count":len(rec["tokens"]),
            "verse_references":sorted(rec["verse_refs"],key=lambda v:int(v.split(".")[-1])),
            "source_word_token_ids":rec["tokens"],
            "observed_pointed_spellings":sorted(rec["source_forms"]),
            "source_tagged_wayyiqtol_count":rec["wayyiqtol_occurrences"],
            "source_crosswalk_status":c["status"],
            "lexical_index_ids":c["verified_existing_lexical_entry_ids"],
            "bdb_explicit_dictionary_refs":sorted({id_ for x in c["lexical_xrefs"] for
                                                    id_ in x["bdb_status"]["found"]}),
            "strong_explicit_dictionary_refs":sorted({id_ for x in c["lexical_xrefs"] for
                                                       id_ in x["strong_status"]["found"]}),
            "owner_approved_english_family":OWNER_LOCKS[key][1] if key in OWNER_LOCKS else None,
            "owner_lexicon_seed_id":OWNER_LOCKS[key][0] if key in OWNER_LOCKS else None,
            "new_english_choice_status":"NEEDS_RESEARCH_AND_APPROVAL" if key not in OWNER_LOCKS else "OWNER_FAMILY_LOCKED",
            "morphology_review":"EXTERNAL_OSHB_UNREVIEWED",
            "homonym_and_typology_review":"NOT_DONE",
        })
    by_status=Counter(v["source_crosswalk_status"] for v in lexemes)
    outstanding=[{"lemma":v["source_exact_lemma"],"tokens":v["genesis_1_occurrence_count"],
                  "xref_status":v["source_crosswalk_status"]}
                 for v in lexemes if v["source_crosswalk_status"]!="EXACT_AUG_TO_LEXICAL_INDEX"]
    result={
        "status":GATE_STATUS,
        "source":"Pinned OSHB/WLC imported via GitHub Actions",
        "scope":{"verses":31,"source_word_tokens":len(token_rows),
                 "source_tagged_wayyiqtol":wa,
                 "unique_exact_lemma_ids":len(lexemes),
                 "owner_locked_occurrences":dict(counts),
                 "unique_lemma_crosswalk_status":dict(by_status),
                 "unmapped_genesis_1_lexemes":outstanding,
                 "nonlexical_prefix_components":dict(nonlexical)},
        "tokens":token_rows,
        "lexemes":lexemes,
        "publishable":False,
        "not_tested":["English lexical consistency for nonlocked entries",
                      "Independent Hebrew morphological accuracy",
                      "Complete literal English verse rendering",
                      "Footnotes and Christological links",
                      "Final ODT/PDF visual review"],
    }
    return result

def main():
    src=load(DATA/"genesis_01_morphology.json")
    cross=list(stream(DATA/"verified_id_crosswalk.jsonl"))
    obj=generate(src,cross)
    out=DATA/"genesis_01_source_review_dossier.json"
    out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(obj["scope"],ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
