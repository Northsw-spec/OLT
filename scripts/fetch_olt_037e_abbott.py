"""OLT-037E: fetch exact pinned Abbott-Smith TEI and verify PD source statement.

Original 1922 Abbott-Smith Greek NT lexicon and project's TEI are described
as public domain by the translatable-exegetical-tools project. Fetch only
immutable upstream commit, verify both source text and original README
Git blob objects; never download from moving master or accept guessed bytes.
Original source is research evidence, never approval of a Greek sense.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from olt_core.engine import SourceContractError
from scripts.fetch_olt_037d_lsj import git_blob_sha1

MANIFEST_PATH="data/engine/olt_037e_abbott_smith_source_manifest.json"
PIN="8c00cb244761aa23659421a8cbbbf7a3b27b7d59"
SOURCE_SHA="e10dcfa534dbc71168ca6ac273e991348bab2bb2"
README_SHA="64eda828221708e54d3b23d2d8a1c17b1e76a1ef"
SOURCE_LENGTH=5698817
README_LENGTH=4416
SOURCE_LICENSE_SENTENCE=("The lexicon (abbott-smith.tei.xml), including the marked "
                         "up version in this repository, is in the public domain.")


def read_abbott_manifest(root:Path=ROOT)->dict:
    p=root/MANIFEST_PATH
    d=json.loads(p.read_text(encoding="utf-8"))
    checks={
       "checkpoint":"OLT-037E",
       "upstream_repository":"https://github.com/translatable-exegetical-tools/Abbott-Smith",
       "upstream_pinned_commit":PIN,
       "upstream_source_path":"abbott-smith.tei.xml",
       "upstream_source_git_blob_sha1":SOURCE_SHA,
       "upstream_source_byte_length":SOURCE_LENGTH,
       "upstream_readme_git_blob_sha1":README_SHA,
       "source_license_statement":SOURCE_LICENSE_SENTENCE,
       "source_license_status":"PUBLIC_DOMAIN_AS_STATED_BY_UPSTREAM_PROJECT",
       "digital_marked_up_corpus_is_a_separate_edition_from_rp2018":True,
       "research_case_numbers":["3004","3754"],
       "original_source_never_vendored":True,
       "source_tei_and_glosses_are_research_evidence_only":True,
       "approved_greek_lemma_identity":False,
       "approved_lexical_sense":False,
       "approved_english_master_entry":False,
       "approved_nt_publication":False,
       "publication_status":"BLOCKED"
    }
    if any(d.get(k)!=v for k,v in checks.items()):
       raise SourceContractError("Original independent Koine lexicon identity/license/approval changed")
    return d


def verify_abbott_source(data:bytes,manifest:dict)->None:
    if len(data)!=SOURCE_LENGTH or git_blob_sha1(data)!=SOURCE_SHA:
       raise SourceContractError("Abbott-Smith TEI source is not the original pinned Git blob")
    try: txt=data.decode("utf-8",errors="strict")
    except UnicodeDecodeError as exc:
       raise SourceContractError("Pinned Abbott-Smith TEI source not UTF-8") from exc
    if (not txt.lstrip().startswith('<?xml version="1.0"') or
        "<teiHeader>" not in txt or "<entry " not in txt or
        "ABBOTT-SMITH" not in txt[:14000].upper()):
       raise SourceContractError("Original Abbott-Smith source XML header or entries absent")
    if manifest["publication_status"]!="BLOCKED":
       raise SourceContractError("Source download would bypass publication control")


def verify_original_readme(raw:bytes)->None:
    if len(raw)!=README_LENGTH or git_blob_sha1(raw)!=README_SHA:
       raise SourceContractError("Original upstream PD licensing statement not source-pinned")
    try: content=raw.decode("utf-8",errors="strict")
    except UnicodeDecodeError as exc: raise SourceContractError("Invalid original README") from exc
    if SOURCE_LICENSE_SENTENCE not in content:
       raise SourceContractError("Public-domain statement not found in pinned original README")


def _download(path:str,size:int)->bytes:
    url=("https://raw.githubusercontent.com/translatable-exegetical-tools/"
         "Abbott-Smith/"+PIN+"/"+path)
    req=Request(url,headers={"User-Agent":"OLT-037E-verify-original-source/1.0"})
    try:
       with urlopen(req,timeout=90) as response:
          if response.status!=200: raise SourceContractError("Original source returned non-200 HTTP")
          return response.read(size+1)
    except OSError as exc:
       raise SourceContractError("Could not fetch immutable original Abbott-Smith source") from exc


def fetch_original_abbott(out:Path,root:Path=ROOT)->Path:
    manifest=read_abbott_manifest(root)
    if out.exists():
       raise SourceContractError("Refusing to overwrite an existing independent lexicon source")
    if not out.parent.is_dir():
       raise SourceContractError("Output must be in a preexisting temporary directory")
    original_readme=_download("README.md",README_LENGTH)
    verify_original_readme(original_readme)
    original_xml=_download(manifest["upstream_source_path"],SOURCE_LENGTH)
    verify_abbott_source(original_xml,manifest)
    out.write_bytes(original_xml)
    if out.read_bytes()!=original_xml:
       raise SourceContractError("Original XML source changed after writing")
    print(json.dumps({
       "source":"Abbott-Smith Greek NT lexicon, 1922; public domain per verified project README",
       "source_commit":PIN,
       "source_original_git_blob_sha1":SOURCE_SHA,
       "source_verified_bytes":len(original_xml),
       "upstream_original_readme_git_blob_sha1":README_SHA,
       "lexical_review":"NOT_DONE",
       "publication_status":"BLOCKED"
    },ensure_ascii=False,sort_keys=True))
    return out


def main()->int:
    ap=argparse.ArgumentParser(description="Read-only pinned public-domain Koine Greek source fetch")
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    fetch_original_abbott(args.output)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
