#!/usr/bin/env python3
"""OLT-022: one source-anchored owner INTERPRETIVE under-word, never auto homonymy.

Preserves the Hebrew source word, primary English verse, and attached power note.
The owner's 'with' below 'In' is NOT a certified instrumental parse of Gen 1:1.
"""
from __future__ import annotations
import re

EXPECTED_TEXT="In the Beginning [of His Power] God — He shaped the Heavens and the Earth."
NOTE_ID=re.compile(r"^[a-z][a-z0-9-]{2,79}$")
COLORS=("#5B277D","#2463A6")
EXPECTED_SOURCE=("01xeN",1,"b/7225","HR/Ncfsa","בְּ")
EXPECTED_FUNCTIONS=("TEMPORAL_CONTEXTUAL_RESEARCH_READING",
                    "OWNER_BINITARIAN_INTERPRETIVE_ALTERNATIVE")

def attach_underwords(verses, configuration):
    """Check source identity and return a manifest without promoting a gloss to fact."""
    if configuration.get("policy_id")!="OLT-022" or configuration.get("authority")!="EXPLICIT_OWNER_DISPLAY_DECISION":
        raise ValueError("Unapproved underword policy")
    if configuration.get("scope")!="ONE_EXCEPTION_GENESIS_1_1_ONLY":
        raise ValueError("Underword scope must be only Genesis 1:1")
    if configuration.get("automatically_generalize_to_other_bet") is not False:
        raise ValueError("A global in/with substitution is prohibited")
    if configuration.get("publication_status")!="BLOCKED":
        raise ValueError("Underword policy falsely marked published")
    entries=configuration.get("underwords")
    if not isinstance(entries,list) or len(entries)!=1:
        raise ValueError("Exactly one owner-requested Genesis 1:1 underword expected")
    entry=entries[0]
    if entry.get("reference")!="Gen.1.1":
        raise ValueError("Owner exception cannot migrate to another verse")
    if (entry.get("source_token_id"),entry.get("source_ordinal"),entry.get("source_lemma_raw"),
        entry.get("source_morphology_raw"),entry.get("source_preposition"))!=EXPECTED_SOURCE:
        raise ValueError("Underword lacks exact original Hebrew source anchor")
    if entry.get("source_preposition_code")!="b":
        raise ValueError("Underword must attach only to the bet prefix")
    if (entry.get("primary_english"),entry.get("secondary_english"))!=("In","with"):
        raise ValueError("Owner-locked In over with underword changed")
    if entry.get("placement")!="DIRECTLY_BELOW_ENGLISH_WORD":
        raise ValueError("Underword must be vertically below In")
    if (entry.get("primary_word_color"),entry.get("secondary_word_color"))!=COLORS:
        raise ValueError("Owner purple/blue underword style changed")
    if (entry.get("primary_semantic_function"),entry.get("secondary_semantic_function"))!=EXPECTED_FUNCTIONS:
        raise ValueError("Primary temporal and theological secondary roles conflated")
    if entry.get("interpretation_label")!="BINITARIAN_CANONICAL_INTERPRETATION":
        raise ValueError("Underword falsely classified as independently lexical")
    if entry.get("owner_selected_display") is not True:
        raise ValueError("Owner did not select exception")
    for key in ("this_verse_instrumental_bet_independently_established",
                "underword_is_verified_homonym","source_lexeme_means_jesus"):
        if entry.get(key) is not False:
            raise ValueError("Underword asserts unsupported original-language fact: "+key)
    if entry.get("english_main_verse_remains")!=EXPECTED_TEXT:
        raise ValueError("Owner Genesis 1:1 main line changed")
    v=[x for x in verses if x.get("reference")=="Gen.1.1"]
    if len(v)!=1:
        raise ValueError("One unique Genesis 1:1 source verse required")
    verse=v[0]
    if verse.get("proposed_english_research_text")!=EXPECTED_TEXT:
        raise ValueError("Cannot change main English verse to show an underword")
    if not verse["original_token_alignment"]:
        raise ValueError("Missing original source token")
    first=verse["original_token_alignment"][0]
    if (first.get("source_token_id"),first.get("source_ordinal"),
        first.get("original_lemma"),first.get("original_morphology"))!=EXPECTED_SOURCE[:4]:
        raise ValueError("Original Hebrew token anchor differs")
    if not first["original_hebrew"].startswith("בְּ/"):
        raise ValueError("Original pointed Hebrew bet prefix missing")
    if first["english_fragment_research_only"]!="In the Beginning":
        raise ValueError("Existing English lexical first-word alignment changed")
    note=entry.get("footnote")
    if not isinstance(note,dict) or note.get("id")!=entry["id"] or note.get("anchor")!="with":
        raise ValueError("Underword interpretation footnote missing")
    if not NOTE_ID.fullmatch(note["id"]):
        raise ValueError("Invalid underword footnote id")
    if note.get("status")!="OWNER_INTERPRETIVE_LINK_NOT_PHILOLOGICALLY_APPROVED":
        raise ValueError("Underword research must not self-certify philology")
    body=note.get("english","")
    if not isinstance(body,str) or not body.strip() or "\n" in body:
        raise ValueError("Underword footnote is empty or multiline")
    required=("temporal","With Wisdom","eternal uncreated Son",
              "NOT an independently established instrumental",
              "NOT a proven lexical identification","NOT a claim that the Son was created")
    if not all(x.lower() in body.lower() for x in required):
        raise ValueError("Underword footnote has lost essential evidence boundary")
    sources=note.get("evidence",[])
    if len(sources)<2 or not all(isinstance(x,dict) and x.get("url","").startswith("https://") for x in sources):
        raise ValueError("Underword requires traceable external scholarly evidence")
    if len(note.get("canonical_intertexts",[]))<2:
        raise ValueError("Intertextual reading has no biblical references")
    if any(x.get("reference")!="Gen.1.1" and x.get("underword_proposals") for x in verses):
        raise ValueError("Owner exception leaked beyond Genesis 1:1")
    manifest={
        "id":entry["id"],"reference":"Gen.1.1","source_token_id":"01xeN",
        "source_ordinal":1,"source_preposition":"בְּ",
        "source_lemma_raw":"b/7225","primary":"In","secondary":"with",
        "placement":"DIRECTLY_BELOW_ENGLISH_WORD",
        "primary_word_color":"#5B277D","secondary_word_color":"#2463A6",
        "semantic_type":"BINITARIAN_CANONICAL_INTERPRETATION",
        "primary_grammatical_function":"TEMPORAL_CONTEXTUAL_RESEARCH_READING",
        "instrumental_claim_confirmed":False,
        "owner_display_approved":True,
        "independent_philological_signoff":False,
        "source_lexical_jesus_claim":False,
        "footnote":note
    }
    verse["underword_proposals"]=[manifest]
    return [manifest]

def render_linked_verse(verse, english_with_standard_footnotes):
    """GitHub Markdown two-column table: with appears on next line UNDER In."""
    under=verse.get("underword_proposals",[])
    if not under:
        return ["**OLT English research proposal:** "+english_with_standard_footnotes]
    if len(under)!=1 or verse.get("reference")!="Gen.1.1":
        raise ValueError("Unexpected underword source verse")
    u=under[0]
    if u["primary"]!="In" or u["secondary"]!="with":
        raise ValueError("Changed owner underword")
    if not english_with_standard_footnotes.startswith("In "):
        raise ValueError("Main English does not begin with separate In")
    continuation=english_with_standard_footnotes[len("In "):]
    if "[of His Power][^gen-1-1-power]" not in continuation:
        raise ValueError("Theological power footnote placement changed")
    return [
        "**OLT English research proposal (vertical linked-word layout):**",
        "",
        "|  |  |",
        "| :--- | :--- |",
        "| **In**<br><sub>with</sub>[^"+u["footnote"]["id"]+"] | "+continuation+" |",
    ]

def underword_note_definitions(manifest):
    return ["[^"+m["footnote"]["id"]+"]: "+m["footnote"]["english"] for m in manifest]
