#!/usr/bin/env python3
"""Build a *candidate*, not approved, all-OT OLT lexical join.

Never infer homonym identity from shared Strong number or shared consonants.
Preserve exact OSHB augmented IDs and source dictionary IDs independently.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json
import re

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
TARGET=DATA/"quality"

def loadjson(file):
    return json.loads(file.read_text(encoding="utf-8"))

def jsonl(file):
    with file.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def exact_number_candidate(value):
    """Only safely match an unambiguous dictionary id, no fuzzy semantics."""
    m=re.fullmatch(r"(?:H)?0*(\d{1,5})",value.strip(),re.I)
    return str(int(m.group(1))) if m else None

def build(data_dir=DATA, output=TARGET):
    a=loadjson(data_dir/"quality"/"observed_exact_lemmas.json")["entries"]
    seed=loadjson(ROOT/"lexicon"/"hebrew.json")["entries"]
    source= data_dir/"imported"/"lexicon"
    strong=list(jsonl(source/"strongs.jsonl"))
    lexical=list(jsonl(source/"lexical_index.jsonl"))
    bdb=list(jsonl(source/"bdb.jsonl"))
    augmented=list(jsonl(source/"aug_index.jsonl"))
    sx=defaultdict(list)
    for row in strong:
        n=exact_number_candidate(row.get("id",""))
        if n:
            sx[n].append(row["id"])
    ax=defaultdict(set)
    for row in augmented:
        aug=row.get("aug")
        index_id=row.get("lexical_index_id")
        if aug and index_id:
            ax[aug].add(index_id)
    lx={x["id"] for x in lexical}
    bx={x["id"] for x in bdb}
    dictionary_ids_used=Counter()
    rows=[]
    for row in a:
        key=row["exact_lemma_key"]
        base=row["strong_number"]
        # AugIndex accepts exact augmented tag; never fall back silently when
        # source contains an augmentation or a "+" marker.
        augmented_index_ids=sorted(ax.get(key,[]))
        valid_lex=[x for x in augmented_index_ids if x in lx]
        dictionary_ids_used["strong_exact_id_found" if sx.get(base) else "strong_exact_id_not_found"]+=1
        dictionary_ids_used["augmented_lexical_found" if valid_lex else "augmented_lexical_unresolved"]+=1
        candidates={
            "source_exact_lemma_id":key,
            "strong_base_number":base,
            "source_extension":row.get("extension"),
            "source_marker":row.get("special_marker"),
            "occurrences":row["occurrences_of_component"],
            "dictionary_strongs_candidate_ids":sorted(sx.get(base,[])),
            "dictionary_lexical_index_candidate_ids":valid_lex,
            "unresolved_aug_index_ids":sorted(set(augmented_index_ids)-set(valid_lex)),
            "dictionary_bdb_candidate_ids":[],
            "olt_english_family":None,
            "olt_approved_morphology":None,
            "review_status":"REVIEW_REQUIRED",
            "note":"Candidate joins from exact sources; unreviewed and NOT a certified meaning."
        }
        if row.get("requires_special_marker_review"):
            candidates["manual_flags"]=["SPECIAL_PLUS_MARKER_UNINTERPRETED"]
        rows.append(candidates)
    # Genesis 1 source-lock anchors remain suggestions until independently reviewed:
    approved_conventions={
        "1254 a":{"seed":"bara","base":"shape"},
        "7549":{"seed":"raqia","base":"firmament"}
    }
    seed_lookup={x["id"]:x for x in seed}
    for key,x in approved_conventions.items():
        if x["seed"] not in seed_lookup or seed_lookup[x["seed"]]["english_base"]!=x["base"]:
            raise RuntimeError("Owner lock corrupted: "+key)
    gen=loadjson(data_dir/"quality"/"genesis_01_morphology.json")["verses"]
    # Discover the exact OSHB extension used for asah in Genesis 1.
    # We do NOT merge possible 6213 a / 6213 b homonyms by base number.
    asah_observed=Counter()
    for verse in gen:
        for token in verse["tokens"]:
            for item in token["lemma_parts"]:
                if item["kind"] in ("LEXEME","LEXEME_FLAGGED") and item["strong_number"]=="6213":
                    asah_observed[item["exact_key"]]+=1
    if sum(asah_observed.values())!=7 or len(asah_observed)!=1:
        raise RuntimeError("Ambiguous Genesis asah OSHB exact-key alignment: "+str(dict(asah_observed)))
    asah_exact=next(iter(asah_observed))
    approved_conventions[asah_exact]={"seed":"asah","base":"make"}
    anchors=[]
    counts=Counter()
    for verse in gen:
        for token in verse["tokens"]:
            keys=[p["exact_key"] for p in token["lemma_parts"]
                  if p["kind"] in ("LEXEME","LEXEME_FLAGGED")]
            matches=[(key,approved_conventions[key]) for key in keys if key in approved_conventions]
            for key,link in matches:
                counts[link["seed"]]+=1
                anchors.append({
                    "verse":verse["verse"],"source_token_id":token["id"],
                    "hebrew":token["hebrew"],"raw_lemma":token["lemma_raw"],
                    "raw_morph":token["morph_raw"],"exact_lemma":key,
                    "locked_olt_english_base":link["base"],
                    "source_approval":"SOURCE_TAG_IMPORTED_UNREVIEWED",
                    "english_surface":"NOT_TRANSLATED_OR_ALIGNED",
                })
    if counts["bara"]!=5 or counts["asah"]!=7:
        raise RuntimeError("Genesis locked verb family occurrence count changed: "+str(dict(counts)))
    if counts["raqia"]<5:
        raise RuntimeError("Genesis raqia anchors unexpectedly absent")
    report={
        "status":"AUTOMATED_CANDIDATE_JOIN_NOT_LEXICALLY_APPROVED",
        "observed_source_lemma_keys":len(rows),
        "dictionary_entries":{"strongs":len(strong),"lexical_index":len(lexical),
                              "bdb":len(bdb),"augmented":len(augmented)},
        "candidate_id_matching":dict(dictionary_ids_used),
        "bdb_direct_crosswalk_status":"NOT_IMPLEMENTED_NO_GUESSING",
        "genesis_1_owner_lock_candidates":dict(counts),
        "genesis_1_asah_exact_source_key":asah_exact,
        "genesis_1_candidate_token_count":len(anchors),
        "all_english_approval":"NOT_DONE",
        "notes":[
            "A Strong number may have several augmented OSHB lemmas.",
            "The AugIndex and BDB joins must be checked against source XML structure and historical lexical distinctions.",
            "An absent exact AugIndex entry is not silently matched by consonantal similarity.",
            "Source-tagged wayyiqtol is not an independently reviewed tense decision."
        ]
    }
    output.mkdir(parents=True,exist_ok=True)
    with (output/"lexicon_candidates.jsonl").open("w",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
    (output/"genesis_01_owner_lock_anchors.json").write_text(json.dumps({
        "status":"PRELIMINARY_SOURCE_MATCH_NOT_VERIFIED_TRANSLATION",
        "records":anchors},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (output/"lexicon_join_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True))
    return report

if __name__=="__main__":
    build()
