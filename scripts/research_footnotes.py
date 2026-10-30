#!/usr/bin/env python3
"""Validate verse-attached research notes and render GitHub Markdown footnotes.

Source anchors are *English editorial spans*, never invented Hebrew words.
This is a preview renderer, not a native PDF/ODT page-bottom-footnote engine.
"""
from __future__ import annotations
import re

NOTE_ID = re.compile(r"^[a-z][a-z0-9-]{2,79}$")

def attach_footnotes(verses):
    """Return (English verses with inline markers, ordered footnote definitions, manifest).

    Fail closed when a source note has no unique anchor, an incorrect verse,
    duplicate identifier, insufficient evidence provenance or a forged signoff.
    The input verse text is never changed; markers belong only to the preview.
    """
    seen=set()
    marked=[]
    definitions=[]
    manifest=[]
    for verse in verses:
        ref=verse["reference"]
        text=verse["proposed_english_research_text"]
        if not isinstance(text,str) or not text.strip():
            raise ValueError("Footnote renderer requires a nonempty English verse")
        notes=verse.get("verse_footnote_proposals",[])
        if not isinstance(notes,list):
            raise ValueError("Footnote collection must be a list")
        for note in notes:
            if not isinstance(note,dict):
                raise ValueError("Footnote record must be an object")
            identifier=note.get("id","")
            if not isinstance(identifier,str) or not NOTE_ID.fullmatch(identifier):
                raise ValueError("Unsafe or invalid verse footnote identifier")
            if identifier in seen:
                raise ValueError("Duplicate footnote identifier "+identifier)
            seen.add(identifier)
            if note.get("reference")!=ref:
                raise ValueError("Footnote verse/source-reference mismatch for "+identifier)
            anchor=note.get("anchor")
            if not isinstance(anchor,str) or not anchor.strip() or text.count(anchor)!=1:
                raise ValueError("Footnote anchor missing or ambiguous in "+ref)
            if note.get("category")=="INTERTEXTUAL_THEOLOGICAL_SUPPLEMENT":
                if note.get("is_independent_hebrew_lexeme") is not False:
                    raise ValueError("Theological supplement falsely claims a Hebrew lexeme")
            if note.get("editorial_status") not in {
                "RESEARCH_DRAFT",
                "OWNER_WORDING_RESEARCH_FOOTNOTE",
                "SOURCE_GRAMMAR_RESEARCH_DRAFT",
            }:
                raise ValueError("Footnote cannot claim independent editorial approval")
            evidence=note.get("evidence_references")
            if not isinstance(evidence,list) or not evidence or any(
                not isinstance(x,str) or not x.strip() for x in evidence
            ):
                raise ValueError("Footnote lacks specific evidence references")
            body=note.get("english")
            if not isinstance(body,str) or not body.strip() or "\n" in body or "\r" in body:
                raise ValueError("Invalid or blank footnote body")
            # Insert the reference IMMEDIATELY after the phrase explained.
            # Never place it at the end of the entire verse by default.
            marker="[^"+identifier+"]"
            text=text.replace(anchor,anchor+marker,1)
            definitions.append(marker+": "+body)
            manifest.append({
                "reference":ref,
                "footnote_id":identifier,
                "anchor":anchor,
                "category":note["category"],
                "source_references":list(evidence),
                "status":"RESEARCH_NOTE_NOT_PUBLISHED",
                "marker_placement":"IMMEDIATELY_AFTER_ANCHOR",
            })
        marked.append(text)
    if len(definitions)!=len(manifest):
        raise ValueError("Footnote definition/reference bijection broken")
    return marked,definitions,manifest
