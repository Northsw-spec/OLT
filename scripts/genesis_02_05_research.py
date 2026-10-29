#!/usr/bin/env python3
"""OLT-009: source-token-aligned Genesis 1:2–5 research; NOT publication."""
import json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/quality"
OUT=ROOT/"data/research/genesis_01_verses_02_to_05_research.json"
# verse, ordinal, immutable source-token ID, exact lemma annotation, exact OSHB morphology, source-linked proposed English span
SPEC="""2|1|01LN3|c/d/776|HC/Td/Ncbsa|And the Earth
2|2|01Qzf|1961|HVqp3fs|she was
2|3|01aPd|8414|HNcmsa|waste
2|4|01eYX|c/922|HC/Ncmsa|and emptiness
2|5|01C5U|c/2822|HC/Ncmsa|and darkness
2|6|01qNN|5921 a|HR|upon
2|7|01EVS|6440|HNcbpc|the face of
2|8|01PB6|8415|HNcbsa|the Deep
2|9|0137c|c/7307|HC/Ncbsc|and the Spirit
2|10|01x9c|430|HNcmpa|of God
2|11|01yNB|7363 b|HVprfsa|hovering
2|12|0129t|5921 a|HR|upon
2|13|01KZG|6440|HNcbpc|the face of
2|14|01TZE|d/4325|HTd/Ncmpa|the Waters
3|1|01thY|c/559|HC/Vqw3ms|And He said
3|2|01JM7|430|HNcmpa|God
3|3|01fpo|1961|HVqj3ms|Let be
3|4|01W26|216|HNcbsa|light
3|5|01yw4|c/1961|HC/Vqw3ms|And was
3|6|01jbg|216|HNcbsa|light
4|1|01USR|c/7200|HC/Vqw3ms|And He saw
4|2|01v6U|430|HNcmpa|God
4|3|015SS|853|HTo|
4|4|01GzE|d/216|HTd/Ncbsa|the light
4|5|01qCU|3588 a|HC|that
4|6|01g2y|2896 a|HAamsa|good
4|7|01jQb|c/914|HC/Vhw3ms|And He separated
4|8|01794|430|HNcmpa|God
4|9|01CsU|996|HR|between
4|10|01XR4|d/216|HTd/Ncbsa|the light
4|11|01KvS|c/996|HC/R|and between
4|12|01dBc|d/2822|HTd/Ncmsa|the darkness
5|1|01nAB|c/7121|HC/Vqw3ms|And He called
5|2|01kfX|430|HNcmpa|God
5|3|01Wkf|l/216|HRd/Ncbsa|to the light
5|4|01wrL|3117|HNcmsa|Day
5|5|013TL|c/l/2822|HC/Rd/Ncmsa|and to the darkness
5|6|01LeN|7121|HVqp3ms|He called
5|7|01sMn|3915|HNcmsa|Night
5|8|01Y3z|c/1961|HC/Vqw3ms|and was
5|9|01NQN|6153|HNcmsa|evening
5|10|01uLf|c/1961|HC/Vqw3ms|and was
5|11|01kA7|1242|HNcmsa|morning
5|12|013TS|3117|HNcmsa|day
5|13|01NFp|259|HAcmsa|one"""
MAIN={
"Gen.1.2":"And the Earth — she was waste and emptiness; and darkness upon the face of the Deep; and the Spirit of God hovering upon the face of the Waters.",
"Gen.1.3":"And God — He said: “Let light be.” And light was.",
"Gen.1.4":"And God — He saw the light, that [he was] — good. And God — He separated between the light and between the darkness.",
"Gen.1.5":"And God — He called to the light Day, and to the darkness He called Night; and was evening, and was morning: day one.",
}
LOCK="And God — He saw the light, that [he was] — good."
NOTES=[
{"reference":"Gen.1.2","type":"LEXICAL_ALTERNATIVES","source_lemma":"7307","text":"Ruach may signify spirit, wind or breath. 'Spirit of God' is an OLT research proposal, not the only dictionary possibility.","status":"UNAPPROVED"},
{"reference":"Gen.1.2","type":"DIFFERENT_LEMMAS","source_lemma":"8414","text":"Tohu (waste/formlessness) and bohu (emptiness) are distinct source lemmas and keep two separate English words.","status":"UNAPPROVED"},
{"reference":"Gen.1.2","type":"MORPHOLOGY","source_lemma":"7363 b","text":"Merachephet is a Piel active feminine-singular participle agreeing with ruach, not a wayyiqtol.","status":"SOURCE_TAG_NOT_INDEPENDENTLY_REVIEWED"},
{"reference":"Gen.1.3","type":"MORPHOLOGY","source_lemma":"1961","text":"Yehi is jussive; the next vayehi is wayyiqtol and renders with English simple past was.","status":"SOURCE_TAG_NOT_INDEPENDENTLY_REVIEWED"},
{"reference":"Gen.1.4","type":"EDITORIAL_SUPPLEMENT","source_lemma":"216","text":"[he was] is the owner's bracketed English completion for light, not separately present Hebrew text. The source marks light as common gender; other lexical evidence treats light as masculine. The Bible-wide gender explanation is given only once at the opening.","status":"OWNER_WORDING_AND_RESEARCH_NOTE"},
{"reference":"Gen.1.4","type":"DIRECT_OBJECT","source_lemma":"853","text":"Et marks a direct object and has no independent English lexical surface. Its token is retained.","status":"SOURCE_TAG_NOT_INDEPENDENTLY_REVIEWED"},
{"reference":"Gen.1.4","type":"TYPOLOGY_RESEARCH_CANDIDATE","source_lemma":"216","text":"Compare Genesis light imagery with John 1:4–9 only as Christian intertextual interpretation, not as Hebrew-Greek homonymy.","status":"UNAPPROVED"},
{"reference":"Gen.1.5","type":"MORPHOLOGY","source_lemma":"7121","text":"First called (vayyiqra) is wayyiqtol, second called (qara) is qatal. Both use English past but the source forms remain distinct.","status":"SOURCE_TAG_NOT_INDEPENDENTLY_REVIEWED"},
{"reference":"Gen.1.5","type":"NUMERAL","source_lemma":"259","text":"Yom echad is literally day one; the ordinal first is an interpretive English alternative.","status":"UNAPPROVED"}]
SOURCES=["https://github.com/openscriptures/morphhb",
"https://github.com/openscriptures/HebrewLexicon",
"https://fellowshipbook.org/en/genesis/1/2",
"https://lashon.online/learn/biblical-hebrew/guided-reading-genesis-1",
"https://openbible.com/text/genesis/1-5.htm"]
def parse(rows=SPEC):
 result={}
 for line in rows.splitlines():
  p=line.split("|")
  if len(p)!=6:raise ValueError("Invalid planned source row")
  v,ordinal,tid,lemma,morph,gloss=p
  result.setdefault("Gen.1."+v,[]).append({"ordinal":int(ordinal),"id":tid,
     "lemma":lemma,"morph":morph,"gloss":gloss})
 if {v:len(rows) for v,rows in result.items()}!={"Gen.1.2":14,"Gen.1.3":6,"Gen.1.4":12,"Gen.1.5":13}:raise ValueError("Missing original verse tokens")
 return result
