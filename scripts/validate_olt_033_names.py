#!/usr/bin/env python3
"""Validate Bible-wide names/meanings policy; never certify research proposals."""
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def verify(p,r,lex,verse,legacy):
    if p.get("policy_id")!="OLT-033" or p.get("publication_status")!="BLOCKED":
        raise ValueError("Policy or release boundary")
    if set(p.get("scope",[]))!={"OLD_TESTAMENT_HEBREW","NEW_TESTAMENT_GREEK","SOURCE_LANGUAGE_NAMES_AND_SEMANTICALLY_SIGNIFICANT_TERMS"}:
        raise ValueError("Both Testaments required")
    if p.get("mandatory_for_every_occurrence_when_supported") is not True or p.get("render_policy",{}).get("may_omit_underword_when_meaning_unresolved") is not True:
        raise ValueError("Meaningful occurrences required; opaque names never invented")
    if p["render_policy"]["direction"]!="DIRECTLY_BELOW_MAIN_ENGLISH_NAME" or p["render_policy"]["underword_color"]!="#2463A6":
        raise ValueError("Wrong linked-word layout")
    if lex.get("name_underword_registry")!="lexicon/name_underwords.json" or lex.get("name_underword_policy")!="data/policy/olt_name_underword_policy.json":
        raise ValueError("Missing canonical lexicon link")
    if r.get("publication_status")!="BLOCKED" or r.get("independent_philological_approval") is not False or r.get("nt_source_edition_pinned") is not False:
        raise ValueError("False NT or name approval")
    if r.get("globally_rendered_occurrences")!=0 or r.get("source_language_identity_checked_for_all_verses") is not False:
        raise ValueError("False biblical coverage")
    entries=r.get("entries",[])
    if len(entries)!=10 or r.get("record_count")!=10:
        raise ValueError("Exactly 10 initial candidate cases")
    wanted={"moses-draw":("Moses","Draw"),"elohim-mighty-governance":("God","Mighty Governance"),
      "el-mighty":("El","Mighty"),"el-shaddai-my-mighty-strength":("El Shaddai","My Mighty Strength"),
      "jerusalem-city-of-peace":("Jerusalem","City of Peace"),"david-the-beloved":("David","The Beloved"),
      "noah-rest":("Noah","Rest"),"shiloh-genesis-title":("Shiloh","To Whom It Belongs"),
      "shiloh-place-rest":("Shiloh","Place of Rest"),"siloam-sent":("Siloam","Sent")}
    seen=set()
    for e in entries:
        key=e["id"]
        if key not in wanted or key in seen or (e["primary"],e["owner_requested_underword"])!=wanted[key]:
            raise ValueError("Wrong or duplicate owner-specified name/underword")
        seen.add(key)
        if e.get("meaning_certified") is not False or e.get("lexical_automatic_render") is not False:
            raise ValueError("Name research incorrectly certified")
        if not (e.get("original_script") and e.get("original_language") and e.get("note") and e.get("primary_context")):
            raise ValueError("Missing original-language identity or note")
        if not e.get("evidence"):
            raise ValueError("Missing source evidence")
        for citation in e["evidence"]:
            u=urlsplit(citation.get("url",""))
            if u.scheme!="https" or not u.netloc:
                raise ValueError("Invalid source reference")
    if seen!=set(wanted):
        raise ValueError("Missing name candidate")
    names={e["id"]:e for e in entries}
    noah=names["noah-rest"]
    if "נוח" not in noah["note"] or "נחם" not in noah["note"]:
        raise ValueError("Noah rest and comfort roots must remain distinct")
    god=names["elohim-mighty-governance"]
    if god.get("verified_olt_source_token_ids")!=["01TyA"] or "NOT an established literal Hebrew gloss" not in god["note"]:
        raise ValueError("Elohim cannot be certified as lexical Mighty Governance")
    token=next((x for x in verse["source_alignment"] if x["source_token_id"]=="01TyA"),{})
    if (token.get("exact_lemma_id"),token.get("proposed_english_surface"))!=("430","God"):
        raise ValueError("Elohim original source token mismatch")
    if "NO first-person" not in names["el-shaddai-my-mighty-strength"]["note"]:
        raise ValueError("El Shaddai lacks possessive My")
    if names["shiloh-genesis-title"]["lexical_reference_ids"]==names["shiloh-place-rest"]["lexical_reference_ids"]:
        raise ValueError("Shiloh title and place are different records")
    if names["siloam-sent"]["primary_context"]!="John.9.7":
        raise ValueError("Siloam explicit Gospel explanation missing")
    if legacy["scope"]!="ONE_EXCEPTION_GENESIS_1_1_ONLY" or len(legacy["underwords"])!=1 or legacy["underwords"][0]["secondary_english"]!="with":
        raise ValueError("Genesis 1:1 unique In/with exception must be preserved")

def main():
    verify(load("data/policy/olt_name_underword_policy.json"),
       load("lexicon/name_underwords.json"),load("lexicon/hebrew.json"),
       load("data/research/genesis_01_verse_01_alignment_proposal.json"),
       load("data/policy/olt_underword_overrides.json"))
    print("PASS: OLT-033 name underwords — God/Mighty Governance, Noah/Rest, research only")
if __name__=="__main__":
    main()
