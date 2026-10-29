#!/usr/bin/env python3
"""OLT-010: precise Genesis 1:6–10 source-token research, not release.

Inputs are pinned OSHB-derived source tokens and source-linked BDB/Strong cards.
All English surfaces are proposals; owner lexical locks may not be changed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data/quality"
DEST=ROOT/"data/research/genesis_01_verses_06_to_10_research.json"
# Immutable original token identities and original raw morphology/lemma strings.
# A proposed English fragment may contain a traceable editorial supplement.
# Fields: verse|token_id|OSHB_lemma_raw|OSHB_morph_raw|research_English_fragment.
ROWS=r"""
6|017am|c/559|HC/Vqw3ms|And He said
6|01hh7|430|HNcmpa|God
6|01BsK|1961|HVqj3ms|Let be
6|01fsu|7549|HNcmsa|a firmament
6|018M6|b/8432|HR/Ncmsc|in the midst of
6|01wM5|d/4325|HTd/Ncmpa|the waters
6|01qty|c/1961|HC/Vqi3ms|and let [him] be
6|015gQ|914|HVhrmsa|separating
6|01Xw6|996|HR|between
6|01eHJ|4325|HNcmpa|waters
6|01H6L|l/4325|HR/Ncmpa|to waters
7|01bmv|c/6213 a|HC/Vqw3ms|And He made
7|01FV9|430|HNcmpa|God
7|01Xm1|853|HTo|
7|01UE6|d/7549|HTd/Ncmsa|the firmament
7|01goK|c/914|HC/Vhw3ms|and He separated
7|01CyH|996|HR|between
7|01A4a|d/4325|HTd/Ncmpa|the waters
7|015Pr|834 a|HTr|which
7|01L4k|m/8478|HR/R|from beneath
7|01Mnv|l/7549|HRd/Ncmsa|to the firmament
7|01mwU|c/996|HC/R|and between
7|01tKT|d/4325|HTd/Ncmpa|the waters
7|01NRT|834 a|HTr|which
7|01sRU|m/5921 a|HR/R|from above
7|01Wxq|l/7549|HRd/Ncmsa|to the firmament
7|019qY|c/1961|HC/Vqw3ms|and was
7|01n5f|3651 c|HD|so
8|01YUq|c/7121|HC/Vqw3ms|And He called
8|01fQr|430|HNcmpa|God
8|01L7t|l/7549|HRd/Ncmsa|to the firmament
8|01A74|8064|HNcmpa|Heavens
8|01dNE|c/1961|HC/Vqw3ms|and was
8|01xdF|6153|HNcmsa|evening
8|01AYg|c/1961|HC/Vqw3ms|and was
8|01Ls9|1242|HNcmsa|morning
8|01Snp|3117|HNcmsa|day
8|0187B|8145|HAomsa|second
9|01nLp|c/559|HC/Vqw3ms|And He said
9|01PzC|430|HNcmpa|God
9|01NPq|6960 b|HVNj3mp|Let be gathered
9|01d5m|d/4325|HTd/Ncmpa|the waters
9|01BYa|m/8478|HR/R|from beneath
9|01LJh|d/8064|HTd/Ncmpa|the heavens
9|01tRR|413|HR|unto
9|01Q7E|4725|HNcmsa|place
9|01dv1|259|HAcmsa|one
9|01QwM|c/7200|HC/VNi3fs|and let be seen
9|01a62|d/3004|HTd/Ncfsa|the dry ground
9|01KvD|c/1961|HC/Vqw3ms|and was
9|01GLz|3651 c|HD|so
10|01BU7|c/7121|HC/Vqw3ms|And He called
10|01iy2|430|HNcmpa|God
10|01zQ2|l/3004|HRd/Ncfsa|to the dry ground
10|01Wxx|776|HNcbsa|Earth
10|01jQ8|c/l/4723 c|HC/R/Ncmsc|and to the gathering of
10|01Haa|d/4325|HTd/Ncmpa|the waters
10|01fJN|7121|HVqp3ms|He called
10|019KV|3220|HNcmpa|Seas
10|01F1s|c/7200|HC/Vqw3ms|And He saw
10|01dns|430|HNcmpa|God
10|01GK3|3588 a|HC|that
10|01nRZ|2896 a|HAamsa|good
""".strip()
VERSES={
 "Gen.1.6":"And God — He said: Let a firmament be in the midst of the waters; and let [him] be separating between waters to waters.",
 "Gen.1.7":"And God — He made the firmament, and He separated between the waters which from beneath to the firmament, and between the waters which from above to the firmament; and so was.",
 "Gen.1.8":"And God — He called to the firmament Heavens; and was evening, and was morning: day second.",
 "Gen.1.9":"And God — He said: Let the waters from beneath the heavens be gathered unto place one, and let the dry ground be seen; and so was.",
 "Gen.1.10":"And God — He called to the dry ground Earth, and to the gathering of the waters He called Seas; and God — He saw that — good.",
}
WAY_PAST={"said","made","separated","was","called","saw"}
CONSTRAINED={"6213 a":"make","7549":"firmament"}
NOTES=[
 {"ref":"Gen.1.6","type":"LEXICAL_SOURCE","lemma":"7549","status":"OWNER_LOCK",
  "text":"Raqia is rendered firmament by OLT owner lock. BDB records extended surface; other source-compatible English alternatives are discussed in notes rather than substituted into the main text."},
 {"ref":"Gen.1.6","type":"GRAMMATICAL_CONSTRUCTION","lemma":"1961","status":"RESEARCH",
  "text":"The first yehi is tagged Qal jussive. The following vihi is tagged Qal yiqtol (HC/Vqi3ms) in OSHB, and a volitive English rendering is proposed from context. Neither form is treated as wayyiqtol."},
 {"ref":"Gen.1.6","type":"PARTICIPLE","lemma":"914","status":"RESEARCH",
  "text":"Mavdil is Hiphil masculine singular active participle (HVhrmsa), rendered separating; not English simple-past separated."},
 {"ref":"Gen.1.6","type":"GRAMMATICAL_SUPPLEMENT","lemma":"7549","status":"RESEARCH",
  "text":"[him] in the proposed English phrase let [him] be separating is an English editorial completion referring to masculine firmament; no independently written Hebrew him occurs here."},
 {"ref":"Gen.1.7","type":"OWNER_LOCK","lemma":"6213 a","status":"OWNER_LOCK",
  "text":"Vayyaas is Hiphil? No: OSHB HC/Vqw3ms means Qal wayyiqtol 3ms; OLT must render the asah lexeme as made, never shaped."},
 {"ref":"Gen.1.7","type":"OBJECT_MARKER","lemma":"853","status":"SOURCE_BASED",
  "text":"The et token marks a direct object. Its English standalone lexical gloss is empty but the original token remains in the source alignment."},
 {"ref":"Gen.1.7","type":"TENSE","lemma":"1961","status":"SOURCE_BASED",
  "text":"Vayehi (HC/Vqw3ms) is wayyiqtol and therefore must be simple past. The OLT research clause and so was preserves the past verb without an English neutral it."},
 {"ref":"Gen.1.8","type":"SECOND_DAY","lemma":"8145","status":"RESEARCH",
  "text":"Yom sheni uses the ordinal second, contrasting with Genesis 1:5 yom echad, the cardinal one. The intentionally awkward English day second preserves the source order."},
 {"ref":"Gen.1.9","type":"MORPHOLOGY","lemma":"6960 b","status":"SOURCE_BASED",
  "text":"Yiqqawu carries OSHB HVNj3mp (Niphal jussive 3mp). Let the waters be gathered is a volitive construction and is NOT a past-tense wayyiqtol."},
 {"ref":"Gen.1.9","type":"MORPHOLOGY","lemma":"7200","status":"SOURCE_BASED",
  "text":"Veteraeh is OSHB HC/VNi3fs (Niphal imperfect 3fs), not wayyiqtol. Let the dry ground be seen is a contextual proposal, not an assertion that the verb is morphologically jussive."},
 {"ref":"Gen.1.10","type":"HOMONYM_CAUTION","lemma":"4723 c","status":"RESEARCH",
  "text":"Miqveh here means gathering/collection of the waters. This must not be automatically conflated with other same-consonant terms or with later ritual mikveh solely from spelling."},
 {"ref":"Gen.1.10","type":"TENSE","lemma":"7121","status":"SOURCE_BASED",
  "text":"The first called is OSHB wayyiqtol and the second qara (HVqp3ms) is qatal. Both can use English called but must not be classified as the same Hebrew verb form."},
 {"ref":"Gen.1.10","type":"GENDER_CAUTION","lemma":"2896 a","status":"RESEARCH",
  "text":"Ki tov is literally that good with a verbless adjective phrase. Do not mechanically assign the [he was] completion from Genesis 1:4 to a different subject without grammatical and contextual review."},
]
def source(path):return json.loads(path.read_text(encoding="utf-8"))
def specs(value=ROWS):
 d={}
 for line in value.splitlines():
  cols=line.split("|")
  if len(cols)!=5:raise ValueError("Bad source-gloss specification")
  v,tid,lemma,morph,gloss=cols
  d.setdefault("Gen.1."+v,[]).append({"id":tid,"lemma":lemma,"morph":morph,"gloss":gloss})
 if {k:len(v) for k,v in d.items()}!={"Gen.1.6":11,"Gen.1.7":17,"Gen.1.8":10,"Gen.1.9":13,"Gen.1.10":12}:
  raise ValueError("Expected all 63 source word tokens")
 return d
def verb_form(morph):
 segments=morph.split("/")
 for item in segments:
  if item.startswith("H") or item.startswith("A"):item=item[1:]
  if item.startswith("V") and len(item)>=3:return item[2]
 return None
def build(dossier,cards,seed,plans=None,texts=None,notes=None):
 plans=plans if plans is not None else specs()
 texts=texts if texts is not None else VERSES
 notes=notes if notes is not None else NOTES
 if dossier["scope"]["source_word_tokens"]!=434:raise ValueError("Wrong original source chapter scope")
 lex={x["source_exact_lemma_id"]:x for x in cards["cards"]}
 if len(lex)!=97:raise ValueError("Missing original Genesis lexical cards")
 owners={x["id"]:x for x in seed["entries"] if x["status"]=="OWNER_LOCKED"}
 if owners["asah"]["english_base"]!="make" or owners["raqia"]["english_base"]!="firmament" or owners["waw.conj"]["english_base"]!="and":
  raise ValueError("One or more owner English-family locks changed")
 if set(plans)!=set(VERSES):raise ValueError("Wrong verse coverage")
 outputs=[];totalway=0;linked_lemmas=set()
 for ref,expected in plans.items():
  original=sorted((x for x in dossier["tokens"] if x["verse"]==ref),key=lambda x:x["ordinal"])
  if len(original)!=len(expected):raise ValueError("Source token count changed in "+ref)
  aligned=[]
  for i,(src,e) in enumerate(zip(original,expected),1):
   if (src["ordinal"],src["source_token_id"],src["source_lemma_raw"],src["source_morphology_raw"])!=(i,e["id"],e["lemma"],e["morph"]):
    raise ValueError("Original source ID/lemma/morph/order mismatch in "+ref+" token "+str(i))
   wf=verb_form(src["source_morphology_raw"])
   way=(wf=="w")
   if way!=src["source_tagged_wayyiqtol"]:
    raise ValueError("Imported wayyiqtol tag contradicts source morphology")
   if e["id"]=="01bmv" and ("made" not in e["gloss"].lower() or "shape" in e["gloss"].lower()):
    raise ValueError("Owner-lock asah must render made, not shaped")
   if way and not re.search(r"\b(?:said|made|separated|was|called|saw)\b",e["gloss"],re.I):
    raise ValueError("Wayyiqtol lacks a simple-past English surface")
   if way and re.search(r"\b(?:hath|has|had|will|shall)\b",e["gloss"],re.I):
    raise ValueError("Wayyiqtol incorrectly perfect/future")
   if e["id"] in ("01BsK","01NPq") and wf!="j":
    raise ValueError("Jussive incorrectly reclassified")
   if e["id"] in ("01qty","01QwM") and wf!="i":
    raise ValueError("Volitive-context imperfect incorrectly reclassified")
   if e["id"]=="015gQ" and (wf!="r" or "separating" not in e["gloss"]):
    raise ValueError("Participle misparsed or cast as finite past")
   if "7549" in src["exact_lexemes"] and "firmament" not in e["gloss"].lower():
    raise ValueError("Owner-lock raqia must render firmament")
   if e["id"]=="01Xm1" and (e["gloss"]!="" or src["source_lemma_raw"]!="853"):
    raise ValueError("Definite direct-object marker must have zero standalone English gloss")
   if re.search(r"\b(?:it|its|itself)\b",e["gloss"],re.I):
    raise ValueError("Neutral standalone pronoun in proposed English token gloss")
   for lemma in src["exact_lexemes"]:
    if lemma not in lex:raise ValueError("No original dictionary card: "+lemma)
    linked_lemmas.add(lemma)
   totalway+=way
   aligned.append({
    "ordinal":i,"source_token_id":src["source_token_id"],
    "pointed_hebrew":src["pointed_source_word"],
    "raw_lemma":src["source_lemma_raw"],"exact_lemma_ids":src["exact_lexemes"],
    "raw_morphology":src["source_morphology_raw"],
    "source_verb_form_code":wf,"source_tagged_wayyiqtol":way,
    "english_fragment_proposed":e["gloss"],
    "dictionary_ids":[{"lemma":lem,
       "bdb":[x["id"] for x in lex[lem]["dictionary_refs"]["bdb"]],
       "strong":[x["id"] for x in lex[lem]["dictionary_refs"]["strong"]]} for lem in src["exact_lexemes"]],
    "English_choice_status":"RESEARCH_ONLY_NOT_APPROVED",
    "independent_morphology_review":"NOT_DONE"})
  final=texts.get(ref)
  if not final:raise ValueError("Proposed English verse missing")
  if re.search(r"\b(?:it|its|itself)\b",final,re.I):raise ValueError("Neutral English it in main candidate")
  if "God — He" not in final:raise ValueError("Named subject + verb-person agreement absent")
  if ref=="Gen.1.7" and "God — He made the firmament" not in final:raise ValueError("Owner-locked make/firmament phrase changed")
  if "firmament" in " ".join(e["gloss"].lower() for e in expected) and "firmament" not in final.lower():
   raise ValueError("Owner-locked firmament omitted")
  outputs.append({"reference":ref,"source_tokens":aligned,"source_token_count":len(aligned),
        "wayyiqtol_count":sum(x["source_tagged_wayyiqtol"] for x in aligned),
        "english_main_research_candidate":final,"status":"DRAFT_NOT_PHILOLOGICALLY_APPROVED"})
 if totalway!=11:raise ValueError("Source tagged wayyiqtol total changed")
 for n in notes:
  if n["ref"] not in plans or n["lemma"] not in linked_lemmas or n["status"] not in {"OWNER_LOCK","RESEARCH","SOURCE_BASED"}:
   raise ValueError("Research note invalid or source-unanchored")
  if n["type"]=="HOMONYM_CAUTION" and n["status"]=="OWNER_LOCK":
   raise ValueError("Unreviewed homonym wrongly owner-certified")
 return {"project":"Olund's Linked Translation","checkpoint":"OLT-010",
   "status":"SOURCE_ALIGNED_RESEARCH_ONLY","source":"pinned OSHB Masoretic WLC and linked BDB/Strong",
   "verse_count":len(outputs),"token_count":sum(x["source_token_count"] for x in outputs),
   "wayyiqtol_count":totalway,"distinct_lemma_ids":len(linked_lemmas),
   "source_verified_ids_only":True,"english_approvals":"NO_NEW_APPROVAL",
   "independent_morphology_review":"NOT_DONE","chapter_publication":"BLOCKED",
   "verses":outputs,"notes":notes,
   "source_urls":["https://github.com/openscriptures/morphhb","https://github.com/openscriptures/HebrewLexicon",
      "https://www.studylight.org/lexicons/eng/gesenius/109.html",
      "https://openbible.com/text/genesis/1-6.htm"]}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--out",type=Path,default=DEST)
 args=parser.parse_args()
 result=build(source(D/"genesis_01_source_review_dossier.json"),
   source(D/"genesis_01_dictionary_study_cards.json"),source(ROOT/"lexicon/hebrew.json"))
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:result[k] for k in ("verse_count","token_count","wayyiqtol_count","distinct_lemma_ids","chapter_publication")},sort_keys=True))
if __name__=="__main__":main()
