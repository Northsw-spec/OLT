#!/usr/bin/env python3
"""OLT-015: strict FIRST-DRAFT Genesis 1 source research merger (never publication).

Reconciles every original Hebrew token ID from the pinned OSHB/WLC source
with every separately generated OLT-008..014 English research proposal.
Do not invent a token or grant editorial approval by merging data.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse,json,re

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"data/research"
SOURCE=ROOT/"data/quality/genesis_01_source_review_dossier.json"
INPUTS=[
 "genesis_01_verse_01_alignment_proposal.json",
 "genesis_01_verses_02_to_05_research.json",
 "genesis_01_verses_06_to_10_research.json",
 "olt_011_genesis_11_15.json","olt_012_genesis_16_20.json",
 "olt_013_genesis_21_25.json","olt_014_genesis_26_31.json",
]
OUTPUT=DIR/"genesis_01_complete_research_alignment.json"
PREVIEW=ROOT/"genesis/GENESIS_01_SOURCE_RESEARCH_PREVIEW.md"
REFS=[f"Gen.1.{i}" for i in range(1,32)]

def load(path):return json.loads(path.read_text(encoding="utf-8"))

def source_verb_form(raw):
    for segment in raw.split("/"):
        if segment.startswith(("H","A")):segment=segment[1:]
        if segment.startswith("V") and len(segment)>=3:return segment[2]
    return None

def normalized_rows(artifact,index):
    if index==0:
        return [{
            "reference":artifact["reference"],"status":artifact["publication_status"],
            "english":artifact["main_english_proposal"],
            "words":artifact["source_alignment"],"format":0,
            "footnotes":[x for x in artifact["footnote_drafts"] if x.get("id")=="gen-1-1-power"],
        }]
    if index==1:
        return [{
            "reference":x["reference"],"status":artifact["release_status"],
            "english":x["english_main_proposal"],
            "words":x["source_aligned_tokens"],"format":1,
        } for x in artifact["verses"]]
    if index==2:
        return [{
            "reference":x["reference"],"status":artifact["chapter_publication"],
            "english":x["english_main_research_candidate"],
            "words":x["source_tokens"],"format":2,
        } for x in artifact["verses"]]
    return [{
        "reference":x["reference"],"status":artifact["publication_status"],
        "english":x["english_main_research_proposal"],
        "words":x["original_word_alignments"],"format":3,
    } for x in artifact["verse_research"]]

def map_token(word,format_):
    fmt=[
        ("ordinal","pointed_hebrew","source_raw_lemma","source_morphology","proposed_english_surface"),
        ("source_ordinal","pointed_hebrew_word","source_raw_lemma","source_raw_morphology","proposed_english_source_gloss"),
        ("ordinal","pointed_hebrew","raw_lemma","raw_morphology","english_fragment_proposed"),
        ("ordinal","pointed_hebrew","source_lemma_raw","source_morphology_raw","english_fragment_research_only"),
    ][format_]
    return {
        "ordinal":word[fmt[0]],"original_hebrew":word[fmt[1]],
        "original_lemma":word[fmt[2]],"original_morphology":word[fmt[3]],
        "english_research_fragment":word[fmt[4]],
        "source_token_id":word["source_token_id"],
    }

def audit(source,artifacts):
    if len(artifacts)!=7:raise ValueError("Expected exactly seven source research checkpoint files")
    orig=source["tokens"]
    if source["scope"]["source_word_tokens"]!=434 or len(orig)!=434:
        raise ValueError("Wrong pinned original chapter corpus scope")
    originals={x["source_token_id"]:x for x in orig}
    if len(originals)!=434:raise ValueError("Duplicate original source word token ID")
    raw_verses={ref:[] for ref in REFS}
    for x in orig:
        if x["verse"] not in raw_verses:raise ValueError("Original source reference outside Genesis 1")
        raw_verses[x["verse"]].append(x)
    rows=[]
    for i,art in enumerate(artifacts):
        rows.extend(normalized_rows(art,i))
    if [r["reference"] for r in rows]!=REFS:
        raise ValueError("Research checkpoints have missing, duplicate or misordered verses")
    normalized=[]
    seen=set();all_lemmas=set();wy_count=0;grammar_only=[];zero_markers=[]
    for rv in rows:
        ref=rv["reference"];english=rv["english"]
        if rv["status"]!="BLOCKED":raise ValueError("A partial chapter claimed publication approval")
        if re.search(r"\b(?:it|its|itself)\b",english,re.I):
            raise ValueError("Neutral pronoun it found in proposed main English text")
        expected=sorted(raw_verses[ref],key=lambda x:x["ordinal"])
        words=[map_token(t,rv["format"]) for t in rv["words"]]
        if len(words)!=len(expected):raise ValueError("Research source word count differs at "+ref)
        aligned=[]
        for n,(t,src) in enumerate(zip(words,expected),1):
            sid=t["source_token_id"]
            if sid in seen:raise ValueError("Duplicate original source token in research: "+sid)
            seen.add(sid)
            if sid!=src["source_token_id"] or t["ordinal"]!=n:
                raise ValueError("Source token ID/order mismatch: "+ref+":"+str(n))
            if (t["original_hebrew"],t["original_lemma"],t["original_morphology"])!=(
                src["pointed_source_word"],src["source_lemma_raw"],src["source_morphology_raw"]):
                raise ValueError("Original Hebrew/lemma/morphology changed: "+sid)
            if re.search(r"\b(?:it|its|itself)\b",t["english_research_fragment"],re.I):
                raise ValueError("Neutral English it found in individual token alignment")
            way=source_verb_form(src["source_morphology_raw"])=="w"
            if way!=src["source_tagged_wayyiqtol"]:
                raise ValueError("Original source wayyiqtol annotation inconsistent: "+sid)
            wy_count+=int(way)
            if not src["exact_lexemes"]:
                grammar_only.append(sid)
            else:
                all_lemmas.update(src["exact_lexemes"])
            if t["english_research_fragment"]=="":
                if src["source_lemma_raw"].split("/")[-1]!="853" or not src["source_morphology_raw"].endswith("To"):
                    raise ValueError("Missing English fragment for lexical non-object word "+sid)
                zero_markers.append(sid)
            aligned.append({
                "source_token_id":sid,"source_ordinal":n,
                "original_hebrew":t["original_hebrew"],
                "original_lemma":t["original_lemma"],
                "original_morphology":t["original_morphology"],
                "source_wayyiqtol":way,
                "source_exact_lemma_ids":src["exact_lexemes"],
                "english_fragment_research_only":t["english_research_fragment"],
                "english_approved":False,
            })
        normalized.append({
            "reference":ref,
            "source_token_count":len(aligned),
            "source_wayyiqtol_count":sum(x["source_wayyiqtol"] for x in aligned),
            "original_verse_source_hebrew_words":[x["original_hebrew"] for x in aligned],
            "proposed_english_research_text":english,
            "original_token_alignment":aligned,
            "editorial_status":"NOT_INDEPENDENTLY_APPROVED",
            "verse_footnote_proposals":rv.get("footnotes",[]),
        })
    if seen!=set(originals):
        raise ValueError("At least one original source token is missing/duplicated")
    if wy_count!=50:
        raise ValueError("Whole-chapter source-tagged wayyiqtol count mismatch")
    if len(all_lemmas)!=97:
        raise ValueError("Whole-chapter unique lexical source-key coverage mismatch")
    if len(grammar_only)!=7:
        raise ValueError("Whole-chapter nonnumeric grammatical word coverage mismatch")
    if normalized[0]["proposed_english_research_text"]!="In the Beginning [of His Power] God — He shaped the Heavens and the Earth.":
        raise ValueError("Owner Genesis 1:1 bracketed main text is missing")
    power_notes=normalized[0]["verse_footnote_proposals"]
    if len(power_notes)!=1 or power_notes[0].get("id")!="gen-1-1-power" or power_notes[0].get("anchor")!="[of His Power]":
        raise ValueError("Owner Genesis 1:1 verse-footnote anchor missing")
    note=power_notes[0]
    if note.get("is_independent_hebrew_lexeme") is not False or note.get("evidence_references")!=["Gen.49.3","Deut.21.17"]:
        raise ValueError("Footnote must preserve truthful intertextual source status")
    if not all(x in note.get("english","") for x in ("Genesis 49:3","Deuteronomy 21:17","separate Hebrew noun","ABSENT from Genesis 1:1")):
        raise ValueError("Footnote hides that the power lexeme is absent from Hebrew Gen 1:1")
    if not normalized[3]["proposed_english_research_text"].startswith(
       "And God — He saw the light, that [he was] — good."):
        raise ValueError("Owner-approved Genesis 1:4 clause was modified")
    for verse in normalized:
        for word in verse["original_token_alignment"]:
            if "1254 a" in word["source_exact_lemma_ids"] and not re.search(
                r"\b(?:shape|shaped|shaping)\b",word["english_fragment_research_only"],re.I):
                raise ValueError("Bara owner-lock violation in aggregated research")
            if "6213 a" in word["source_exact_lemma_ids"] and not re.search(
                r"\b(?:make|made|making)\b",word["english_fragment_research_only"],re.I):
                raise ValueError("Asah owner-lock violation in aggregated research")
            if "7549" in word["source_exact_lemma_ids"] and not re.search(
                r"\bfirmament\b",word["english_fragment_research_only"],re.I):
                raise ValueError("Raqia owner-lock violation in aggregated research")
    return {
        "project":"Olund's Linked Translation",
        "checkpoint":"OLT-015",
        "status":"FULL_ORIGINAL_TOKEN_RESEARCH_COVERAGE_ONLY",
        "source":"Pinned OSHB/WLC Masoretic words and source-backed lexical IDs",
        "source_verses":len(normalized),"original_source_word_tokens":len(seen),
        "distinct_exact_source_lemma_ids":len(all_lemmas),
        "actual_original_grammar_only_word_tokens":len(grammar_only),
        "original_grammar_only_source_ids":sorted(grammar_only),
        "original_zero_surface_object_markers":len(zero_markers),
        "source_tagged_wayyiqtol_count":wy_count,
        "sources_merged":INPUTS,
        "genesis_1_research_verses":normalized,
        "authoritatively_approved_english_verses":0,
        "non_owner_english_lexical_families_approved":0,
        "independently_audited_morphology":False,
        "actual_homonym_identity_links_approved":0,
        "homonym_presentation_rule":"UNDER_ENGLISH_WORD",
        "final_scholarly_footnotes_done":False,
        "bilingual_odt_pdf_and_layout_inspection_done":False,
        "publication_status":"BLOCKED",
        "statement":"Machine coverage PASS means every source token is represented in research; does NOT mean every English rendering is correct or editorially approved.",
    }

def preview(audit):
    items=[
        "# Genesis 1 — ORIGINAL-SOURCE RESEARCH PREVIEW (NOT APPROVED BIBLE TEXT)",
        "",
        "**WARNING:** The English below is an unapproved research proposal, not a completed Olund's Linked Translation chapter. Source IDs and morphological annotations are machine-audited; English lexical senses, grammatical decisions, footnotes and typography are not independently certified.",
        "",
        "Hebrew word spelling is displayed with OSHB's analytic morpheme separators removed solely for readability; the source data and original separators are preserved unchanged in the JSON alignment.",
        "",
    ]
    for v in audit["genesis_1_research_verses"]:
        hebrew=" ".join(x.replace("/","") for x in v["original_verse_source_hebrew_words"])
        items.extend([
            "### "+v["reference"],
            "",
            "**Masoretic Hebrew:** "+hebrew,
            "",
            "**OLT English research proposal:** "+v["proposed_english_research_text"]+("[^gen-1-1-power]" if v["reference"]=="Gen.1.1" else ""),
            "",
        ])
    power=audit["genesis_1_research_verses"][0]["verse_footnote_proposals"][0]
    items.extend(["---","","**RELEASE BLOCKED.** These paragraphs have no independent philological/owner approval. Homonyms and theological cross-references are not inferred from spelling; no unverified alternatives are displayed inline.","",
                  "[^gen-1-1-power]: "+power["english"],""])
    return "\n".join(items)+"\n"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=OUTPUT)
    ap.add_argument("--preview",type=Path,default=PREVIEW)
    args=ap.parse_args()
    x=audit(load(SOURCE),[load(DIR/p) for p in INPUTS])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    args.preview.parent.mkdir(parents=True,exist_ok=True)
    args.preview.write_text(preview(x),encoding="utf-8")
    print(json.dumps({"verse_count":x["source_verses"],"word_tokens":x["original_source_word_tokens"],
        "source_wayyiqtol":x["source_tagged_wayyiqtol_count"],
        "unique_lemmas":x["distinct_exact_source_lemma_ids"],
        "release":x["publication_status"]},sort_keys=True))
if __name__=="__main__":main()
