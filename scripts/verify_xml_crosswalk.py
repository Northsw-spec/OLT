#!/usr/bin/env python3
"""OLT-004: authoritative ID crosswalk from pinned Open Scriptures XML.

Only source-asserted links are accepted. No inferred homonym identity, English
translation approval or verse publication permission is generated.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
LEX_COMMIT="21c9add13bc727d3a951361778e97e3ff7afd1ce"
MORPH_COMMIT="3d15126fb1ef74867fc1434be1942e837932691f"
RX_LEMMA=re.compile(r"^([0-9]{1,5})(?:\s+([a-z]))?(\+)?$")
RX_REF=re.compile(r"^[A-Za-z0-9._:-]+$")

def tag(el):
    return el.tag.rsplit("}",1)[-1]

def checksum(path):
    return sha256(path.read_bytes()).hexdigest()

def normalize_osbh(lemma):
    """Keep raw and convert OSHB spacing only: 1254 a -> AugIndex 1254a.
    Plus suffix is NEVER removed: 1008+ is not equivalent to 1008."""
    m=RX_LEMMA.fullmatch(lemma)
    if not m:
        raise ValueError("Nonstandard exact numeric lemma key: "+repr(lemma))
    n,ext,plus=m.groups()
    return n+(ext or "")+(plus or "")

def parse_list(raw):
    """Parse only safe whitespace/comma/semicolon-separated IDs.
    Do not synthesize IDs from ranges or punctuation."""
    if raw is None or not raw.strip():
        return [], []
    tokens=re.split(r"[\s,;]+",raw.strip())
    valid=[];invalid=[]
    for x in tokens:
        if RX_REF.fullmatch(x): valid.append(x)
        elif x: invalid.append(x)
    return sorted(set(valid)),sorted(set(invalid))

def parse_lex_index(path):
    root=ET.parse(path).getroot()
    results={}
    duplicates=[]
    count=0
    for el in root.iter():
        if tag(el)!="entry":continue
        count+=1
        key=el.get("id")
        if not key:
            raise ValueError("LexicalIndex entry without id")
        if key in results:
            duplicates.append(key);continue
        xrefs=[]
        for child in el:
            if tag(child)=="xref":
                xrefs.append(dict(child.attrib))
        results[key]={"id":key,"xref_attributes":xrefs,
                      "headword":next(("".join(x.itertext()).strip() for x in el if tag(x)=="w"),""),
                      "source":"LexicalIndex.xml",
                      "review":"UNREVIEWED"}
    if duplicates:raise ValueError("Duplicate LexicalIndex ID: "+str(duplicates[:10]))
    if count < 9000:raise ValueError("Insufficient LexicalIndex entries: "+str(count))
    return results

def parse_aug(path):
    root=ET.parse(path).getroot()
    out=defaultdict(set)
    duplicates=Counter()
    for w in root.iter():
        if tag(w)=="w" and w.get("aug"):
            value="".join(w.itertext()).strip()
            if not value:raise ValueError("Empty AugIndex target: "+str(w.get("aug")))
            key=w.get("aug")
            duplicates[key]+=1
            out[key].add(value)
    if len(out)<9000:raise ValueError("Insufficient AugIndex keys: "+str(len(out)))
    return out, {k:v for k,v in duplicates.items() if v>1}

def parse_entry_ids(path):
    root=ET.parse(path).getroot()
    entries=set()
    for el in root.iter():
        if tag(el)=="entry":
            key=el.get("id")
            if key:
                if key in entries:raise ValueError("Duplicate dictionary entry ID: "+key)
                entries.add(key)
    return entries

def report(observed,aug,lex_index,bdb_ids,strong_ids):
    rows=[]
    status_counts=Counter()
    bdb_reference_status=Counter()
    strong_reference_status=Counter()
    bad_xref_samples=[]
    mismatched_direct_aug=[]
    for r in observed:
        raw=r["exact_lemma_key"]
        norm=normalize_osbh(raw)
        targets=sorted(aug.get(norm,set()))
        good=[t for t in targets if t in lex_index]
        missing=[t for t in targets if t not in lex_index]
        if not targets:
            status="NO_EXACT_AUG_INDEX_ENTRY"
        elif missing:
            status="DANGLING_LEXICAL_TARGET"
        elif len(good)!=1:
            status="AMBIGUOUS_AUG_INDEX_TARGET"
        else:
            status="EXACT_AUG_TO_LEXICAL_INDEX"
        status_counts[status]+=1
        refs=[]
        for target in good:
            v=lex_index[target]
            for attrs in v["xref_attributes"]:
                parsed={}
                for field in ("bdb","strong","aug","twot"):
                    ids,invalid=parse_list(attrs.get(field))
                    parsed[field]={"raw":attrs.get(field), "ids":ids,"unparsed":invalid}
                    if invalid and len(bad_xref_samples)<35:
                        bad_xref_samples.append({"key":raw,"entry":target,"field":field,"unparsed":invalid})
                # BDB/Strong references must resolve to actual entry IDs; do not
                # use mere printed Strong numbers or Hebrew consonants to fill gaps.
                parsed["bdb_status"]={
                    "found":[x for x in parsed["bdb"]["ids"] if x in bdb_ids],
                    "missing":[x for x in parsed["bdb"]["ids"] if x not in bdb_ids]}
                parsed["strong_status"]={
                    "found":[x for x in parsed["strong"]["ids"] if x in strong_ids],
                    "missing":[x for x in parsed["strong"]["ids"] if x not in strong_ids]}
                for id_ in parsed["bdb_status"]["found"]:bdb_reference_status["FOUND"]+=1
                for id_ in parsed["bdb_status"]["missing"]:bdb_reference_status["DANGLING"]+=1
                for id_ in parsed["strong_status"]["found"]:strong_reference_status["FOUND"]+=1
                for id_ in parsed["strong_status"]["missing"]:strong_reference_status["DANGLING"]+=1
                if parsed["aug"]["ids"] and norm not in parsed["aug"]["ids"] and len(mismatched_direct_aug)<35:
                    mismatched_direct_aug.append({"key":raw,"aug_normalized":norm,"entry":target,"xref_aug":parsed["aug"]["raw"]})
                refs.append(parsed)
        row={
            "source_exact_lemma":raw,
            "aug_index_key":norm,
            "aug_index_target_lexical_ids":targets,
            "verified_existing_lexical_entry_ids":good,
            "dangling_lexical_entry_ids":missing,
            "lexical_xrefs":refs,
            "source_occurrences":r["occurrences_of_component"],
            "status":status,
            "english_olt_approved":False,
            "source_editorial_review":"NOT_INDEPENDENTLY_REVIEWED"
        }
        rows.append(row)
    summary={
        "scope":"ALL_OBSERVED_EXACT_LEMMA_COMPONENT_IDENTIFIERS",
        "source_lexicon_commit":LEX_COMMIT,
        "source_morphhb_commit":MORPH_COMMIT,
        "observed":len(rows),
        "aug_index_keys":len(aug),
        "lexical_index_entries":len(lex_index),
        "bdb_entry_ids":len(bdb_ids),
        "strong_entry_ids":len(strong_ids),
        "exact_mapping_status":dict(status_counts),
        "bdb_explicit_reference_results":dict(bdb_reference_status),
        "strong_explicit_reference_results":dict(strong_reference_status),
        "duplicate_aug_key_counts":{k:v for k,v in sorted(aug.items()) if len(v)>1},
        "xref_unparsed_examples":bad_xref_samples,
        "xref_aug_disagreements_examples":mismatched_direct_aug,
        "release_status":"BLOCKED_NOT_EDITORIALLY_REVIEWED",
        "meaning_status":"NOT_APPROVED",
        "notes":[
            "Spaces before a letter on OSHB exact IDs are removed ONLY for documented AugIndex key comparison.",
            "Plus markers are not stripped or equated to unmarked IDs.",
            "The candidate count concerns source identity, not approved English meanings.",
            "BDB/Strong IDs are validated using explicit LexicalIndex xref attributes.",
            "Every absent or dangling reference remains unresolved; no homonym meaning inferred.",
        ],
    }
    return rows,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--observed",type=Path,default=ROOT/"data/quality/observed_exact_lemmas.json")
    p.add_argument("--output",type=Path,default=ROOT/"data/quality")
    args=p.parse_args()
    names=("AugIndex.xml","LexicalIndex.xml","BrownDriverBriggs.xml","HebrewStrong.xml")
    files={name:args.source/name for name in names}
    for name,path in files.items():
        if not path.is_file():raise FileNotFoundError(str(path))
    exacts=json.loads(args.observed.read_text(encoding="utf-8"))["entries"]
    lex_index=parse_lex_index(files["LexicalIndex.xml"])
    augmented,dupes=parse_aug(files["AugIndex.xml"])
    bdb_ids=parse_entry_ids(files["BrownDriverBriggs.xml"])
    strong_ids=parse_entry_ids(files["HebrewStrong.xml"])
    rows,summary=report(exacts,augmented,lex_index,bdb_ids,strong_ids)
    summary["aug_duplicate_source_keys"]=dupes
    summary["source_sha256"]={name:checksum(path) for name,path in files.items()}
    if len(rows)<9000:raise ValueError("Insufficient observed rows")
    if sum(summary["exact_mapping_status"].values())!=len(rows):
        raise ValueError("Mapping coverage accounting mismatch")
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"verified_id_crosswalk.jsonl").write_text(
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows),encoding="utf-8")
    (args.output/"verified_id_crosswalk_report.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:summary[k] for k in
        ("observed","exact_mapping_status","bdb_explicit_reference_results","strong_explicit_reference_results","release_status")},sort_keys=True))

if __name__=="__main__":
    main()
