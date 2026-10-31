"""Private incremental CHES OT chapter importer for a user with appropriate rights.

No CHES source text in public Git; no assumption of owner permission to
redistribute, fine-tune models, create Amharic derivatives or publish.
A complete chapter download is NOT independently verified translation.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

from scripts.ches_import import import_private_pdf, write_private_json
from scripts.ches_index import INDEX, parse_index
from scripts.ches_013_structural_exceptions import (
    structural_code, record_structural_exception, resolve_structural_exception,
)

INDEX_BYTES_MAX=3_000_000
PDF_BYTES_MAX=30_000_000
EXPECTED_OT_CHAPTERS=929
EXPECTED_OT_SOURCE_PREFIXES=39
SOURCE_TIMEOUT=60


def fetch_exact_source(url: str, max_size: int) -> bytes:
    parsed=urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc != "www.scripture4all.org"
        or parsed.query or parsed.fragment or
        not parsed.path.startswith("/OnlineInterlinear/")
        or ".." in parsed.path or "%" in parsed.path):
        raise ValueError("Refusing noncanonical untrusted source host or PDF path")
    req=Request(url,headers={"User-Agent":"OLT-CHES-private-academic-reader/0.1"})
    with urlopen(req,timeout=SOURCE_TIMEOUT) as res:
        if res.geturl() != url:
            raise ValueError("Source URL redirected to an unapproved destination")
        raw=res.read(max_size+1)
    if not raw or len(raw)>max_size:
        raise ValueError("Original index/source PDF exceeds bounded private fetch")
    return raw


def validate_inventory(source: bytes) -> dict:
    report=parse_index(source)
    if (report["discovered_chapter_pdf_count"] != EXPECTED_OT_CHAPTERS or
        report["discovered_original_source_filename_prefix_count"] != EXPECTED_OT_SOURCE_PREFIXES or
        report["publication_status"] != "BLOCKED" or
        report["downloaded_chapter_pdf_count"] != 0):
        raise ValueError("Scripture4All original chapter inventory changed; stop")
    return report


def private_batch(index: dict, private_root: Path, *,
                  limit: int,
                  delay_seconds: float = 1.5,
                  continue_on_structural_error: bool = False,
                  fetch=fetch_exact_source) -> dict:
    """Sequential, resumable only, fails closed on the first unsafe chapter."""
    if not 1<=limit<=EXPECTED_OT_CHAPTERS:
        raise ValueError("Unsafe private batch chapter limit")
    if delay_seconds < 1.0:
        raise ValueError("Bulk importer requires a slow per-chapter request delay")
    if type(continue_on_structural_error) is not bool:
        raise ValueError("Unsafe structural exception mode")
    root=private_root.expanduser().resolve()
    if ".olt-private" not in root.parts:
        raise ValueError("Private CHES corpus must reside in .olt-private")
    chapters=index["chapter_links"][:limit]
    imported=resumed=deferred=fetch_attempts=0
    for position, row in enumerate(chapters,1):
        prefix=row["source_book_filename_prefix_NOT_OLT_BOOK_ID"]
        chapter=row["source_chapter_filename_number"]
        url=row["original_pdf_url"]
        if (not re.fullmatch(r"[A-Za-z0-9_-]{1,20}",prefix)
            or not isinstance(chapter,int) or chapter < 1):
            raise ValueError("Untrusted source chapter identity")
        target=root / f"{prefix}.{chapter}.json"
        if target.is_file():
            existing=json.loads(target.read_text(encoding="utf-8"))
            if (existing.get("source_origin_url") != url
                or existing.get("source_book_identifier_is_not_verified_oshb_book_mapping") is not True
                or existing.get("full_source_text_in_public_git_permitted") is not False
                or existing.get("publication_status") != "BLOCKED"
                or not existing.get("verses")
                or not existing.get("original_source_pdf_sha256")):
                raise ValueError("Existing private CHES extract cannot safely resume: "+target.name)
            resumed += 1
            continue
        if fetch_attempts > 0:
            time.sleep(delay_seconds)
        fetch_attempts += 1
        pdf=fetch(url,PDF_BYTES_MAX)
        try:
            result=import_private_pdf(pdf,prefix,chapter)
        except ValueError as exc:
            diagnostic=structural_code(exc)
            if not continue_on_structural_error or diagnostic is None:
                raise
            record_structural_exception(
                root, prefix=prefix, chapter=chapter, pdf_data=pdf,
                index_sha256=index["source_index_html_sha256"],
                diagnostic_code=diagnostic,
            )
            deferred += 1
            print(f"CHES013_SOURCE_EXCEPTION source={prefix}.{chapter} code={diagnostic} "
                  "status=UNRESOLVED release=BLOCKED")
            continue
        result["source_origin_url"]=url
        result["source_original_index_sha256"]=index["source_index_html_sha256"]
        result["owner_attested_machine_readable_permission_no_public_distribution"]=True
        result["source_chapter_verse_count_independent_oshb_qa"]="NOT_DONE"
        write_private_json(result,target)
        # Never silently resolve an exception for *different* source bytes.
        resolve_structural_exception(root,prefix=prefix,chapter=chapter,pdf_data=pdf)
        imported += 1
        print(f"PRIVATE_SOURCE_IMPORT {position}/{len(chapters)} source={prefix}.{chapter} verses={result['verses_extracted']} ches_spans={result['ches_pdf_green_spans']} release=BLOCKED")
    return {
        "index_chapter_count": index["discovered_chapter_pdf_count"],
        "index_source_book_prefix_count": index["discovered_original_source_filename_prefix_count"],
        "selected_chapter_count": len(chapters),
        "newly_imported_to_private_storage": imported,
        "existing_private_chapters_validated_for_resume_only": resumed,
        "deferred_structurally_unreadable_source_chapters": deferred,
        "source_pdf_fetch_attempts": fetch_attempts,
        "selected_chapter_files_present_after_run": imported + resumed,
        "all_selected_chapter_files_present_by_count_only":
            (imported + resumed == len(chapters) and deferred == 0),
        "import_run_status": ("INCOMPLETE_UNRESOLVED_STRUCTURAL_EXCEPTIONS"
                              if deferred else "SELECTED_SOURCE_CHAPTERS_STORED_NOT_CERTIFIED"),
        "original_source_to_oshb_alignment_certified": False,
        "whole_old_testament_chapter_coverage_qa_complete": False,
        "owner_english_scripture_translation_approved": False,
        "amharic_translation_authorized": False,
        "publication_status": "BLOCKED"
    }


def main() -> int:
    parser=argparse.ArgumentParser(description="Private sequential CHES OT importer; source-text rights required")
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inventory-only",action="store_true")
    mode.add_argument("--import-first",type=int)
    mode.add_argument("--import-all",action="store_true")
    parser.add_argument("--private-root",type=Path,default=Path(".olt-private/ches"))
    parser.add_argument("--confirm-machine-readable-use-permission",action="store_true")
    parser.add_argument("--delay-seconds",type=float,default=1.5)
    parser.add_argument("--continue-on-structural-error",action="store_true",
                        help="Opt-in: record only known PDF verse-layout problems privately, "
                             "keep importing other chapters, exit nonzero if gaps remain")
    opts=parser.parse_args()
    if opts.inventory_only and opts.continue_on_structural_error:
        parser.error("Exception handling applies only to private chapter imports")
    if not opts.inventory_only and not opts.confirm_machine_readable_use_permission:
        parser.error("Private CHES import requires authorization for machine-readable use")
    index=validate_inventory(fetch_exact_source(INDEX,INDEX_BYTES_MAX))
    if opts.inventory_only:
        print(json.dumps({key:value for key,value in index.items() if key!="chapter_links"},
                         indent=2,sort_keys=True))
        return 0
    limit=EXPECTED_OT_CHAPTERS if opts.import_all else opts.import_first
    report=private_batch(index,opts.private_root,limit=limit,
                         delay_seconds=opts.delay_seconds,
                         continue_on_structural_error=opts.continue_on_structural_error)
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2 if report["deferred_structurally_unreadable_source_chapters"] else 0


if __name__=="__main__":
    raise SystemExit(main())
