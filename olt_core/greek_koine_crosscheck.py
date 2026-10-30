"""OLT-037E: source-bound Koine lexical witnesses and LSJ key diagnostic.

Inputs: exact SHA-verified original public-domain Abbott-Smith 1922 Greek NT
TEI XML, CC BY-SA 4.0 Perseus LSJ TEI XML and OLT-037C/037D frozen
original-source research checkpoints. The Abbott-Smith dictionary depends in
part on earlier lexicography: it is NOT an automatically independent vote for
a lexical sense, nor proof of translation correctness.

Only native source entry labels, original TEI orths and short SOURCE-ONLY
definition evidence are captured. No lexicographic case is approved.
Never interpret original per-entry Strong labels as source token IDs or use
a lossy ASCII diagnostic key to select a biblical lemma/meaning.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
from typing import Any
import xml.etree.ElementTree as ET

from .engine import SourceContractError
from .greek_independent_lsj import (
    _frozen_context_dossiers,
    REPORT_PATH as LSJ_PREVIOUS_REPORT_PATH,
    source_entry_key_index,
    _entry_key_candidates,
    RESEARCH_QUERIES,
    CONTEXT_SHA256,
)
from .sources import ROOT
from scripts.fetch_olt_037d_lsj import read_lsj_source_manifest, verify_original_lsj
from scripts.fetch_olt_037e_abbott import read_abbott_manifest, verify_abbott_source

CHECKPOINT="OLT-037E"
REPORT_PATH="data/quality/olt_037e_abbott_koine_and_lsj_key_diagnostics.json"
LSJ_PREVIOUS_SHA256="ea9f6e031897630cd5645ace24797e91e145f2018e5dba236b8951d5f1aa4973"
TARGETS=("3004","3754")
MAX_SOURCE_DEFINITIONS=12
MAX_DIAGNOSTIC_KEYS=36


def _frozen_lsj_source(root:Path)->dict[str,Any]:
    raw=(root/LSJ_PREVIOUS_REPORT_PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=LSJ_PREVIOUS_SHA256:
        raise SourceContractError("OLT-037D original independent LSJ source evidence changed")
    value=json.loads(raw.decode("utf-8"))
    if (value.get("checkpoint")!="OLT-037D"
        or value.get("scholarly_decisions_approved")!=0
        or value.get("english_master_entries_approved")!=0
        or value.get("publication_status")!="BLOCKED"
        or value.get("source_shards_verified_with_original_git_blob_sha1")!=2):
        raise SourceContractError("Frozen LSJ research was unexpectedly approved")
    return value


def _native_tag(tag:str)->str:
    return tag.rsplit("}",1)[-1]


def _source_text(element:ET.Element)->str:
    return "".join(element.itertext()).strip()


def _validate_source_metadata(source:bytes)->ET.Element:
    """XML entity resolution is never used; input was verified by exact Git blob."""
    txt=source.decode("utf-8",errors="strict")
    if "<!DOCTYPE" in txt or "<!ENTITY" in txt:
        raise SourceContractError("Do not parse unreviewed external XML DTD or entities")
    try:
        root=ET.fromstring(source)
    except ET.ParseError as exc:
        raise SourceContractError("Original Abbott-Smith TEI XML parse failed") from exc
    if _native_tag(root.tag)!="TEI":
        raise SourceContractError("Abbott-Smith original source did not have TEI root")
    return root


def index_abbott_source_entries(source:bytes)->dict[str,Any]:
    """Preserve all native lexical entry labels and source-only definition evidence."""
    root=_validate_source_metadata(source)
    found:dict[str,list[dict[str,Any]]]={t:[] for t in TARGETS}
    total=0
    with_native_n=0
    for el in root.iter():
        if _native_tag(el.tag)!="entry":
            continue
        total+=1
        n=el.attrib.get("n")
        if not n:
            continue
        with_native_n+=1
        # Metadata Strong is an *Abbott dictionary reference*, not the
        # publisher's own NT word token ID or independent Greek lemma review.
        refs=re.findall(r"(?<![A-Za-z0-9])G(\d{1,5})(?![A-Za-z0-9])",n)
        if not refs or not set(refs).intersection(TARGETS):
            continue
        orth=[]
        definitions=[]
        for child in el.iter():
            tag=_native_tag(child.tag)
            if tag=="orth":
                form=_source_text(child)
                if form and form not in orth:
                    orth.append(form)
            elif tag in {"def","gloss"}:
                # The 1922-derived TEI edition can encode lexicographer
                # definition evidence as either <def> or <gloss>. Retain
                # the native source label; never treat it as an OLT choice.
                gloss=_source_text(child)
                if gloss and not any(x["original_source_text"]==gloss and
                                     x["original_source_tag"]==tag for x in definitions):
                    definitions.append({"original_source_tag":tag,
                                        "original_source_text":gloss})
        for t in TARGETS:
            if t not in refs:
                continue
            if (any(len(x)>1000 for x in orth[:4]) or
                any(len(x["original_source_text"])>1000
                    for x in definitions[:MAX_SOURCE_DEFINITIONS])):
                raise SourceContractError("Oversize native dictionary lexical evidence")
            found[t].append({
                "native_abbott_entry_attribute_n_SOURCE_ONLY":n,
                "all_native_abbott_strong_crossrefs_SOURCE_ONLY":refs,
                "native_entry_references_multiple_strong_numbers":len(set(refs))>1,
                "original_tei_entry_number_in_source":total,
                "first_source_orth_forms_NOT_APPROVED":orth[:4],
                "original_source_orth_form_count":len(orth),
                "first_source_def_or_gloss_records_NOT_OLT_TRANSLATION":
                    definitions[:MAX_SOURCE_DEFINITIONS],
                "original_source_def_or_gloss_count":len(definitions),
                "abbott_dictionary_gloss_used_as_translation":False,
                "biblical_contextual_sense_selected":None,
                "publication_status":"BLOCKED",
            })
    if total<4000 or with_native_n<4000:
        raise SourceContractError("Complete original Abbott-Smith dictionary entry inventory truncated")
    return {"original_xml_entry_count":total,
            "original_entries_with_native_n_attribute":with_native_n,
            "case_entries":found}


def _lossy_ascii_key_signature(raw:str)->str:
    """DIAGNOSTIC ONLY: discards Greek Beta Code accent, punctuation, digits."""
    if not raw or len(raw)>240:
        raise SourceContractError("Unexpected raw LSJ TEI lookup key")
    return "".join(ch.lower() for ch in raw if ch.isascii() and ch.isalpha())


def inspect_lsj_source_keys(rows:list[dict[str,str]],query:str)->dict[str,Any]:
    """Diagnostic orthographic neighborhoods, never automatic matching."""
    exact=_entry_key_candidates(rows,query)
    sig=_lossy_ascii_key_signature(query)
    diagnostic=[r for r in rows
                if _lossy_ascii_key_signature(r["source_tei_entry_key_UNREVIEWED"])==sig]
    wider=[r for r in rows
           if _lossy_ascii_key_signature(r["source_tei_entry_key_UNREVIEWED"]).startswith(sig)]
    return {
      "original_query_exact_source_key":query,
      "exact_original_source_key_matches_UNREVIEWED":exact,
      "lossy_ascii_signature_NOT_FOR_CROSSWALK":sig,
      "lossy_signature_count_DIAGNOSTIC_ONLY":len(diagnostic),
      "lossy_signature_source_key_records_DIAGNOSTIC_ONLY":
          diagnostic[:MAX_DIAGNOSTIC_KEYS],
      "lossy_ascii_prefix_count_DIAGNOSTIC_ONLY":len(wider),
      "lossy_ascii_prefix_source_key_samples_DIAGNOSTIC_ONLY":
          wider[:MAX_DIAGNOSTIC_KEYS],
      "lossy_evidence_automatically_resolves_original_exact_miss":False,
      "any_dictionary_lemma_or_sense_approved":False,
    }


def build_source_crosscheck(abbott_file:Path, lsj_source_dir:Path,
                            root:Path=ROOT)->dict[str,Any]:
    manifest=read_abbott_manifest(root)
    lsj_manifest=read_lsj_source_manifest(root)
    original=_frozen_context_dossiers(root)
    lsj_prev=_frozen_lsj_source(root)
    if (original["checkpoint"]!="OLT-037C"
        or original["number_of_verified_greek_lemma_decisions"]!=0
        or original["publication_status"]!="BLOCKED"
        or lsj_prev["source_lsj_commit"]!=lsj_manifest["upstream_pinned_commit"]
        or lsj_prev["frozen_greek_context_sha256"]!=CONTEXT_SHA256):
        raise SourceContractError("Original source research or license contract changed")

    data=abbott_file.read_bytes()
    verify_abbott_source(data,manifest)
    abbott=index_abbott_source_entries(data)
    prior={x["original_rp2018_strong_number"]:x for x in
            lsj_prev["source_lexicon_candidate_key_research_cases"]}
    source_books={x["rp2018_original_editor_strong_number"]:x for x in original["cases"]}
    cases=[]
    for spec in lsj_manifest["file_specs"]:
        target=spec["research_editor_strong"]
        if target not in TARGETS or target not in prior or target not in source_books:
            raise SourceContractError("Unrecognized original RP2018 Greek research target")
        xml=(lsj_source_dir/spec["filename"]).read_bytes()
        verify_original_lsj(xml,spec)
        lsj_index=source_entry_key_index(xml.decode("utf-8",errors="strict"))
        expected=RESEARCH_QUERIES[target]["lsj_source_entry_key_query"]
        diag=inspect_lsj_source_keys(lsj_index,expected)
        prev=prior[target]
        if (diag["exact_original_source_key_matches_UNREVIEWED"]!=
            prev["exact_lsj_entry_key_matches_NO_OWNERSHIP_OR_MEANING_INFERRED"]
            or source_books[target]["approved_greek_lemma"] is not None):
            raise SourceContractError("Previous pinned original LSJ source evidence drifted")
        cases.append({
            "rp2018_original_strong_number":target,
            "original_rp2018_source_word_occurrences":
                source_books[target]["primary_source_word_positions"],
            "stepbible_native_source_candidate_ids_UNREVIEWED":
                prev["stepbible_dstrong_ids_UNREVIEWED"],
            "abbott_smith_original_source_lexical_entries_UNREVIEWED":
                abbott["case_entries"][target],
            "abbott_original_source_dictionary_entry_count_for_target":
                len(abbott["case_entries"][target]),
            "lsj_source_shard_verified_git_blob_sha1":spec["original_git_blob_sha1"],
            "lsj_original_source_key_diagnostic":diag,
            "original_greek_source_word_context_corpus_sha256":CONTEXT_SHA256,
            "both_lexica_have_interdependencies_NOT_INDEPENDENT_VOTES":True,
            "abbott_original_source_lemma_equals_rp2018_verified":False,
            "english_source_gloss_equal_to_olt_translation":False,
            "selected_lsj_entry_id":None,
            "selected_abbott_lexical_sense":None,
            "contextual_greek_lemma_approved":None,
            "owner_english_master_word":None,
            "independent_philological_signoff":False,
            "owner_editorial_approval":False,
            "publication_status":"BLOCKED",
        })
    if [x["rp2018_original_strong_number"] for x in cases]!=list(TARGETS):
        raise SourceContractError("Source dossiers missing one original case")

    return {
        "checkpoint":CHECKPOINT,
        "source_evidence_status":"INDEPENDENT_KOINE_SOURCE_AND_LSJ_ORTHOGRAPHY_DIAGNOSTIC_NOT_APPROVED",
        "source_abbott_lexicon_pinned_commit":manifest["upstream_pinned_commit"],
        "source_abbott_original_git_blob_sha1":manifest["upstream_source_git_blob_sha1"],
        "source_abbott_license_status":"PUBLIC_DOMAIN_AS_STATED_BY_UPSTREAM_PROJECT",
        "source_abbott_citation":manifest["bibliography"],
        "source_lsj_pinned_commit":lsj_manifest["upstream_pinned_commit"],
        "source_lsj_license":"CC BY-SA 4.0",
        "source_lsj_attribution":lsj_manifest["attribution"],
        "frozen_lsj_original_key_snapshot_sha256":LSJ_PREVIOUS_SHA256,
        "frozen_rp2018_greek_context_snapshot_sha256":CONTEXT_SHA256,
        "source_abbott_entries_in_full_original_teixml":abbott["original_xml_entry_count"],
        "source_abbott_entries_with_native_n_attribute":
            abbott["original_entries_with_native_n_attribute"],
        "original_greek_word_positions_crosschecked":[
            x["original_rp2018_source_word_occurrences"] for x in cases],
        "source_cases":cases,
        "machine_approved_lexical_senses":0,
        "human_approved_lexical_senses":0,
        "independently_signed_greek_lemma_assignments":0,
        "approved_english_master_entries":0,
        "published_scripture_verses":0,
        "publication_status":"BLOCKED",
    }


def serialize_report(report:dict[str,Any])->str:
    return json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n"


def require_exact_checkpoint(report:dict[str,Any],root:Path=ROOT)->None:
    p=root/REPORT_PATH
    if not p.is_file() or p.read_text(encoding="utf-8")!=serialize_report(report):
        raise SourceContractError("OLT-037E original Koine lexicon source report absent or drifted")


def emit_initial_checkpoint(report:dict[str,Any])->None:
    raw=serialize_report(report).encode("utf-8")
    print("OLT037E_CHECKPOINT_BEGIN")
    b64=base64.b64encode(raw).decode("ascii")
    for i in range(0,len(b64),4000):
        print("OLT037E_CHECKPOINT_PART "+b64[i:i+4000])
    print("OLT037E_CHECKPOINT_END "+hashlib.sha256(raw).hexdigest())


def main()->int:
    p=argparse.ArgumentParser(description="Original Abbott-Smith and LSJ source diagnostics only")
    p.add_argument("--abbott",type=Path,required=True)
    p.add_argument("--lsj-dir",type=Path,required=True)
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--audit",action="store_true")
    modes.add_argument("--emit-initial-checkpoint",action="store_true")
    modes.add_argument("--verify-checkpoint",action="store_true")
    args=p.parse_args()
    report=build_source_crosscheck(args.abbott,args.lsj_dir)
    if args.emit_initial_checkpoint:
        emit_initial_checkpoint(report)
    elif args.verify_checkpoint:
        require_exact_checkpoint(report)
        print(json.dumps({"checkpoint":CHECKPOINT,
           "exact_koine_and_lsj_source_crosscheck_reproduced":True,
           "case_count":len(report["source_cases"]),
           "publication_status":"BLOCKED"},indent=2))
    else:
        print(serialize_report(report),end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
