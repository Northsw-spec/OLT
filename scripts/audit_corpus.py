#!/usr/bin/env python3
"""Source-grounded OLT-003 corpus audit.

Reads every imported OSHB token without altering the primary corpus.
Produces a full distinct lemma-id index, analysis of exceptional annotations,
and exact morphology-tag extraction for Genesis 1.

IMPORTANT: Import/machine validation != independent philological approval.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import json
import re

MORPHOLOGY_FORMS = {
    "p":"QATAL", "q":"SEQUENTIAL_PERFECT", "i":"YIQTOL",
    "w":"WAYYIQTOL", "v":"IMPERATIVE",
    "r":"PARTICIPLE", "s":"PASSIVE_PARTICIPLE",
    "c":"INFINITIVE_CONSTRUCT", "a":"INFINITIVE_ABSOLUTE"
}
LEMMA_PART = re.compile(r"^(\d{1,5})(?:\s+([a-z]))?$")
REFERENCE = re.compile(r"^Gen\.1\.(\d+)$")

def lemma_parts(raw: str):
    """Keep space-separated OSHB homonym letters: 1254 a != 1254 b."""
    parsed=[]
    for i,segment in enumerate(raw.split("/")):
        segment=segment.strip()
        if not segment:
            parsed.append({"position":i,"raw":segment,"kind":"EMPTY"})
            continue
        match=LEMMA_PART.fullmatch(segment)
        if match:
            n=match.group(1)
            letter=match.group(2)
            parsed.append({"position":i,"raw":segment,"kind":"LEXEME",
                           "strong_number":n,"extension":letter,
                           "exact_key":n+(" "+letter if letter else "")})
        else:
            parsed.append({"position":i,"raw":segment,"kind":"PREFIX_OR_OTHER"})
    return parsed

def morphology_parts(raw: str):
    """OSHB is e.g. HC/Vqw3ms or HVqp3ms; w denotes wayyiqtol."""
    output=[]
    lang = raw[0] if raw and raw[0] in ("H","A") else None
    for i, segment in enumerate(raw.split("/")):
        data=segment
        if data and data[0] in ("H","A"):
            data=data[1:]
        obj={"position":i, "raw":segment,"language":lang,
             "part_of_speech":data[:1] or None}
        if data.startswith("V") and len(data)>=3:
            obj.update({"binyan_code":data[1], "verb_form_code":data[2],
                        "verb_form":MORPHOLOGY_FORMS.get(data[2],"UNKNOWN"),
                        "remaining_morphology":data[3:]})
        output.append(obj)
    return output

def scan(path:Path):
    books=sorted(path.glob("*.json"))
    if len(books)!=39:
        raise ValueError(f"Expected exactly 39 imported book files: got {len(books)}")
    count=0
    verse_count=0
    all_lex=Counter()
    forms=Counter()
    prefix=Counter()
    invalid_annotations=Counter()
    langs=Counter()
    same_strongs=defaultdict(set)
    gen=[]
    year_missing=0
    for book in books:
        d=json.loads(book.read_text(encoding="utf-8"))
        if not isinstance(d.get("verses"), list):
            raise ValueError("Book lacks verses: "+book.name)
        for verse in d["verses"]:
            verse_count+=1
            ref=verse["reference"]
            enriched=[]
            for w in verse["words"]:
                count+=1
                L=lemma_parts(w.get("lemma_raw",""))
                M=morphology_parts(w.get("morph_raw",""))
                lexemes=[p for p in L if p["kind"]=="LEXEME"]
                if not lexemes:
                    invalid_annotations[w.get("lemma_raw","")]+=1
                for piece in L:
                    if piece["kind"]=="LEXEME":
                        all_lex[piece["exact_key"]]+=1
                        same_strongs[piece["strong_number"]].add(piece["exact_key"])
                    else:
                        prefix[piece["raw"]]+=1
                lang=M[0]["language"] if M else None
                langs[lang or "UNKNOWN"]+=1
                vforms=[s for s in M if s.get("part_of_speech")=="V"]
                for v in vforms:
                    forms[v["verb_form"]]+=1
                if REFERENCE.fullmatch(ref):
                    enriched.append({
                        "id":w["source_id"],
                        "ordinal":w["ordinal"],
                        "hebrew":w["hebrew"],
                        "lemma_raw":w.get("lemma_raw",""),
                        "lemma_parts":L,
                        "morph_raw":w.get("morph_raw",""),
                        "morph_parts":M,
                        "wayyiqtol":any(v["verb_form"]=="WAYYIQTOL" for v in vforms),
                        "olt_translation":"NOT_YET_ALIGNED",
                        "editorial_status":"SOURCE_TAG_IMPORTED_UNREVIEWED",
                    })
            if REFERENCE.fullmatch(ref):
                gen.append({"verse":ref,"tokens":enriched})
    gen.sort(key=lambda x:int(REFERENCE.fullmatch(x["verse"]).group(1)))
    if len(gen)!=31:
        raise ValueError(f"Genesis 1 only has {len(gen)} verses, expected 31")
    if count!=306785 or verse_count!=23213:
        raise ValueError(f"Source counts changed unexpectedly: {count}, {verse_count}")
    rows=[{
        "exact_lemma_key":key,
        "strong_number":key.split(" ")[0],
        "extension":key.split(" ",1)[1] if " " in key else None,
        "occurrences_of_component":freq,
        "olt_english_family":None,
        "review_status":"NOT_YET_EDITORIALLY_APPROVED",
    } for key,freq in all_lex.items()]
    rows.sort(key=lambda x:(int(x["strong_number"]),x["extension"] or ""))
    genesis_verbs=[(v["verse"],tok) for v in gen for tok in v["tokens"] if tok["wayyiqtol"]]
    ambiguous={n:sorted(keys) for n,keys in same_strongs.items() if len(keys)>1}
    summary={
        "scope":"39_IMPORTED_BOOKS_ALL_SOURCE_TOKENS",
        "editorial_certification":"NOT_PERFORMED",
        "token_count":count,
        "verse_count":verse_count,
        "distinct_exact_lemma_keys":len(rows),
        "strong_numbers_with_multiple_exact_ids":len(ambiguous),
        "multivariant_examples":dict(list(sorted(ambiguous.items(),key=lambda x:int(x[0])))[:30]),
        "source_lemma_without_numeric_component":dict(invalid_annotations),
        "lemma_prefix_or_other_components":dict(prefix),
        "languages_as_tagged":dict(langs),
        "morphology_verb_form_counts":dict(forms),
        "genesis_1_verse_count":len(gen),
        "genesis_1_source_tokens":sum(len(v["tokens"]) for v in gen),
        "genesis_1_wayyiqtol_source_tag_count":len(genesis_verbs),
        "genesis_1_wayyiqtol_source_refs":[{"verse":ref,"token_id":tok["id"],
                                            "raw_morph":tok["morph_raw"],
                                            "hebrew":tok["hebrew"]}
                                           for ref,tok in genesis_verbs],
        "limitations":[
            "Exact lemma keys retain OSHB disambiguating letters, but they are not independently audited senses.",
            "A word token may contain slash-separated prefixes, multiple morphemes and pronominal suffixes.",
            "The numeric lemma index counts observed component occurrences, not unique complete words.",
            "Hebrew vs Aramaic is taken from OSHB morphology tags, not independently verified.",
            "A machine-detected wayyiqtol tag is a source annotation, not independent parse review.",
            "No English translation or Christian typology is certified by this dataset."
        ]
    }
    return rows,gen,summary

def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def run():
    ap=argparse.ArgumentParser()
    ap.add_argument("--books",type=Path,default=Path("data/imported/books"))
    ap.add_argument("--out",type=Path,default=Path("data/quality"))
    args=ap.parse_args()
    rows,gen,summary=scan(args.books)
    write_json(args.out/"corpus_audit.json",summary)
    write_json(args.out/"observed_exact_lemmas.json",{
        "status":"AUTOMATIC_INDEX_UNREVIEWED",
        "entries":rows
    })
    write_json(args.out/"genesis_01_morphology.json",{
        "source":"OSHB_WLC_PINNED",
        "status":"IMPORTED_SOURCE_MORPHOLOGY_NOT_INDEPENDENTLY_REVIEWED",
        "verses":gen
    })
    print(json.dumps({
        "STATUS":"SOURCE_TAG_AUDIT_COMPLETED_NOT_EDITORIAL_CERTIFICATION",
        "tokens":summary["token_count"],
        "verses":summary["verse_count"],
        "exact_lemma_keys":summary["distinct_exact_lemma_keys"],
        "ambiguous_strongs":summary["strong_numbers_with_multiple_exact_ids"],
        "genesis_1_tokens":summary["genesis_1_source_tokens"],
        "genesis_1_wayyiqtol":summary["genesis_1_wayyiqtol_source_tag_count"]
    },ensure_ascii=False))
if __name__=="__main__":
    run()
