import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REL={"HOMONYM","HOMOGRAPH","POLYSEMY","SHARED_ROOT","NAME_ASSOCIATION","PARONOMASIA","DIRECT_INTERTEXT","TYPOLOGY","DISPUTED"}
LOCK={"bara":"shape","asah":"make","raqia":"firmament","waw.conj":"and"}
def data(file): return json.loads((ROOT/file).read_text(encoding="utf-8"))
def validate(lex,links,verse,css):
    e=[]; lemmas=lex.get("entries",[]); ids=[x["id"] for x in lemmas]; M={x["id"]:x for x in lemmas}
    if len(set(ids))!=len(ids): e.append("DUPLICATE_LEMMA_ID")
    for k,v in LOCK.items():
        if M.get(k,{}).get("english_base")!=v or M.get(k,{}).get("status")!="OWNER_LOCKED": e.append("LOCK:"+k)
    if lex.get("source_morphology")!="NOT_IMPORTED": e.append("FALSE_SOURCE_STATUS")
    if links.get("layout")!="VERTICAL_UNDER_WORD": e.append("LAYOUT_MODE")
    for l in links.get("entries",[]):
        if l.get("relation") not in REL: e.append("REL:"+l.get("id","?"))
        if l.get("position")!="below": e.append("POSITION:"+l.get("id","?"))
        if "/" in l.get("word","") or "/" in l.get("below",""): e.append("INLINE_SLASH")
        if not l.get("note_required") or not l.get("refs") or not l.get("note"): e.append("MISSING_NOTE")
        if l.get("colors")!={"main":"#5B277D","linked":"#2463A6"}: e.append("COLOR")
        for k in l.get("lemma_ids",[]):
            if k not in M: e.append("UNRESOLVED_LEMMA:"+k)
    if "flex-direction:column" not in css.replace(" ",""): e.append("NONVERTICAL_CSS")
    if verse.get("translation")!="And God — He saw the light, that [he was] — good.": e.append("WRONG_GEN_1_4")
    if re.search(r"\b(?:it|its|itself)\b",verse.get("translation",""),re.I): e.append("NEUTER")
    for f in verse.get("morphology",[]):
        if f.get("claimed_form")=="WAYYIQTOL":
            if f.get("english_tense")!="SIMPLE_PAST" or f.get("english") not in {"saw","said","came","made","shaped","destroyed","called"}: e.append("WRONG_WAYYIQTOL_TENSE")
    return e
def blockers(lex,verse):
    b=[]
    if lex.get("source_morphology")!="IMPORTED_REVIEWED": b.append("SOURCE_MORPHOLOGY_NOT_REVIEWED")
    if lex.get("coverage")!="COMPLETE_GENESIS_1": b.append("GENESIS_LEXICON_INCOMPLETE")
    if verse.get("status")!="ALL_31_VERSES_INDEPENDENTLY_REVIEWED": b.append("CHAPTER_NOT_REVIEWED")
    for p in ["release/Genesis_1.odt","release/Genesis_1.pdf","release/PRINT_SIGNOFF.json"]:
        if not (ROOT/p).exists(): b.append("MISSING:"+p)
    return b
def main():
    lex=data("lexicon/hebrew.json");lnk=data("links/registry.json");v=data("samples/Gen_1_4.json");css=(ROOT/"style/links.css").read_text()
    errors=validate(lex,lnk,v,css)
    if errors: print("FAIL",errors);return 2
    if "--release" in sys.argv:
        for b in blockers(lex,v): print("RELEASE BLOCKED:",b)
        return 3 if blockers(lex,v) else 0
    print("FOUNDATION PASS: seed only; no verified Hebrew morphology or released chapter")
    return 0
if __name__=="__main__": sys.exit(main())
