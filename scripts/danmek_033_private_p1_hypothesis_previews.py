"""DANMEK-033: exact, PRIVATE, hypothetical English subject-order previews.

This tool NEVER decides whether a candidate noun is a subject or an object.
It displays a counterfactual English reading *if and only if* a human later
determines that the candidate noun is the subject. A possible direct object
is an equally live interpretation. All results are UNAPPROVED and are never
installed as an active DANMEK-030 approval manifest or reading version.

No Hebrew comparison; CHES source wording is accepted for this work.
No licensed CHES English is sent to GitHub, public CI, or CLI stdout.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re

from scripts.ches_014_offline_english_bridge import _private_archive_root
from scripts.danmek_027_multiclause_subject_first import (
    DanMek027Error, _format_subject_before_verb, _safe_dir, _write_once,
)
from scripts.danmek_029_private_english_clause_review import (
    classify_english_clause_pairs, OBJECT_RISK, UNRESOLVED,
)
from scripts.danmek_030_reviewed_english_subject_order import (
    _candidate_rules,
)
from scripts.danmek_031_private_english_priority_triage import (
    DanMek031Error, triage_private_english_roles,
)
from scripts.danmek_032_private_p1_batch_review import (
    DanMek032Error, _load_priority_report, _p1_only,
    build_private_p1_batches,
)

REVISION = "DANMEK-033-PRIVATE-P1-HYPOTHETICAL-ENGLISH-PREVIEWS-v1"
MAX_BATCH_SIZE = 50
MAX_PRIVATE_OUTPUT_BYTES = 50_000_000
MAX_HYPOTHESES = 100_000

class DanMek033Error(ValueError):
    """Fixed error codes without private English, verse text, or file paths."""


def preview_one_unapproved_subject_hypothesis(
    *, verse_english: str, rule: dict,
    trusted_reference: str, trusted_chapter_sha256: str,
) -> str:
    """Return *illustrative* subject-first English, never an approved edit.

    Matches the exact already-stored rule ordinal, original English pair,
    source chapter SHA and complete displayed verse SHA. No normalization,
    guessed grammatical role, or overlapping/partial string replacement.
    """
    if (type(verse_english) is not str or type(rule) is not dict
            or type(trusted_reference) is not str
            or type(trusted_chapter_sha256) is not str):
        raise DanMek033Error("INVALID_UNAPPROVED_HYPOTHESIS_INPUT")
    if (rule.get("reference") != trusted_reference
            or rule.get("source_chapter_sha256") != trusted_chapter_sha256):
        raise DanMek033Error("HYPOTHESIS_TRUSTED_SOURCE_CONTEXT_MISMATCH")
    if (rule.get("english_subject_role_reviewed") is not False
            or rule.get("review_note") != ""):
        raise DanMek033Error("HYPOTHESIS_MUST_REMAIN_UNAPPROVED")
    try:
        reference = rule["reference"]
        sha = rule["source_chapter_sha256"]
        ordinal = rule["candidate_ordinal"]
        expected = _candidate_rules(
            reference=reference, chapter_sha256=sha, verse=verse_english,
        )
        if (type(ordinal) is not int
                or [r for r in expected if r["candidate_ordinal"] == ordinal]
                != [rule]):
            raise DanMek033Error("STALE_UNAPPROVED_HYPOTHESIS_PAIR")
        parsed = [
            r for r in classify_english_clause_pairs([verse_english])
            if r["ordinal"] == ordinal
        ]
        if len(parsed) != 1:
            raise DanMek033Error("HYPOTHESIS_PAIR_NOT_PRESENT")
        observed = parsed[0]
        if observed["english_role_class"] not in (OBJECT_RISK, UNRESOLVED):
            raise DanMek033Error("HYPOTHESIS_ROLE_WAS_NOT_UNRESOLVED")
        left = observed["source_english_position_start"]
        right = observed["source_english_position_end"]
        verb = observed["observed_verb_gloss"]
        noun = observed["observed_adjacent_noun_phrase"]
        if re.fullmatch(
            re.escape(verb) + r"[ \t]+" + re.escape(noun),
            verse_english[left:right],
        ) is None:
            raise DanMek033Error("HYPOTHESIS_PAIR_CONTEXT_CHANGED")
        replacement = _format_subject_before_verb(verb, noun)
        if replacement == verse_english[left:right]:
            raise DanMek033Error("NO_CONDITIONAL_WORD_ORDER_DIFFERENCE")
        return verse_english[:left] + replacement + verse_english[right:]
    except DanMek033Error:
        raise
    except Exception:
        raise DanMek033Error("INVALID_UNAPPROVED_HYPOTHESIS_PAIR") from None


def _generate_unapproved_hypotheses(cases: list[dict]) -> list[dict]:
    hypotheses = []
    for row in cases:
        english = row["english_verse_text"]
        for rule in row["candidates"]:
            alternate = preview_one_unapproved_subject_hypothesis(
                verse_english=english, rule=rule,
                trusted_reference=row["reference"],
                trusted_chapter_sha256=row["candidates"][0]["source_chapter_sha256"],
            )
            hypotheses.append({
                "reference": row["reference"],
                "candidate_ordinal": rule["candidate_ordinal"],
                "english_role_class": rule["english_role_class"],
                "source_chapter_sha256": rule["source_chapter_sha256"],
                "expected_verse_english_sha256":
                    rule["expected_verse_english_sha256"],
                "original_verb_gloss": rule["observed_verb_gloss"],
                "adjacent_noun_phrase":
                    rule["observed_adjacent_noun_phrase"],
                "original_displayed_english": english,
                "if_noun_is_subject_illustrative_english": alternate,
                "if_noun_is_object_or_role_unresolved_english": english,
                "hypothesis_only": True,
                "grammar_subject_proven": False,
                "grammar_object_proven": False,
                "reviewer_approval": "UNAPPROVED",
                "approved_manifest_entry_created": False,
                "actual_reading_modified": False,
                "publication_status": "BLOCKED",
            })
            if len(hypotheses) > MAX_HYPOTHESES:
                raise DanMek033Error("PRIVATE_HYPOTHESIS_LIMIT_EXCEEDED")
    return hypotheses


def _page(title: str, content: str) -> bytes:
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        "<title>" + html.escape(title, quote=True) + "</title>"
        "<style>body{font:16px/1.5 Georgia,serif;max-width:1000px;"
        "margin:2rem auto;padding:0 1rem;background:#faf9f6;color:#242424}"
        "article{border-bottom:1px solid #bbb;padding:1rem 0}"
        "section{padding:.5rem 0;border-left:3px solid #aaa;padding-left:1rem}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#edebe6;"
        "padding:.7rem}h2{font:600 19px system-ui}"
        "h3{font:600 15px system-ui}"
        "small{font:12px system-ui}</style>"
        "</head><body>" + content + "</body></html>\n"
    ).encode("utf-8")
    if len(page) > MAX_PRIVATE_OUTPUT_BYTES:
        raise DanMek033Error("PRIVATE_HYPOTHESIS_HTML_TOO_LARGE")
    return page


def _batch_page(number: int, rows: list[dict]) -> bytes:
    esc = lambda x: html.escape(str(x), quote=True)
    blocks = []
    for row in rows:
        children = []
        for item in row["hypotheses"]:
            children.append(
                "<section><h3>Candidate " + esc(item["candidate_ordinal"]) +
                " — " + esc(item["english_role_class"]) + "</h3>"
                "<p><strong>Interpretation A — IF the noun is a "
                "postposed subject:</strong> hypothetical typography only</p>"
                "<pre>" + esc(item["if_noun_is_subject_illustrative_english"]) +
                "</pre><p><strong>Interpretation B — IF it is an object "
                "or role is unresolved:</strong> preserve the existing "
                "English without movement</p><pre>" +
                esc(item["if_noun_is_object_or_role_unresolved_english"]) +
                "</pre><small>UNAPPROVED. No independent proof of grammatical "
                "role; this preview is NOT an editorial correction.</small>"
                "</section>"
            )
        blocks.append(
            "<article><h2>" + esc(row["reference"]) + "</h2>"
            "<p>Current protected English display:</p><pre>" +
            esc(row["english_verse"]) +
            "</pre>" + "".join(children) + "</article>"
        )
    return _page(
        "DANMEK-033 P1 conditional preview batch " + str(number),
        "<h1>Private P1 conditional English proposals — batch " +
        str(number) + "</h1>"
        "<p>Two competing grammatical readings are kept visible. "
        "None has been proven, reviewed, approved or applied. "
        "CHES English source and previous readings remain unchanged. "
        "No Hebrew crosscheck or publication approval.</p>"
        '<p><a href="index.html">Back to private index</a></p>' +
        "".join(blocks),
    )


def generate_private_p1_hypothesis_previews(
    private_root: Path, *, require_311: bool = False,
    write_private_previews: bool = False,
    batch_size: int = 25,
) -> dict:
    """Revalidate the source and 032 snapshot before proposing private views."""
    if (type(require_311) is not bool
            or type(write_private_previews) is not bool
            or type(batch_size) is not int
            or not 1 <= batch_size <= MAX_BATCH_SIZE):
        raise DanMek033Error("INVALID_PRIVATE_HYPOTHESIS_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        old_batches = build_private_p1_batches(
            folder, require_311=require_311, write_private_batches=False,
            batch_size=batch_size,
        )
        current = triage_private_english_roles(
            folder, require_311=require_311, write_private_report=False,
        )
        data, source_bytes = _load_priority_report(folder, current)
        cases, candidate_rules = _p1_only(data, current)
        if (len(cases) != old_batches["historical_p1_verses"]
                or len(candidate_rules) !=
                old_batches["historical_p1_candidate_pairs"]):
            raise DanMek033Error("PRIVATE_P1_HYPOTHESIS_BASELINE_MISMATCH")
        grouped: list[dict] = []
        role_counts: dict[str, int] = {OBJECT_RISK: 0, UNRESOLVED: 0}
        for row in cases:
            hypothesis = _generate_unapproved_hypotheses([row])
            for item in hypothesis:
                role_counts[item["english_role_class"]] += 1
            grouped.append({
                "reference": row["reference"],
                "english_verse": row["english_verse_text"],
                "hypotheses": hypothesis,
            })
        total = sum(len(row["hypotheses"]) for row in grouped)
        if total != len(candidate_rules):
            raise DanMek033Error("PRIVATE_P1_HYPOTHESIS_COUNT_MISMATCH")
        count = (len(grouped) + batch_size - 1) // batch_size
        snapshot = "preview-" + hashlib.sha256(
            REVISION.encode("ascii") + b":" + source_bytes +
            b":" + str(batch_size).encode("ascii")
        ).hexdigest()[:24]
        if write_private_previews:
            root = folder.parent / "ches-subject-previews"
            _safe_dir(root)
            dest = root / snapshot
            _safe_dir(dest)
            names = []
            for i in range(count):
                name = "batch-" + str(i + 1).zfill(3) + ".html"
                _write_once(
                    dest, name,
                    _batch_page(
                        i + 1, grouped[i * batch_size:(i + 1) * batch_size],
                    ),
                )
                names.append(name)
            payload = {
                "schema": REVISION,
                "source_p1_batch_snapshot":
                    old_batches["new_private_batch_snapshot_id"],
                "owner_reader_snapshot":
                    current["source_owner_reader_snapshot"],
                "source_ches_modified": False,
                "approved_manifest_modified": False,
                "grammar_subject_roles_proven": 0,
                "all_candidates_unapproved": True,
                "hypotheses": [
                    hypothesis
                    for row in grouped for hypothesis in row["hypotheses"]
                ],
                "publication_status": "BLOCKED",
            }
            buffer = (
                json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            ).encode("utf-8")
            if len(buffer) > MAX_PRIVATE_OUTPUT_BYTES:
                raise DanMek033Error("PRIVATE_HYPOTHESIS_JSON_TOO_LARGE")
            _write_once(dest, "UNAPPROVED-hypothetical-previews.json", buffer)
            index = _page(
                "DANMEK-033 P1 review conditional hypotheses",
                "<h1>DANMEK-033 — private P1 conditional preview</h1>"
                "<p>Hypothetical candidate-by-candidate subject-order "
                "alternatives. An adjacent noun can instead be an object. "
                "NO automatic edits, NO grammar proofs, NO approvals. "
                "Source and approved readers remain unchanged.</p>"
                "<ul>" +
                "".join(
                    '<li><a href="' + html.escape(name, quote=True) +
                    '">Batch ' + str(i + 1) + "</a></li>"
                    for i, name in enumerate(names)
                ) + "</ul>",
            )
            _write_once(dest, "index.html", index)
        return {
            "checkpoint": REVISION,
            "mode": (
                "PRIVATE_P1_HYPOTHETICAL_PREVIEW_ONLY"
                if write_private_previews
                else "METADATA_ONLY_NO_FILE_WRITES"
            ),
            "source_owner_reader_snapshot":
                current["source_owner_reader_snapshot"],
            "source_private_p1_batch_snapshot":
                old_batches["new_private_batch_snapshot_id"],
            "source_chapters_scanned": current["source_chapters_scanned"],
            "source_verses_scanned": current["source_verses_scanned"],
            "historical_p1_verses": len(grouped),
            "historical_p1_pair_hypotheses": total,
            "hypotheses_by_english_role": role_counts,
            "unreviewed_alternative_pair_presentations": total,
            "private_html_batches": count,
            "private_files_written_or_verified":
                count + 2 if write_private_previews else 0,
            "new_private_preview_snapshot": snapshot,
            "confirmed_grammar_errors": 0,
            "approved_english_corrections": 0,
            "original_ches_modified": False,
            "approved_manifest_modified": False,
            "prior_readers_modified": False,
            "hebrew_source_crosschecked": False,
            "private_english_in_cli_output": False,
            "publication_status": "BLOCKED",
        }
    except DanMek033Error:
        raise
    except (DanMek031Error, DanMek032Error, DanMek027Error) as error:
        # The called modules are fixed-code exception surfaces only.
        raise DanMek033Error(str(error)) from None
    except Exception:
        raise DanMek033Error("PRIVATE_P1_HYPOTHESIS_PREVIEW_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-033 private, unapproved P1 conditional English"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission",
                        action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--write-private-previews", action="store_true")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--require-311", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private source use permission must be confirmed")
    try:
        report = generate_private_p1_hypothesis_previews(
            args.private_root, require_311=args.require_311,
            write_private_previews=args.write_private_previews,
            batch_size=args.batch_size,
        )
    except DanMek033Error:
        parser.exit(2, "DANMEK_033_PRIVATE_P1_PREVIEWS_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
