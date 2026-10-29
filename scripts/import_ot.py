#!/usr/bin/env python3
"""OLT source corpus importer: factual OT tokens + dictionary records only.

No automatic OLT English translations and NO claim of independent philological signoff.
Uses externally pinned Open Scriptures source snapshots, with CC BY 4.0 attribution.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata as ud
import xml.etree.ElementTree as ET

MORPH_SHA = "3d15126fb1ef74867fc1434be1942e837932691f"
LEX_SHA = "21c9add13bc727d3a951361778e97e3ff7afd1ce"

def tagname(el):
    return el.tag.rsplit("}", 1)[-1]

def plain(element):
    return " ".join("".join(element.itertext()).split()) if element is not None else ""

def first_named(element, name):
    return next((x for x in element if tagname(x) == name), None)

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def json_output(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")

def jsonlines(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in items:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n")

def consonants(word):
    return "".join(c for c in word if "\u05d0" <= c <= "\u05ea")  # do not normalize original

def lex_entries(path, kind):
    root = ET.parse(path).getroot()
    entries = []
    for e in root.iter():
        if tagname(e) != "entry":
            continue
        eid = e.get("id")
        if not eid:
            continue
        head = first_named(e, "w")
        fields = {n: plain(first_named(e, n)) for n in
                  ("source", "meaning", "usage", "def", "pos")}
        entries.append({
            "id": eid, "headword": plain(head),
            "consonants": consonants(plain(head)),
            "transliteration": (head.get("xlit", "") if head is not None else ""),
            "language": (head.get("{http://www.w3.org/XML/1998/namespace}lang", "") if head is not None else ""),
            "pos": (head.get("pos", "") if head is not None else fields["pos"]),
            "fields": {k:v for k,v in fields.items() if v},
            "source": kind, "editorial_review": "IMPORTED_UNREVIEWED",
        })
    return sorted(entries, key=lambda x:x["id"])

def parse_morph(morph_dir, out):
    books = sorted(p for p in morph_dir.glob("*.xml") if p.name != "VerseMap.xml")
    if len(books) != 39:
        raise RuntimeError(f"Expected 39 MT book files; got {len(books)}")
    word_ids=set()
    verse_ids=set()
    lemma_freq=Counter()
    all_headwords=defaultdict(Counter)
    morphology=Counter()
    unmatched_lemma=Counter()
    total=0
    missing_id=0
    missing_morph=0
    digests={}
    for file in books:
        book=file.stem
        digests[file.name]=sha(file)
        root=ET.parse(file).getroot()
        verses=[]
        for verse in root.iter():
            if tagname(verse) != "verse" or "osisID" not in verse.attrib:
                continue
            ref=verse.get("osisID")
            if ref in verse_ids:
                raise RuntimeError("Duplicate OSIS verse " + ref)
            verse_ids.add(ref)
            words=[]
            for ordinal,w in enumerate((e for e in verse.iter() if tagname(e) == "w"),1):
                wid=w.get("id","")
                if not wid:
                    missing_id+=1
                elif wid in word_ids:
                    raise RuntimeError("Duplicate immutable OSHB token id " + wid)
                else:
                    word_ids.add(wid)
                form="".join(w.itertext()).strip()
                lemma=w.get("lemma","")
                morph=w.get("morph","")
                if not morph: missing_morph+=1
                # OSHB may contain multiple semantically independent morpheme
                # segments separated by '/' and supplemental lemma suffixes.
                # DO NOT silently normalize these source annotations.
                numbers=re.findall(r"(?<![0-9])([0-9]{1,5})([a-z]?)",lemma)
                refs=[a+b for a,b in numbers]
                if not refs and lemma: unmatched_lemma[lemma]+=1
                for key in refs:
                    lemma_freq[key]+=1
                    all_headwords[key][consonants(form)]+=1
                if morph: morphology[morph]+=1
                words.append({
                    "source_id":wid, "reference":ref, "ordinal":ordinal,
                    "hebrew":form, "lemma_raw":lemma, "morph_raw":morph,
                    "lemma_numeric_components":refs, "source_status":"IMPORTED_UNREVIEWED",
                })
                total+=1
            verses.append({"reference":ref,"words":words})
        if not verses:
            raise RuntimeError("No OSIS verses found in "+file.name)
        json_output(out/"books"/(book+".json"),{"book":book,"source_commit":MORPH_SHA,"verses":verses})
    if total < 200000 or len(verse_ids)<23000:
        raise RuntimeError(f"Insufficient MT coverage: words={total}, verses={len(verse_ids)}")
    rows=[]
    for identifier, freq in sorted(lemma_freq.items(),key=lambda x:(int(re.match(r"\d+",x[0]).group()),x[0])):
        rows.append({"oshb_numeric_lemma":identifier,
                     "strong_id":"H"+re.match(r"\d+",identifier).group(),
                     "tokens_observed":freq,
                     "observed_consonantal_forms":all_headwords[identifier].most_common(12),
                     "english_olt_translation":None,
                     "editorial_status":"UNREVIEWED_NO_LOCK",
                     "source":"OSHB_word_annotations"})
    jsonlines(out/"lexicon"/"observed_lemmas.jsonl", rows)
    return {
        "books":len(books),"verses":len(verse_ids),
        "word_tokens":total,"word_ids":len(word_ids),
        "source_tokens_missing_id":missing_id,"source_tokens_missing_morph":missing_morph,
        "observed_numeric_lemma_ids":len(rows),
        "unparsed_lemma_tags":dict(unmatched_lemma.most_common(30)),
        "morphological_tag_types":len(morphology),
        "books_sha256":digests,
    }

def parse_lexicon(folder,out):
    paths={name:folder/name for name in
        ("HebrewStrong.xml","LexicalIndex.xml","BrownDriverBriggs.xml","AugIndex.xml")}
    for path in paths.values():
        if not path.is_file():
            raise RuntimeError("Missing lexical source " + str(path))
    all_data={}
    for label,source in (("strongs","HebrewStrong.xml"),("lexical_index","LexicalIndex.xml"),("bdb","BrownDriverBriggs.xml")):
        rows=lex_entries(paths[source],label)
        if not rows:
            raise RuntimeError("Empty source lexical list: "+source)
        jsonlines(out/"lexicon"/(label+".jsonl"),rows)
        all_data[label]=rows
    # Do not manufacture a lexical identity from coincident Hebrew consonants:
    # same spelling only yields a HOMOGRAPH_CANDIDATE.
    homographs=defaultdict(set)
    for row in all_data["strongs"]:
        if row["consonants"]:
            homographs[row["consonants"]].add(row["id"])
    candidate_rows=[
        {"consonants":k, "possible_entry_ids":sorted(v),"status":"AUTO_HOMOGRAPH_CANDIDATE_NOT_PROVEN_HOMONYM"}
        for k,v in homographs.items() if len(v)>1
    ]
    jsonlines(out/"lexicon"/"homograph_candidates.jsonl",sorted(candidate_rows,key=lambda x:x["consonants"]))
    augroot=ET.parse(paths["AugIndex.xml"]).getroot()
    aug=[{"aug":x.get("aug"),"lexical_index_id":plain(x)}
         for x in augroot.iter() if tagname(x)=="w" and x.get("aug")]
    jsonlines(out/"lexicon"/"aug_index.jsonl",aug)
    if len(all_data["strongs"]) < 8000 or len(all_data["lexical_index"])<7000:
        raise RuntimeError("Hebrew dictionary appears incomplete")
    return {
        "strongs":len(all_data["strongs"]),
        "lexical_index":len(all_data["lexical_index"]),
        "bdb":len(all_data["bdb"]),
        "aug_index":len(aug),
        "homograph_candidates":len(candidate_rows),
        "lexical_source_sha256":{k:sha(v) for k,v in paths.items()},
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--morph-dir",type=Path,required=True)
    ap.add_argument("--lexicon-dir",type=Path,required=True)
    ap.add_argument("--out",type=Path,default=Path("data/imported"))
    args=ap.parse_args()
    out=args.out
    out.mkdir(parents=True,exist_ok=True)
    corpus=parse_morph(args.morph_dir,out)
    lex=parse_lexicon(args.lexicon_dir,out)
    manifest={
        "state":"COMPLETE_AUTOMATED_SOURCE_IMPORT_NOT_INDEPENDENT_EDITORIAL_REVIEW",
        "project":"Olund's Linked Translation",
        "source_text":"WLC-based OSHB",
        "morphhb":{"repo":"https://github.com/openscriptures/morphhb","commit":MORPH_SHA},
        "hebrew_lexicon":{"repo":"https://github.com/openscriptures/HebrewLexicon","commit":LEX_SHA},
        "license":{"hebrew_text":"Public Domain","morphology_and_edited_lexicon":"CC BY 4.0"},
        "required_attribution":"Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb",
        "corpus":corpus,"lexicon":lex,
        "hard_limits":{
            "source_word_ids_verification":"AUTOMATIC_UNIQUENESS_ONLY",
            "morphology":"EXTERNAL_TAGS_IMPORTED_UNREVIEWED",
            "lexical_senses":"DICTIONARY_CANDIDATES_UNREVIEWED",
            "owner_approved_english":"HELD_SEPARATELY_IN_lexicon/hebrew.json",
            "genesis_1_publication":"BLOCKED",
        },
    }
    json_output(out/"manifest.json",manifest)
    print(json.dumps({
        "SOURCE_IMPORT_COMPLETED":True,
        "books":corpus["books"],"verses":corpus["verses"],
        "tokens":corpus["word_tokens"],"unique_numeric_lemmas":corpus["observed_numeric_lemma_ids"],
        "strong_entries":lex["strongs"],"lexical_index":lex["lexical_index"],"bdb":lex["bdb"],
        "homograph_candidates":lex["homograph_candidates"],
        "editorial_review":"NOT DONE, NO FALSE PASS"
    },sort_keys=True))
if __name__=="__main__":
    main()
