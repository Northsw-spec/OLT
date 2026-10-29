#!/usr/bin/env python3
"""OLT-007: loss-preserving structured Brown–Driver–Briggs XML import.

This records XML nodes, text, tails and attributes in order, including all nested
senses and citations. It does NOT transform dictionary prose into OLT approval.
"""
from __future__ import annotations
from collections import Counter
import argparse
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
UPSTREAM="21c9add13bc727d3a951361778e97e3ff7afd1ce"

def local_tag(raw):
    return raw.rsplit("}",1)[-1]

def preserve(el):
    return {
        "tag":el.tag, "attrs":dict(el.attrib),
        "text":el.text or "", "tail":el.tail or "",
        "children":[preserve(x) for x in el],
    }

def iter_named(node,name):
    for x in node.iter():
        if local_tag(x.tag)==name:yield x

def import_bdb(source):
    root=ET.parse(source).getroot()
    records=[]
    ids=set()
    tags=Counter()
    for entry in iter_named(root,"entry"):
        key=entry.get("id")
        if not key or key in ids:
            raise ValueError("Duplicate or missing BDB XML entry ID: "+str(key))
        ids.add(key)
        item=preserve(entry)
        for node in entry.iter():tags[local_tag(node.tag)]+=1
        records.append({
            "id":key,
            "xml_tree":item,
            "plain_reading_view":" ".join(" ".join(entry.itertext()).split()),
            "source_provenance":"BrownDriverBriggs.xml",
            "source_version":UPSTREAM,
            "meaning_approval":"IMPORTED_DICTIONARY_EVIDENCE_NOT_OLT_APPROVAL",
        })
    if len(records)<11000:raise ValueError("Not a complete BDB XML source")
    return records,dict(tags)

def index_genesis(cards,records):
    lookup={x["id"]:x for x in records}
    if len(lookup)!=len(records):raise ValueError("BDB ID uniqueness failure")
    links=[]
    referenced=set()
    for card in cards["cards"]:
        key=card["source_exact_lemma_id"]
        refs=card["dictionary_refs"]["bdb"]
        keys=[x["id"] for x in refs]
        missing=[x for x in keys if x not in lookup]
        if missing:raise ValueError("Genesis BDB target not found: "+str(missing))
        referenced.update(keys)
        links.append({
            "source_exact_lemma":key,
            "bdb_entry_ids":keys,
            "source_occurrences":card["genesis_occurrences"],
            "owner_approved_english_family":card["owner_english_family"],
            "source_sense_evidence":[{
                "id":x,
                "structured_xml":lookup[x]["xml_tree"],
                "plain_reading_view":lookup[x]["plain_reading_view"],
                "sense_node_count":sum(1 for v in walk_tree(lookup[x]["xml_tree"]) if local_tag(v["tag"])=="sense"),
                "source_review":"NOT_INDEPENDENTLY_APPROVED"
            } for x in keys],
            "editorial_sense_selection":"PENDING",
            "wordplay_and_christological_links":"NOT_REVIEWED",
        })
    if len(links)!=97:raise ValueError("Expected Genesis 1 97 lemma research cards")
    return links,referenced

def walk_tree(node):
    yield node
    for c in node["children"]:yield from walk_tree(c)

def save_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--cards",type=Path,default=ROOT/"data/quality/genesis_01_dictionary_study_cards.json")
    p.add_argument("--out",type=Path,default=ROOT/"data")
    a=p.parse_args()
    dictionary,counts=import_bdb(a.source)
    cards=json.loads(a.cards.read_text(encoding="utf-8"))
    if cards["status"]!="DICTIONARY_RESEARCH_CARDS_NOT_OLT_ENGLISH_APPROVAL":
        raise ValueError("Translation-card status not recognized")
    genesis,unique=index_genesis(cards,dictionary)
    gz_path=a.out/"imported"/"lexicon"/"bdb_nested.jsonl.gz"
    gz_path.parent.mkdir(parents=True,exist_ok=True)
    with gz_path.open("wb") as dest:
        with gzip.GzipFile(filename="",mode="wb",fileobj=dest,mtime=0) as z:
            for r in sorted(dictionary,key=lambda x:x["id"]):
                z.write((json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8"))
    manifest={
        "source":"Open Scriptures HebrewLexicon/BrownDriverBriggs.xml",
        "source_commit":UPSTREAM,
        "source_sha256":sha256(a.source.read_bytes()).hexdigest(),
        "reproducible_gzip_sha256":sha256(gz_path.read_bytes()).hexdigest(),
        "entries":len(dictionary),
        "node_counts":counts,
        "genesis_1_lexical_cards":len(genesis),
        "genesis_1_distinct_bdb_entries_referenced":len(unique),
        "meaning_status":"DICTIONARY_SENSES_IMPORTED_UNREVIEWED",
        "hebrew_morphology_independent_check":"NOT_DONE",
        "genesis_1_english_translation":"NOT_DONE",
        "genesis_1_release":"BLOCKED",
        "original_nesting_preserved":True,
        "full_source_xml_node_text_tail_and_attributes_preserved":True,
        "record_format":"gzip-compressed UTF8 JSONL; each entry has recursive XML tree",
        "license":"Edited Open Scriptures HebrewLexicon source CC BY 4.0, BDB original source public domain; retain attribution",
    }
    save_json(a.out/"quality"/"bdb_nested_manifest.json",manifest)
    save_json(a.out/"quality"/"genesis_01_bdb_sense_evidence.json",{
        "source":manifest["source"],
        "source_commit":UPSTREAM,
        "status":"STRUCTURED_LEXICAL_EVIDENCE_NOT_ENGLISH_TRANSLATION_APPROVAL",
        "cards":genesis,
    })
    print(json.dumps({k:manifest[k] for k in
       ("entries","genesis_1_lexical_cards","genesis_1_distinct_bdb_entries_referenced","original_nesting_preserved","genesis_1_release")},sort_keys=True))
if __name__=="__main__":
    main()
