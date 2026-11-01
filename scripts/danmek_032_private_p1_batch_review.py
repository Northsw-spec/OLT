"""DANMEK-032: private, unapproved, finite P1 English role review batches.

Read the owner's existing private DANMEK-031 priority report and independently
reconfirm its aggregated source snapshot. All historical P1 candidates remain
UNAPPROVED. Never infer a subject, alter CHES or any older reader, or publish
licensed verse English. Output is a separate immutable private workspace.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import stat

from scripts.ches_014_offline_english_bridge import _private_archive_root
from scripts.danmek_027_multiclause_subject_first import (
    _safe_dir, _write_once, DanMek027Error,
)
from scripts.danmek_030_reviewed_english_subject_order import (
    SCHEMA as APPROVAL_SCHEMA, RULE_KEYS, _candidate_rules,
)
from scripts.danmek_031_private_english_priority_triage import (
    REVISION as SOURCE_SCHEMA, HISTORICAL_WITH_PAIRS, HISTORICAL_NO_PAIRS,
    triage_private_english_roles,
)

REVISION = "DANMEK-032-PRIVATE-P1-BATCHED-REVIEW-v1"
MAX_SOURCE_BYTES = 50_000_000
MAX_BATCH_SIZE = 50
MAX_SOURCE_CASES = 100_000
PRIORITY_NAME = re.compile(r"priority-[a-f0-9]{20}\.json\Z")


class DanMek032Error(ValueError):
    """Fixed-code failure; no private English or path disclosure."""


def _load_priority_report(folder: Path, current: dict) -> tuple[dict, bytes]:
    root = folder.parent / "ches-subject-triage"
    if (root.is_symlink() or not root.is_dir()
            or stat.S_IMODE(root.stat().st_mode) & 0o077):
        raise DanMek032Error("PRIVATE_PRIORITY_REPORT_DIRECTORY_MISSING_OR_UNSAFE")
    names = [p for p in root.iterdir() if PRIORITY_NAME.fullmatch(p.name)]
    if len(names) != 1:
        raise DanMek032Error("REQUIRE_ONE_PRIVATE_PRIORITY_JSON")
    path = names[0]
    if (path.is_symlink() or not path.is_file()
            or stat.S_IMODE(path.stat().st_mode) & 0o077
            or not 0 < path.stat().st_size <= MAX_SOURCE_BYTES):
        raise DanMek032Error("PRIVATE_PRIORITY_JSON_MISSING_OR_UNSAFE")
    blob = path.read_bytes()
    if (len(blob) != path.stat().st_size
            or hashlib.sha256(blob).hexdigest()[:20]
            != path.name.removeprefix("priority-").removesuffix(".json")):
        raise DanMek032Error("PRIVATE_PRIORITY_JSON_CONTENT_CHANGED")
    try:
        def no_duplicates(pairs: list[tuple[str, object]]) -> dict:
            data: dict = {}
            for name, value in pairs:
                if name in data:
                    raise DanMek032Error("PRIVATE_PRIORITY_DUPLICATE_JSON_KEY")
                data[name] = value
            return data
        data = json.loads(
            blob.decode("utf-8"), object_pairs_hook=no_duplicates,
            parse_constant=lambda _x: (_ for _ in ()).throw(
                DanMek032Error("PRIVATE_PRIORITY_NONFINITE_JSON")
            ),
        )
    except (UnicodeError, ValueError, TypeError):
        raise DanMek032Error("PRIVATE_PRIORITY_JSON_INVALID") from None
    if (type(data) is not dict
            or data.get("schema") != SOURCE_SCHEMA
            or data.get("all_cases_unapproved") is not True
            or data.get("publication_status") != "BLOCKED"
            or data.get("source_owner_reader_snapshot") !=
            current["source_owner_reader_snapshot"]
            or data.get("source_chapters_scanned") !=
            current["source_chapters_scanned"]
            or data.get("source_verses_scanned") != current["source_verses_scanned"]
            or data.get("historical_english_ambiguities_seen") !=
            current["historical_english_ambiguities_seen"]
            or data.get("english_subject_review_candidates_seen") !=
            current["all_role_candidates"]
            or type(data.get("cases")) is not list
            or len(data["cases"]) != current["review_verses_queued"]
            or len(data["cases"]) > MAX_SOURCE_CASES):
        raise DanMek032Error("PRIVATE_PRIORITY_REPORT_STALE_OR_INCOMPLETE")
    return data, blob


def _p1_only(
    data: dict, current: dict,
) -> tuple[list[dict], list[dict]]:
    """Validate candidate fields and historical group, never approve."""
    cases: list[dict] = []
    rules: list[dict] = []
    historical_refs: set[str] = set()
    seen: set[str] = set()
    p2 = 0
    total_pairs = 0
    for row in data["cases"]:
        if (type(row) is not dict or type(row.get("reference")) is not str
                or row["reference"] in seen
                or type(row.get("candidate_count")) is not int
                or type(row.get("candidates")) is not list
                or len(row["candidates"]) != row["candidate_count"]
                or type(row.get("review_priority")) is not str
                or row.get("all_candidates_unapproved") is not True
                or row.get("correction_automatically_applied") is not False):
            raise DanMek032Error("PRIVATE_PRIORITY_CASE_INVALID")
        seen.add(row["reference"])
        total_pairs += row["candidate_count"]
        if row["review_priority"] in (HISTORICAL_WITH_PAIRS, HISTORICAL_NO_PAIRS):
            if row.get("historical_english_regex_ambiguity") is not True:
                raise DanMek032Error("PRIVATE_PRIORITY_HISTORICAL_FLAG_MISMATCH")
            historical_refs.add(row["reference"])
        if row["review_priority"] == HISTORICAL_NO_PAIRS:
            p2 += 1
            if row["candidate_count"] != 0:
                raise DanMek032Error("PRIVATE_PRIORITY_P2_WITH_PAIRS")
        elif row["review_priority"] == HISTORICAL_WITH_PAIRS:
            if (row["candidate_count"] < 1
                    or type(row.get("english_verse_text")) is not str):
                raise DanMek032Error("PRIVATE_PRIORITY_P1_WITHOUT_ENGLISH")
            expected = _candidate_rules(
                reference=row["reference"],
                chapter_sha256=row["candidates"][0]["source_chapter_sha256"],
                verse=row["english_verse_text"],
            )
            if row["candidates"] != expected:
                raise DanMek032Error("PRIVATE_PRIORITY_ENGLISH_PAIR_MISMATCH")
            for candidate in row["candidates"]:
                if (type(candidate) is not dict or set(candidate) != RULE_KEYS
                        or candidate["english_subject_role_reviewed"] is not False
                        or candidate["review_note"] != ""):
                    raise DanMek032Error("PRIVATE_PRIORITY_CANDIDATE_NOT_UNAPPROVED")
            cases.append(row)
            rules.extend(row["candidates"])
    if (total_pairs != current["all_role_candidates"]
            or len(historical_refs) !=
            current["historical_english_ambiguities_seen"]
            or len(cases) != current["historical_verses_with_role_candidates"]
            or p2 != current["historical_verses_without_role_candidates"]
            or len(rules) != current["historical_role_candidates"]):
        raise DanMek032Error("PRIVATE_PRIORITY_HISTORICAL_OVERLAP_CHANGED")
    return sorted(cases, key=lambda x: x["reference"]), rules


def _frame(title: str, body: str) -> bytes:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        "<title>" + html.escape(title, quote=True) + "</title>"
        "<style>body{font:16px/1.5 Georgia,serif;max-width:980px;"
        "margin:2rem auto;padding:0 1rem;background:#faf9f6;color:#252525}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:.8rem;"
        "background:#eceae6}section{padding:1rem 0;border-bottom:1px solid #bbb}"
        "h2{font:600 20px system-ui}li{padding:.25rem}</style>"
        "</head><body>" + body + "</body></html>\n"
    ).encode("utf-8")


def _batch_page(index: int, rows: list[dict]) -> bytes:
    esc = lambda value: html.escape(str(value), quote=True)
    sections = []
    for row in rows:
        candidates = "".join(
            "<li>Candidate " + esc(r["candidate_ordinal"]) +
            ": <code>" + esc(r["observed_verb_gloss"]) + "</code> / " +
            "<code>" + esc(r["observed_adjacent_noun_phrase"]) + "</code> — " +
            esc(r["english_role_class"]) + " — <b>UNAPPROVED</b></li>"
            for r in row["candidates"]
        )
        sections.append(
            "<section><h2>" + esc(row["reference"]) +
            "</h2><pre>" + esc(row["english_verse_text"]) +
            "</pre><ol>" + candidates + "</ol>"
            "<p>No automatic approval. Verify English subject vs. direct "
            "object in the complete clause context before individually "
            "authorizing any correction.</p></section>"
        )
    return _frame(
        "DANMEK-032 private P1 batch " + str(index),
        "<h1>DANMEK-032 — historical English ambiguities, batch " +
        str(index) + "</h1><p>Review context only; CHES remains "
        "authoritative for lexical choices. No Hebrew crosscheck, "
        "no automatic corrections, no publication.</p>" +
        '<p><a href="index.html">Back to private index</a></p>' +
        "".join(sections),
    )


def build_private_p1_batches(
    private_root: Path, *, require_311: bool = False,
    write_private_batches: bool = False,
    batch_size: int = 25,
) -> dict:
    if (type(require_311) is not bool
            or type(write_private_batches) is not bool
            or type(batch_size) is not int
            or not 1 <= batch_size <= MAX_BATCH_SIZE):
        raise DanMek032Error("INVALID_P1_BATCH_PARAMETERS")
    try:
        folder = _private_archive_root(private_root)
        current = triage_private_english_roles(
            folder, require_311=require_311, write_private_report=False,
        )
        data, source_bytes = _load_priority_report(folder, current)
        cases, rules = _p1_only(data, current)
        count = (len(cases) + batch_size - 1) // batch_size
        snapshot = "p1-" + hashlib.sha256(
            REVISION.encode("ascii") + b":" + source_bytes +
            b":" + str(batch_size).encode("ascii")
        ).hexdigest()[:24]
        if write_private_batches:
            root = folder.parent / "ches-subject-batches"
            _safe_dir(root)
            dest = root / snapshot
            _safe_dir(dest)
            names = []
            for i in range(count):
                name = "batch-" + str(i + 1).zfill(3) + ".html"
                names.append(name)
                page = _batch_page(
                    i + 1, cases[i * batch_size:(i + 1) * batch_size],
                )
                _write_once(dest, name, page)
            seed = {
                "schema": APPROVAL_SCHEMA,
                "source_owner_reader_snapshot":
                    current["source_owner_reader_snapshot"],
                "rules": rules,
            }
            starter = (
                json.dumps(seed, sort_keys=True, ensure_ascii=False, indent=2)
                + "\n"
            ).encode("utf-8")
            _write_once(dest, "UNAPPROVED-review-starter.json", starter)
            links = "".join(
                "<li><a href='" + html.escape(name, quote=True) + "'>" +
                "Batch " + str(i + 1) + "</a></li>"
                for i, name in enumerate(names)
            )
            home = _frame(
                "DANMEK-032 English P1 review batches",
                "<h1>Historical English ambiguity review</h1>"
                "<p>Unapproved working material. No automatic subject "
                "corrections. This index organizes the existing historical "
                "P1 cases into small batches. All English stays private.</p>"
                "<p>The separate UNAPPROVED-review-starter.json contains "
                "only unapproved DANMEK-030 candidate fields. It is NOT "
                "the active approved.json, and generates no correction.</p>"
                "<ul>" + links + "</ul>",
            )
            _write_once(dest, "index.html", home)
        return {
            "checkpoint": REVISION,
            "mode": (
                "PRIVATE_P1_BATCH_REVIEW_UNAPPROVED" if write_private_batches
                else "P1_BATCH_METADATA_ONLY_NO_FILES"
            ),
            "source_owner_reader_snapshot":
                current["source_owner_reader_snapshot"],
            "source_chapters_scanned": current["source_chapters_scanned"],
            "source_verses_scanned": current["source_verses_scanned"],
            "historical_english_ambiguities": 
                current["historical_english_ambiguities_seen"],
            "historical_p1_verses": len(cases),
            "historical_p2_unmatched_verses":
                current["historical_verses_without_role_candidates"],
            "historical_p1_candidate_pairs": len(rules),
            "additional_nonhistorical_candidate_pairs":
                current["additional_nonhistorical_role_candidates"],
            "total_candidate_pairs": current["all_role_candidates"],
            "batch_size": batch_size,
            "number_of_private_p1_batches": count,
            "new_private_batch_snapshot_id": snapshot,
            "new_private_files_written_or_verified":
                count + 2 if write_private_batches else 0,
            "subject_corrections_approved_by_this_tool": 0,
            "approved_manifest_modified": False,
            "original_ches_modified": False,
            "locked_readers_modified": False,
            "hebrew_cross_validation_performed": False,
            "private_source_text_on_stdout": False,
            "publication_status": "BLOCKED",
        }
    except DanMek032Error:
        raise
    except DanMek027Error as exc:
        raise DanMek032Error(str(exc)) from None
    except Exception:
        raise DanMek032Error("PRIVATE_P1_BATCH_REVIEW_FAILED") from None


def main() -> int:
    p = argparse.ArgumentParser(
        description="DANMEK-032 private P1 English grammar review batches"
    )
    p.add_argument("--private-root", type=Path, required=True)
    p.add_argument("--confirm-machine-readable-use-permission",
                   action="store_true")
    opts = p.add_mutually_exclusive_group(required=True)
    opts.add_argument("--audit-only", action="store_true")
    opts.add_argument("--write-private-p1-batches", action="store_true")
    p.add_argument("--batch-size", type=int, default=25)
    p.add_argument("--require-311", action="store_true")
    a = p.parse_args()
    if not a.confirm_machine_readable_use_permission:
        p.error("Private CHES use permission must be confirmed")
    try:
        report = build_private_p1_batches(
            a.private_root, require_311=a.require_311,
            write_private_batches=a.write_private_p1_batches,
            batch_size=a.batch_size,
        )
    except DanMek032Error:
        p.exit(2, "DANMEK_032_PRIVATE_P1_BATCH_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
