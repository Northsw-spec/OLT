"""DANMEK-029: bounded English clause-role review, PRIVATE and read-only.

Owner policy:
- CHES is accepted as the working English authority. No Hebrew/Aramaic
  morph, vocabulary, word alignments, or CHES-accuracy crosschecks are used.
- English subject-first editorial moves are owner-directed only when a
  subject is defensibly identified. A noun after a transitive verb may be
  an object, and an automatically detected pair is NOT a grammar proof.
- DANMEK-013/014 and DANMEK-027/028 snapshots must remain immutable.
- No real CHES English may be committed, printed, or uploaded to CI.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re

from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import (
    NAME as CHES_FILE_NAME, build_private_reader,
)
from scripts.danmek_025_private_english_grammar import _private_write_once
from scripts.danmek_027_multiclause_subject_first import (
    RULES, SUBJECT, _legacy_candidate_guard,
    reorder_postverbal_subjects, MAX_VERSE_CHARS,
)
from scripts.danmek_008_english_display import simplify_sur_faces_for_olt_view
from scripts.danmek_012_display import hide_isolated_c

REVISION = "DANMEK-029-ENGLISH-CLAUSE-ROLE-REVIEW-v1"
MAX_CANDIDATES_PER_VERSE = 80
MAX_PRIVATE_CASES = 50000
MAX_CHAPTERS = 1100

# Review subject/verb-like typography, not the surface meaning of
# Bible text. Does not use a statistical parser or any external service.
_PRONOUN_VERB = (
    r"(?:[Aa]nd[· ])?"
    r"(?:he|she|they|we|thou|ye|you)-"
    r"[a-z]+(?:-[a-z]+){0,6}"
)
_POTENTIAL_POSTVERBAL_PAIR = re.compile(
    r"(?<![A-Za-z-])(?P<verb>" + _PRONOUN_VERB + r")"
    r"[ \t]+(?P<phrase>" + SUBJECT + r")(?![A-Za-z-])"
)
# A word in this list can be a *direct-object-taking* predicate. Classify
# its post-verbal noun as unresolved (object RISK), never proven object.
_TRANSITIVE_VERB_HINTS = frozenset({
    "saw", "see", "sees", "seeing", "heard", "hear", "hears", "hearing",
    "met", "meet", "meets", "meeting", "called", "call", "calls", "calling",
    "loved", "love", "loves", "loving", "made", "make", "makes", "making",
    "blessed", "bless", "blesses", "blessing", "found", "find", "finds",
    "took", "take", "takes", "taking", "built", "build", "builds",
    "returned", "return", "returns", "returning",
    "sent", "send", "sends", "sending",
    "cut", "invited", "invite", "invites", "inviting",
})
PATTERN_SUBJECT = "BOUNDED_ENGLISH_SUBJECT_PATTERN_CANDIDATE"
OBJECT_RISK = "TRANSITIVE_OBJECT_RISK_UNRESOLVED"
UNRESOLVED = "ENGLISH_ROLE_UNRESOLVED_NO_REORDER"


class DanMek029Error(ValueError):
    """Fixed-code, never private English or local paths."""


def classify_english_clause_pairs(
    fragments: list[str | None],
) -> list[dict]:
    """Report *possible* post-verbal noun roles, never apply any correction.

    Parse every candidate in one verse; preserve distinct spans and order.
    Stronger bounded rules yield a subject *candidate*, not a certified
    grammatical subject. Other transitive predicates are object-risk;
    unusual syntax remains unresolved and unchanged.
    """
    if (type(fragments) is not list or not fragments or len(fragments) > 10000
            or any(fragment is not None and type(fragment) is not str
                   for fragment in fragments)):
        raise DanMek029Error("INVALID_ENGLISH_CLAUSE_FRAGMENT_SEQUENCE")
    flat = " ".join(fragment or "" for fragment in fragments)
    if len(flat) > MAX_VERSE_CHARS:
        raise DanMek029Error("ENGLISH_CLAUSE_REVIEW_VERSE_TOO_LONG")
    matches = list(_POTENTIAL_POSTVERBAL_PAIR.finditer(flat))
    if len(matches) > MAX_CANDIDATES_PER_VERSE:
        raise DanMek029Error("ENGLISH_CLAUSE_REVIEW_TOO_MANY_PAIRS")

    accepted_spans: dict[tuple[int, int], str] = {}
    for code, pattern in RULES:
        for match in pattern.finditer(flat):
            key = match.span()
            if key in accepted_spans:
                raise DanMek029Error("ENGLISH_CLAUSE_RULE_OVERLAP")
            accepted_spans[key] = code

    records = []
    for index, match in enumerate(matches, 1):
        reason = accepted_spans.get(match.span())
        if reason is not None:
            status = PATTERN_SUBJECT
        else:
            verb_lexeme = match["verb"].rsplit("-", 1)[-1]
            status = (
                OBJECT_RISK if verb_lexeme in _TRANSITIVE_VERB_HINTS
                else UNRESOLVED
            )
        records.append({
            "ordinal": index,
            "source_english_position_start": match.start(),
            "source_english_position_end": match.end(),
            "observed_verb_gloss": match["verb"],
            "observed_adjacent_noun_phrase": match["phrase"],
            "english_role_class": status,
            "rule_code": reason,
            "subject_syntax_certified": False,
            "object_syntax_certified": False,
            "english_word_order_change_authorized_by_this_tool": False,
            "source_hebrew_aramaic_comparison_performed": False,
        })
    # Every bounded auto-rule match must be represented exactly as a
    # recognized phrase in this independent review, not silently lost.
    represented = {
        (m.start(), m.end()) for m in matches
    }
    if any(span not in represented for span in accepted_spans):
        raise DanMek029Error("ENGLISH_CLAUSE_RULE_NOT_REPRESENTED")
    return records


def _private_review_html(cases: list[dict], *, snapshot: str) -> bytes:
    """Completely static, escaped, no network, scripts, forms or unsafe URLs."""
    blocks = []
    for case in cases:
        raw = " ".join(x or "" for x in case["original_english_fragments"])
        guarded = " ".join(x or "" for x in case["guarded_english_fragments"])
        derived = " ".join(x or "" for x in case["v2_proposed_english_fragments"])
        details = "".join(
            "<li>" +
            html.escape(str(row["ordinal"]), quote=True) + ": " +
            html.escape(row["english_role_class"], quote=True) +
            " (" + html.escape(row["rule_code"] or "NO_BOUNDED_RULE",
                              quote=True) + ") — " +
            html.escape(row["observed_verb_gloss"], quote=True) + " / " +
            html.escape(row["observed_adjacent_noun_phrase"], quote=True) +
            "</li>"
            for row in case["candidates"]
        )
        if not details:
            details = "<li>Historical English ambiguity; no parsed noun pair.</li>"
        blocks.append(
            "<details><summary>" +
            html.escape(case["reference"], quote=True) +
            " — " + html.escape(case["case_status"], quote=True) +
            "</summary><h3>Original CHES-derived English</h3><pre>" +
            html.escape(raw, quote=True) +
            "</pre><h3>Guarded English (new reader before move)</h3><pre>" +
            html.escape(guarded, quote=True) +
            "</pre><h3>Existing v2 English proposal (NOT approved by 029)</h3><pre>" +
            html.escape(derived, quote=True) +
            "</pre><h3>English role candidates</h3><ol>" +
            details +
            "</ol><p>Grammar not independently certified. No editing; "
            "no Hebrew crosscheck. Publication BLOCKED.</p></details>"
        )
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        '<title>DANMEK-029 private English clause-role review</title>'
        '<style>body{font:16px/1.5 Georgia,serif;max-width:960px;'
        'margin:2rem auto;padding:0 1rem;background:#faf9f7;color:#222}'
        'summary{cursor:pointer;font-weight:700}details{border:1px solid #bbb;'
        'border-radius:.4rem;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;'
        'overflow-wrap:anywhere;background:#ecebe6;padding:.75rem}'
        'h3{font:600 14px system-ui}li{margin:.2rem 0}</style>'
        '</head><body><h1>Private English clause-role review (DANMEK-029)</h1>'
        '<p>Snapshot: ' + html.escape(snapshot, quote=True) +
        '. CHES accepted as working authority. English grammatical roles '
        'are candidates, NOT proven subjects or objects. Historical 311 '
        'regex ambiguities are English review cases, not proven errors. '
        'No source changes or published Bible.</p>' +
        "".join(blocks) + "</body></html>\n"
    )
    return page.encode("utf-8")


def review_private_english_clauses(
    private_root: Path, *, require_311: bool = False,
    write_private_report: bool = False,
) -> dict:
    """Corpus scan, metadata-only by default; optional private review queue.

    Scans source English directly, then compares against the safely guarded
    v2 presentation in memory. Neither the CHES JSON nor locked derived
    HTML is edited. 311-case baseline is a regex signal, not proof of error.
    """
    if type(require_311) is not bool or type(write_private_report) is not bool:
        raise DanMek029Error("INVALID_CLAUSE_REVIEW_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        old_reader = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        case_rows: list[dict] = []
        by_role: Counter[str] = Counter()
        by_rule: Counter[str] = Counter()
        chapters = verses = pairs = ambiguous = skipped_legacy = 0
        changed_in_v2 = 0
        object_risk_verses = 0
        digest = hashlib.sha256(
            (REVISION + ":" + old_reader["snapshot_id"]).encode("ascii")
        )
        for item in sorted(folder.iterdir(), key=lambda p: p.name):
            if item.is_symlink() or not item.is_file():
                raise DanMek029Error("PRIVATE_CHES_ENTRY_UNSAFE")
            match = CHES_FILE_NAME.fullmatch(item.name)
            if match is None:
                raise DanMek029Error("PRIVATE_CHES_ENTRY_NAME_INVALID")
            prefix, chapter_str = match.groups()
            source, source_sha = _load_private_source(
                folder, prefix=prefix, chapter=int(chapter_str),
            )
            chapters += 1
            if chapters > MAX_CHAPTERS:
                raise DanMek029Error("PRIVATE_CLAUSE_REVIEW_TOO_MANY_CHAPTERS")
            digest.update((item.name + ":" + source_sha + "\n").encode("ascii"))
            for verse in source["verses"]:
                verses += 1
                original = [
                    span["original_ches_line_text"]
                    for span in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                observed_pairs = classify_english_clause_pairs(original)
                guarded, old_reason, withheld = _legacy_candidate_guard(
                    reference=verse["reference"], chapter_sha256=source_sha,
                    original=original,
                )
                ambiguous += int(old_reason == "AMBIGUOUS")
                skipped_legacy += int(withheld)
                guarded, _ = simplify_sur_faces_for_olt_view(guarded)
                guarded, _ = hide_isolated_c(guarded)
                revised, moves, _ = reorder_postverbal_subjects(guarded)
                changed_in_v2 += len(moves)

                if not observed_pairs and old_reason != "AMBIGUOUS" and not withheld:
                    continue
                if len(case_rows) >= MAX_PRIVATE_CASES:
                    raise DanMek029Error("PRIVATE_CLAUSE_REVIEW_CASE_LIMIT")
                pairs += len(observed_pairs)
                risky = any(
                    row["english_role_class"] == OBJECT_RISK
                    for row in observed_pairs
                )
                object_risk_verses += int(risky)
                for record in observed_pairs:
                    by_role[record["english_role_class"]] += 1
                    if record["rule_code"] is not None:
                        by_rule[record["rule_code"]] += 1
                case_rows.append({
                    "reference": verse["reference"],
                    "original_source_chapter_sha256": source_sha,
                    "old_reader_snapshot": old_reader["snapshot_id"],
                    "original_english_fragments": original,
                    "guarded_english_fragments": guarded,
                    "v2_proposed_english_fragments": revised,
                    "legacy_311_regex_ambiguity": old_reason == "AMBIGUOUS",
                    "legacy_unverified_reorder_withheld": withheld,
                    "v2_bounded_reorders_detected": len(moves),
                    "case_status": (
                        "OBJECT_OR_SUBJECT_REQUIRES_ENGLISH_CONTEXT"
                        if risky else
                        "UNRESOLVED_GRAMMAR_REVIEW"
                        if any(row["english_role_class"] == UNRESOLVED
                               for row in observed_pairs) or not observed_pairs else
                        "SUBJECT_PATTERN_CANDIDATE_NOT_CERTIFIED"
                    ),
                    "candidates": observed_pairs,
                    "proposed_corrections_approved_by_029": False,
                    "original_ches_modified": False,
                    "publication_status": "BLOCKED",
                })
        if verses != old_reader["observed_verse_count"]:
            raise DanMek029Error("ENGLISH_CLAUSE_VERSE_COUNT_CHANGED")
        if ambiguous != old_reader["olt_owner_candidate_ambiguous_verses_unchanged"]:
            raise DanMek029Error("ENGLISH_CLAUSE_LEGACY_AMBIGUITIES_CHANGED")
        if require_311 and ambiguous != 311:
            raise DanMek029Error("OWNER_EXPECTED_311_ENGLISH_AMBIGUITIES_NOT_FOUND")
        if old_reader != build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek029Error("PRIVATE_SOURCE_CHANGED_DURING_CLAUSE_REVIEW")

        output_status = "AUDIT_ONLY_NO_REPORT_WRITTEN"
        if write_private_report:
            document = {
                "schema": REVISION,
                "source_owner_reader_snapshot": old_reader["snapshot_id"],
                "english_only": True,
                "hebrew_aramaic_source_used": False,
                "english_role_proofs": 0,
                "chapters_scanned": chapters,
                "verses_scanned": verses,
                "legacy_regex_ambiguities_seen": ambiguous,
                "postverbal_candidates_seen": pairs,
                "publication_status": "BLOCKED",
                "cases": case_rows,
            }
            data = (
                json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            ).encode("utf-8")
            snapshot = "review-" + digest.hexdigest()[:24]
            html_data = _private_review_html(case_rows, snapshot=snapshot)
            root = folder.parent / "ches-clause-review"
            idpart = hashlib.sha256(data).hexdigest()[:20]
            saved_json = _private_write_once(
                root, "danmek-029-" + idpart + ".json", data,
            )
            saved_html = _private_write_once(
                root, "danmek-029-" + idpart + ".html", html_data,
            )
            output_status = (
                "NEW_PRIVATE_REPORT" if "NEW_PRIVATE_REPORT" in
                (saved_json, saved_html) else
                "EXISTING_IDENTICAL_PRIVATE_REPORT"
            )
        return {
            "checkpoint": REVISION,
            "mode": "PRIVATE_ENGLISH_CLAUSE_ROLE_AUDIT_NO_EDITS",
            "owner_reader_snapshot": old_reader["snapshot_id"],
            "source_chapters_scanned": chapters,
            "source_verses_scanned": verses,
            "historical_311_english_ambiguities_seen": ambiguous,
            "verses_with_review_cases": len(case_rows),
            "postverbal_noun_pairs_reviewed": pairs,
            "pair_classification_counts": dict(sorted(by_role.items())),
            "bounded_subject_pattern_counts": dict(sorted(by_rule.items())),
            "verses_with_object_risk": object_risk_verses,
            "legacy_unverified_moves_withheld": skipped_legacy,
            "v2_reorders_observed_in_memory": changed_in_v2,
            "grammar_cases_certified_correct": 0,
            "grammar_cases_owner_approved_by_this_tool": 0,
            "english_source_lexical_choices_changed": False,
            "previously_approved_reader_changed": False,
            "original_ches_source_changed": False,
            "hebrew_or_aramaic_translation_accuracy_checked": False,
            "private_source_text_logged": False,
            "private_output_state": output_status,
            "publication_status": "BLOCKED",
        }
    except DanMek029Error:
        raise
    except Exception:
        raise DanMek029Error("PRIVATE_ENGLISH_CLAUSE_REVIEW_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-029 offline English clause-role classification"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument(
        "--confirm-machine-readable-use-permission", action="store_true",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--write-private-report", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private CHES source-use permission required")
    try:
        report = review_private_english_clauses(
            args.private_root, require_311=args.require_311,
            write_private_report=args.write_private_report,
        )
    except DanMek029Error:
        parser.exit(2, "DANMEK_029_PRIVATE_CLAUSE_REVIEW_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