def make(source,cards,plan=None,main=None,notes=None):
 plan=plan if plan is not None else parse()
 main=main if main is not None else MAIN
 notes=notes if notes is not None else NOTES
 if source.get("scope",{}).get("source_word_tokens")!=434:raise ValueError("Original Genesis dossier scope changed")
 lex={x["source_exact_lemma_id"]:x for x in cards["cards"]}
 if len(lex)!=97:raise ValueError("Source lexicon card coverage changed")
 records=[];total_way=0;lemma_ids=set()
 for verse,specs in plan.items():
  actual=sorted((x for x in source["tokens"] if x["verse"]==verse),key=lambda x:x["ordinal"])
  if len(actual)!=len(specs):raise ValueError("Missing original source token: "+verse)
  items=[]
  for a,s in zip(actual,specs):
   if (a["ordinal"],a["source_token_id"],a["source_lemma_raw"],a["source_morphology_raw"])!=(s["ordinal"],s["id"],s["lemma"],s["morph"]):
    raise ValueError("Source token/lemma/morphology mismatch: "+verse)
   is_way=a["source_tagged_wayyiqtol"]
   # Categorize forms before checking their English past tense, so a
   # mislabelled jussive/participle cannot masquerade as narrative wayyiqtol.
   if s["id"]=="01fpo" and (s["morph"]!="HVqj3ms" or is_way):
    raise ValueError("Jussive was wrongly identified as wayyiqtol")
   if s["id"]=="01yNB" and (s["morph"]!="HVprfsa" or is_way):
    raise ValueError("Piel participle wrongly identified")
   if s["id"]=="01LeN" and (s["morph"]!="HVqp3ms" or is_way):
    raise ValueError("Gen 1:5 second called is QATAL, not wayyiqtol")
   if is_way and not re.search(r"\b(?:said|was|saw|separated|called)\b",s["gloss"],re.I):
    raise ValueError("Wayyiqtol not English simple past")
   if is_way and re.search(r"\b(?:has|hath|had|will|shall)\b",s["gloss"],re.I):
    raise ValueError("Wayyiqtol used English perfect/future")
   if s["id"]=="015SS" and (s["gloss"]!="" or s["lemma"]!="853"):
    raise ValueError("Object marker not explicitly zero-glossed")
   for k in a["exact_lexemes"]:
    if k not in lex:raise ValueError("No verified lexical source-ID for "+k)
    lemma_ids.add(k)
   total_way+=int(is_way)
   items.append({"source_token_id":a["source_token_id"],"source_ordinal":a["ordinal"],
     "pointed_hebrew_word":a["pointed_source_word"],"source_raw_lemma":a["source_lemma_raw"],
     "source_raw_morphology":a["source_morphology_raw"],"source_tagged_wayyiqtol":is_way,
     "proposed_english_source_gloss":s["gloss"],
     "source_lexicon_ids":a["exact_lexemes"],
     "dictionary_refs":[{"source_exact_lemma_id":k,
       "bdb":[x["id"] for x in lex[k]["dictionary_refs"]["bdb"]],
       "strong":[x["id"] for x in lex[k]["dictionary_refs"]["strong"]]} for k in a["exact_lexemes"]],
     "editorial_english_status":"UNAPPROVED_RESEARCH_PROPOSAL"})
  txt=main[verse]
  if re.search(r"\b(?:it|its|itself)\b",txt,re.I) or re.search(r"\b(?:it|its|itself)\b"," ".join(s["gloss"] for s in specs),re.I):
   raise ValueError("Neutral it in English main or token gloss")
  if verse!="Gen.1.2" and "God — He" not in txt:raise ValueError("Mandatory subject-person visibility missing")
  records.append({"reference":verse,"english_main_proposal":txt,"source_word_count":len(items),
    "source_wayyiqtol_count":sum(x["source_tagged_wayyiqtol"] for x in items),
    "source_aligned_tokens":items,"review_status":"NOT_INDEPENDENTLY_APPROVED"})
 if total_way!=7:raise ValueError("Incorrect actual number of wayyiqtol forms")
 if not main["Gen.1.4"].startswith(LOCK):raise ValueError("Changed owner-approved Gen 1:4 clause")
 for note in notes:
  if note["type"]=="TYPOLOGY_RESEARCH_CANDIDATE" and note["status"]!="UNAPPROVED":
   raise ValueError("Typology falsely promoted to lexical identity")
  if note["source_lemma"] not in lemma_ids:raise ValueError("Unanchored biblical research note")
 return {"project":"Olund's Linked Translation","checkpoint":"OLT-009",
   "verses":records,"verses_count":4,"source_token_count":sum(x["source_word_count"] for x in records),
   "source_tagged_wayyiqtol_count":total_way,"distinct_lemma_ids":len(lemma_ids),
   "research_notes":notes,"sources":SOURCES,
   "english_lexical_approvals":"NONE_NEW","independent_philological_review":"NOT_DONE",
   "release_status":"BLOCKED","scope":"SOURCE_ALIGNED_RESEARCH_ONLY"}
def main():
 source=json.loads((DATA/"genesis_01_source_review_dossier.json").read_text())
 cards=json.loads((DATA/"genesis_01_dictionary_study_cards.json").read_text())
 j=make(source,cards)
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"tokens":j["source_token_count"],"wayyiqtol":j["source_tagged_wayyiqtol_count"],"distinct_lemmas":j["distinct_lemma_ids"],"release":j["release_status"]}))
if __name__=="__main__":main()
