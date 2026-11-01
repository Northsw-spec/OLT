"""DANMEK-031: privacy-preserving priority triage of real English review cases.

Never assume the historical 311 regex-ambiguous verses are grammatical
errors, or that all 4,142 source-dependent candidates are subjects.
This tool scans only private CHES-derived English using the existing
DANMEK-030 guarded presentation and emits aggregate counters by default.
An explicit option writes a *separate*, immutable private priority report.
No edits to CHES, approved manifests, or reader snapshots.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path

from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import (
    NAME as CHES_FILE_NAME, build_private_reader,
)
from scripts.danmek_025_private_english_grammar import _private_write_once
from scripts.danmek_029_private_english_clause_review import (
    OBJECT_RISK, UNRESOLVED,
)
from scripts.danmek_030_reviewed_english_subject_order import (
    _candidate_rules, _read_source_text,
)

REVISION = "DANMEK-031-PRIVATE-PRIORITY-TRIAGE-v1"
MAX_CHAPTERS = 1100
MAX_CASES = 100000
MAX_OUTPUT_BYTES = 50000000

HISTORICAL_WITH_PAIRS = "P1_HISTORICAL_AMBIGUITY_WITH_ENGLISH_CANDIDATES"
HISTORICAL_NO_PAIRS = "P2_HISTORICAL_AMBIGUITY_WITHOUT_MATCHED_CANDIDATE"
OTHER_OBJECT_RISK = "P3_OTHER_TRANSITIVE_OBJECT_RISK_CANDIDATES"
OTHER_UNRESOLVED = "P4_OTHER_UNRESOLVED_ENGLISH_CANDIDATES"
PRIORITIES = (
    HISTORICAL_WITH_PAIRS, HISTORICAL_NO_PAIRS,
    OTHER_OBJECT_RISK, OTHER_UNRESOLVED,
)


class DanMek031Error(ValueError):
    """Fixed failure code, never include CHES text or the private path."""


def classify_private_priority(
    *, historical: bool, candidate_classes: list[str],
) -> str | None:
    """Returns a **review priority**, not a verdict on correctness."""
    if type(historical) is not bool or type(candidate_classes) is not list:
        raise DanMek031Error("INVALID_PRIVATE_PRIORITY_CLASS_INPUT")
    if any(c not in (OBJECT_RISK, UNRESOLVED) for c in candidate_classes):
        raise DanMek031Error("UNKNOWN_PRIVATE_PRIORITY_ROLE")
    if historical:
        return HISTORICAL_WITH_PAIRS if candidate_classes else HISTORICAL_NO_PAIRS
    if OBJECT_RISK in candidate_classes:
        return OTHER_OBJECT_RISK
    if candidate_classes:
        return OTHER_UNRESOLVED
    return None


def _private_html(cases: list[dict], snapshot_id: str) -> bytes:
    esc = lambda text: html.escape(str(text), quote=True)
    sections = []
    for case in cases:
        evidence = "".join(
            "<li>Pair " + esc(row["candidate_ordinal"]) +
            ": " + esc(row["observed_verb_gloss"]) + " / " +
            esc(row["observed_adjacent_noun_phrase"]) + " — " +
            esc(row["english_role_class"]) +
            " — <strong>UNAPPROVED</strong></li>"
            for row in case["candidates"]
        ) or "<li>No bounded English candidate; historical ambiguity still requires review</li>"
        sections.append(
            '<details><summary>' + esc(case["reference"]) + " — " +
            esc(case["review_priority"]) +
            "</summary><pre>" + esc(case["english_verse_text"]) +
            "</pre><ol>" + evidence + "</ol></details>"
        )
    result = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        "<title>DANMEK-031 private English role-priority queue</title>"
        "<style>body{font:16px/1.5 Georgia,serif;max-width:960px;"
        "margin:2rem auto;padding:0 1rem;background:#faf9f7;color:#222}"
        "details{border:1px solid #bbb;padding:.6rem;margin:.5rem 0}"
        "summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;"
        "background:#eeece8;padding:.6rem}</style></head><body>"
        "<h1>DANMEK-031: private review order, not grammatical proof</h1>"
        "<p>Snapshot " + esc(snapshot_id) +
        ". P1/P2: historical English regex ambiguity. P3/P4: additional "
        "English role candidates. No automatic correction, and no Hebrew "
        "crosscheck or publication approval.</p>" +
        "".join(sections) + "</body></html>\n"
    ).encode("utf-8")
    if len(result) > MAX_OUTPUT_BYTES:
        raise DanMek031Error("PRIVATE_PRIORITY_HTML_SIZE_LIMIT")
    return result


def triage_private_english_roles(
    private_root: Path, *, require_311: bool = False,
    write_private_report: bool = False,
) -> dict:
    """Prioritize real locally present English review cases, not source edits.

    Historical ambiguity and current English role-candidate detection are
    independent dimensions. Both are always represented; no cases dropped.
    """
    if type(require_311) is not bool or type(write_private_report) is not bool:
        raise DanMek031Error("INVALID_PRIVATE_TRIAGE_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        old_reader = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        cases: list[dict] = []
        by_priority: Counter[str] = Counter()
        role_totals: Counter[str] = Counter()
        chapters = verses = historical = total_candidates = 0
        historical_candidate_pairs = historical_with_pairs = 0
        legacy_with_no_pair = 0
        other_candidates = 0
        digest = hashlib.sha256(
            (REVISION + ":" + old_reader["snapshot_id"]).encode("ascii")
        )
        for source_file in sorted(folder.iterdir(), key=lambda p: p.name):
            if source_file.is_symlink() or not source_file.is_file():
                raise DanMek031Error("PRIVATE_TRIAGE_SOURCE_ENTRY_UNSAFE")
            match = CHES_FILE_NAME.fullmatch(source_file.name)
            if match is None:
                raise DanMek031Error("PRIVATE_TRIAGE_SOURCE_ENTRY_INVALID")
            prefix, number = match.groups()
            source, sha = _load_private_source(
                folder, prefix=prefix, chapter=int(number),
            )
            chapters += 1
            if chapters > MAX_CHAPTERS:
                raise DanMek031Error("PRIVATE_TRIAGE_CHAPTER_LIMIT")
            digest.update((source_file.name + ":" + sha + "\n").encode("ascii"))
            for verse in source["verses"]:
                verses += 1
                ref = verse["reference"]
                original = [
                    span["original_ches_line_text"]
                    for span in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                english, status = _read_source_text(
                    original, reference=ref, chapter_sha256=sha,
                )
                is_historical = status == "AMBIGUOUS"
                historical += int(is_historical)
                matches = _candidate_rules(
                    reference=ref, chapter_sha256=sha, verse=english,
                )
                candidate_classes = [x["english_role_class"] for x in matches]
                priority = classify_private_priority(
                    historical=is_historical, candidate_classes=candidate_classes,
                )
                total_candidates += len(matches)
                if is_historical:
                    historical_candidate_pairs += len(matches)
                    historical_with_pairs += int(bool(matches))
                    legacy_with_no_pair += int(not matches)
                else:
                    other_candidates += len(matches)
                for klass in candidate_classes:
                    role_totals[klass] += 1
                if priority is None:
                    continue
                by_priority[priority] += 1
                cases.append({
                    "reference": ref,
                    "review_priority": priority,
                    "historical_english_regex_ambiguity": is_historical,
                    "english_verse_text": english,
                    "candidate_count": len(matches),
                    "candidates": matches,
                    "all_candidates_unapproved": True,
                    "english_role_certified_by_triage": False,
                    "correction_automatically_applied": False,
                })
                if len(cases) > MAX_CASES:
                    raise DanMek031Error("PRIVATE_PRIORITY_CASE_LIMIT")
        if (verses != old_reader["observed_verse_count"]
                or historical !=
                old_reader["olt_owner_candidate_ambiguous_verses_unchanged"]):
            raise DanMek031Error("PRIVATE_PRIORITY_BASELINE_MISMATCH")
        if require_311 and historical != 311:
            raise DanMek031Error("HISTORICAL_311_ENGLISH_CASE_COUNT_CHANGED")
        if old_reader != build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek031Error("PRIVATE_PRIORITY_SOURCE_CHANGED")
        snapshot_id = "triage-" + digest.hexdigest()[:24]
        if write_private_report:
            cases.sort(key=lambda row: (
                PRIORITIES.index(row["review_priority"]), row["reference"],
            ))
            document = {
                "schema": REVISION,
                "snapshot_id": snapshot_id,
                "source_owner_reader_snapshot": old_reader["snapshot_id"],
                "all_cases_unapproved": True,
                "english_only": True,
                "source_chapters_scanned": chapters,
                "source_verses_scanned": verses,
                "historical_english_ambiguities_seen": historical,
                "english_subject_review_candidates_seen": total_candidates,
                "cases": cases,
                "publication_status": "BLOCKED",
            }
            data = (
                json.dumps(document, sort_keys=True, ensure_ascii=False, indent=2)
                + "\n"
            ).encode("utf-8")
            if len(data) > MAX_OUTPUT_BYTES:
                raise DanMek031Error("PRIVATE_PRIORITY_JSON_SIZE_LIMIT")
            page = _private_html(cases, snapshot_id)
            parent = folder.parent / "ches-subject-triage"
            identifier = hashlib.sha256(data).hexdigest()[:20]
            _private_write_once(parent, "priority-" + identifier + ".json", data)
            _private_write_once(parent, "priority-" + identifier + ".html", page)
        return {
            "checkpoint": REVISION,
            "mode": (
                "PRIVATE_PRIORITY_REPORT_UNAPPROVED" if write_private_report
                else "AGGREGATE_ONLY_NO_FILES"
            ),
            "source_owner_reader_snapshot": old_reader["snapshot_id"],
            "source_chapters_scanned": chapters,
            "source_verses_scanned": verses,
            "historical_english_ambiguities_seen": historical,
            "historical_verses_with_role_candidates": historical_with_pairs,
            "historical_verses_without_role_candidates": legacy_with_no_pair,
            "historical_role_candidates": historical_candidate_pairs,
            "additional_nonhistorical_role_candidates": other_candidates,
            "all_role_candidates": total_candidates,
            "priority_verse_counts": {
                label: by_priority[label] for label in PRIORITIES
            },
            "role_candidate_counts": dict(sorted(role_totals.items())),
            "review_verses_queued": len(cases),
            "approved_grammar_corrections": 0,
            "new_english_reading_created": False,
            "source_ches_edited": False,
            "locked_readers_edited": False,
            "hebrew_translation_crosscheck_performed": False,
            "private_text_on_stdout": False,
            "private_report_files_written_or_verified": (
                2 if write_private_report else 0
            ),
            "publication_status": "BLOCKED",
        }
    except DanMek031Error:
        raise
    except Exception:
        raise DanMek031Error("PRIVATE_ENGLISH_ROLE_TRIAGE_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-031 private English review prioritization; no edits"
    )
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument(
        "--confirm-machine-readable-use-permission", action="store_true",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--write-private-priority-report", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    options = parser.parse_args()
    if not options.confirm_machine_readable_use_permission:
        parser.error("Private source use permission must be confirmed")
    try:
        result = triage_private_english_roles(
            options.private_root, require_311=options.require_311,
            write_private_report=options.write_private_priority_report,
        )
    except DanMek031Error:
        parser.exit(2, "DANMEK_031_PRIVATE_TRIAGE_FAILED\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
