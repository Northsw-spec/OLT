"""DANMEK-025: private English-only grammar candidate review.

CHES is the owner's accepted English authority. This module never loads,
compares, or analyzes separately imported Hebrew/Aramaic sources. It never
writes CHES source or the owner-accepted DANMEK-013/014 reading.

Rule matching is intentionally narrow: a detected English pronoun + finite
BE disagreement creates an UNAPPROVED candidate, not proof of a defective
verse. All unusual but unflagged syntax is unchanged; silence is not a
grammar certificate. The historic 311 regex ambiguities are considered
English review cases, never Hebrew translation errors.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
import os
from pathlib import Path
import re
import stat
import tempfile

from scripts.ches_014_offline_english_bridge import _load_private_source, _private_archive_root
from scripts.ches_015_direct_private_reader import NAME, build_private_reader
from scripts.danmek_008_english_display import simplify_sur_faces_for_olt_view
from scripts.danmek_011_owner_order import apply_owner_approved_candidates
from scripts.danmek_012_display import hide_isolated_c

REVISION = "DANMEK-025-ENGLISH-ONLY-GRAMMAR-TRIAGE-v1"
MAX_CASES = 30000
MAX_VERSE_CHARS = 50000

# Deliberately tiny, review-only English grammar heuristic. Do not expand
# to word-order smoothing, free paraphrase or automatically applied corrections.
_AGREEMENT = re.compile(
    r"(?<![A-Za-z])(?P<subject>I|he|she|we|they|you|thou)"
    r"(?P<gap>\s+(?:—\s*)?)(?P<verb>is|are|am)(?![A-Za-z])",
    re.IGNORECASE,
)
_REPLACEMENTS = {
    "i": {"is": "am", "are": "am"},
    "he": {"are": "is", "am": "is"},
    "she": {"are": "is", "am": "is"},
    "we": {"is": "are", "am": "are"},
    "they": {"is": "are", "am": "are"},
    "you": {"is": "are", "am": "are"},
    "thou": {"is": "art", "are": "art", "am": "art"},
}


class DanMek025Error(ValueError):
    """Sanitized, fixed-code private grammar review error."""


def inspect_english_fragments(fragments: list[str | None]) -> tuple[list[str | None], list[dict]]:
    """Propose token-local replacements; never make or authorize a reader edit.

    Keeps the exact fragment structure, punctuation and order. Only the
    verb-token span may change in a proposal, and only after a directly
    adjacent subject pronoun. This rule is not a general English parser.
    """
    if (type(fragments) is not list or not fragments or len(fragments) > 10000
            or any(t is not None and type(t) is not str for t in fragments)):
        raise DanMek025Error("INVALID_ENGLISH_FRAGMENT_SEQUENCE")
    chunks = [t if t is not None else "" for t in fragments]
    flat = " ".join(chunks)
    if len(flat) > MAX_VERSE_CHARS:
        raise DanMek025Error("ENGLISH_VERSE_EXCEEDS_REVIEW_LIMIT")
    intervals = []
    offset = 0
    for piece in chunks:
        intervals.append((offset, offset + len(piece)))
        offset += len(piece) + 1
    changes: dict[int, list[tuple[int, int, str]]] = {}
    evidence = []
    for match in _AGREEMENT.finditer(flat):
        replacement = _REPLACEMENTS[match.group("subject").lower()].get(
            match.group("verb").lower()
        )
        if replacement is None:
            continue
        # Alter the actual finite verb, not its subject, neighbouring tokens
        # or its order. The match may bridge adjacent CHES text fragments.
        verb_start, verb_end = match.span("verb")
        targets = [
            (i, start) for i, (start, end) in enumerate(intervals)
            if start <= verb_start and verb_end <= end
        ]
        if len(targets) != 1:
            raise DanMek025Error("ENGLISH_GRAMMAR_FRAGMENT_OFFSET_INVALID")
        i, start = targets[0]
        original_verb = match.group("verb")
        if original_verb.isupper():
            replacement = replacement.upper()
        elif original_verb[0].isupper():
            replacement = replacement.capitalize()
        changes.setdefault(i, []).append(
            (verb_start - start, verb_end - start, replacement)
        )
        evidence.append({
            "reason_code": "ENGLISH_FINITE_BE_PRONOUN_AGREEMENT_CANDIDATE",
            "observed_subject": match.group("subject"),
            "observed_verb": original_verb,
            "proposed_verb": replacement,
            "editorial_status": "PROPOSED_UNVERIFIED_NEEDS_OWNER_REVIEW",
            "reorder_proposed": False,
            "hebrew_crosscheck_performed": False,
        })
    proposed = list(fragments)
    for index, edits in changes.items():
        value = chunks[index]
        for start, end, replacement in sorted(edits, reverse=True):
            value = value[:start] + replacement + value[end:]
        proposed[index] = value
    return proposed, evidence


def _private_write_once(folder: Path, name: str, data: bytes) -> str:
    """Exclusive, immutable 0600 report; never replace owner-modified work."""
    if folder.is_symlink():
        raise DanMek025Error("PRIVATE_GRAMMAR_DIRECTORY_SYMLINK")
    if folder.exists():
        if not folder.is_dir() or stat.S_IMODE(folder.stat().st_mode) & 0o077:
            raise DanMek025Error("PRIVATE_GRAMMAR_DIRECTORY_UNSAFE")
    else:
        folder.mkdir(mode=0o700)
    destination = folder / name
    if destination.is_symlink():
        raise DanMek025Error("PRIVATE_GRAMMAR_REPORT_SYMLINK")
    if destination.exists():
        if (not destination.is_file()
                or stat.S_IMODE(destination.stat().st_mode) & 0o077
                or destination.read_bytes() != data):
            raise DanMek025Error("PRIVATE_GRAMMAR_REPORT_NO_OVERWRITE")
        return "EXISTING_IDENTICAL_PRIVATE_REPORT"
    fd, temporary = tempfile.mkstemp(prefix=".danmek025-", dir=folder)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, destination, follow_symlinks=False)
        except FileExistsError as exc:
            raise DanMek025Error("PRIVATE_GRAMMAR_REPORT_RACE_NO_OVERWRITE") from exc
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return "NEW_PRIVATE_REPORT"


def _private_html(records: list[dict], *, snapshot: str) -> bytes:
    """Read-only offline side-by-side review, fully escaped, no remote assets."""
    blocks = []
    for item in records:
        before = " ".join(x or "" for x in item["before_fragments"])
        after = " ".join(x or "" for x in item["proposed_fragments"])
        blocks.append(
            "<section><h2>" + html.escape(item["reference"], quote=True) +
            " — " + html.escape(item["status"], quote=True) + "</h2>" +
            "<h3>Current English</h3><p class='english'>" +
            html.escape(before, quote=True) + "</p>" +
            "<h3>Unapproved candidate (identical if NO_CHANGE)</h3>" +
            "<p class='english'>" + html.escape(after, quote=True) + "</p>" +
            "<p>Candidate reason: " +
            html.escape(", ".join(x["reason_code"] for x in item["evidence"])
                        or "NO_DEMONSTRATED_GRAMMAR_ERROR", quote=True) +
            ". No automatic correction. No Hebrew revalidation.</p></section>"
        )
    page = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta name='robots' content='noindex,nofollow,noarchive'>"
        "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; "
        "style-src 'unsafe-inline'; img-src 'none'; object-src 'none'; "
        "base-uri 'none'; form-action 'none'\">"
        "<title>DANMEK-025 — private English grammar candidates</title>"
        "<style>body{font:16px/1.6 Georgia,serif;max-width:980px;margin:auto;"
        "padding:1.5rem;background:#faf9f7;color:#202020}"
        "section{border-top:1px solid #bbb;padding:.6rem 0 1rem}"
        ".english{white-space:pre-wrap;overflow-wrap:anywhere;padding:.5rem;"
        "background:#f0eee8}h2,h3{font-family:system-ui,sans-serif}"
        "h2{font-size:18px}h3{font-size:14px}</style></head><body>"
        "<h1>DANMEK-025 — private English grammar review</h1>"
        "<p>Owner-approved reader is unchanged. CHES is the accepted English "
        "source; the review does not compare Hebrew. Unusual Hebraic word "
        "order is intentional. Every proposed edit remains UNVERIFIED and "
        "requires separate owner approval. Unflagged sentences are NOT "
        "automatically certified correct. Publication BLOCKED.</p>"
        "<p>Reader snapshot: " + html.escape(snapshot, quote=True) +
        ". Review cases: " + str(len(records)) + ".</p>" +
        "".join(blocks) + "</body></html>\n"
    )
    return page.encode("utf-8")


def review_private_english_grammar(
    private_root: Path, *, require_311: bool = False,
    write_private_report: bool = False,
) -> dict:
    """Inspect current derived English only; metadata-only by default.

    Preserves every source chapter, the current owner-approved HTML and all
    historic 311-case queues. Private JSON/HTML contain proposals only when
    explicitly requested. Never accesses original-language word records.
    """
    if type(require_311) is not bool or type(write_private_report) is not bool:
        raise DanMek025Error("INVALID_ENGLISH_GRAMMAR_REVIEW_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        baseline = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        cases = []
        total_verses = total_ambiguous = total_candidates = 0
        count_by_reason: Counter[str] = Counter()
        for file in sorted(folder.iterdir(), key=lambda p: p.name):
            match = NAME.fullmatch(file.name)
            if not match or file.is_symlink() or not file.is_file():
                raise DanMek025Error("UNEXPECTED_PRIVATE_CHES_SOURCE_FILE")
            prefix, number = match.groups()
            source, source_sha = _load_private_source(
                folder, prefix=prefix, chapter=int(number),
            )
            for row in source["verses"]:
                total_verses += 1
                original = [
                    span["original_ches_line_text"]
                    for span in row["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                visible, order_reason = apply_owner_approved_candidates(
                    reference=row["reference"], chapter_sha256=source_sha,
                    original=original, visible=list(original),
                )
                visible, _ = simplify_sur_faces_for_olt_view(visible)
                visible, _ = hide_isolated_c(visible)
                proposal, evidence = inspect_english_fragments(visible)
                ambiguous = order_reason == "AMBIGUOUS"
                total_ambiguous += int(ambiguous)
                total_candidates += len(evidence)
                for item in evidence:
                    count_by_reason[item["reason_code"]] += 1
                if not (ambiguous or evidence):
                    continue
                if len(cases) >= MAX_CASES:
                    raise DanMek025Error("ENGLISH_GRAMMAR_REVIEW_CASE_LIMIT")
                cases.append({
                    "reference": row["reference"],
                    "source_chapter_sha256": source_sha,
                    "locked_reader_snapshot": baseline["snapshot_id"],
                    "historic_english_ambiguity": ambiguous,
                    "status": ("PROPOSED_GRAMMAR_CORRECTION_UNVERIFIED"
                               if evidence else "GRAMMAR_UNRESOLVED_NO_REORDER"),
                    "before_fragments": visible,
                    "proposed_fragments": proposal,
                    "evidence": evidence,
                    "changes_applied_to_reader": False,
                    "owner_approved": False,
                    "publication_status": "BLOCKED",
                })
        if total_verses != baseline["observed_verse_count"]:
            raise DanMek025Error("ENGLISH_GRAMMAR_VERSE_COUNT_CHANGED")
        if total_ambiguous != baseline["olt_owner_candidate_ambiguous_verses_unchanged"]:
            raise DanMek025Error("ENGLISH_GRAMMAR_AMBIGUITY_COUNT_CHANGED")
        if require_311 and total_ambiguous != 311:
            raise DanMek025Error("ENGLISH_GRAMMAR_EXPECTED_311_MISMATCH")
        if baseline != build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek025Error("PRIVATE_CHES_SOURCE_CHANGED_DURING_GRAMMAR_REVIEW")

        output_state = "AUDIT_ONLY_NO_PRIVATE_REPORT_WRITTEN"
        if write_private_report:
            payload = {
                "checkpoint": REVISION,
                "baseline_reader_snapshot_id": baseline["snapshot_id"],
                "scope": "PRIVATE_ENGLISH_GRAMMAR_ONLY",
                "ches_accepted_as_working_authority": True,
                "hebrew_or_aramaic_accuracy_comparison_performed": False,
                "total_verses_examined": total_verses,
                "historic_ambiguities_examined": total_ambiguous,
                "english_rule_candidates_unverified": total_candidates,
                "no_automatic_corrections": True,
                "grammar_certification_of_complete_corpus": False,
                "publication_status": "BLOCKED",
                "cases": cases,
            }
            raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
                   + "\n").encode("utf-8")
            private_html = _private_html(cases, snapshot=baseline["snapshot_id"])
            target = folder.parent / "ches-grammar-review"
            digest = hashlib.sha256(raw).hexdigest()[:20]
            json_state = _private_write_once(
                target, "danmek-025-english-review-" + digest + ".json", raw,
            )
            html_state = _private_write_once(
                target, "danmek-025-english-review-" + digest + ".html",
                private_html,
            )
            output_state = (
                "NEW_PRIVATE_REPORT" if "NEW_PRIVATE_REPORT" in
                (json_state, html_state) else "EXISTING_IDENTICAL_PRIVATE_REPORT"
            )
        return {
            "checkpoint": REVISION,
            "mode": "ENGLISH_ONLY_PRIVATE_GRAMMAR_REVIEW_NO_READER_EDITS",
            "reader_snapshot_id": baseline["snapshot_id"],
            "verses_scanned": total_verses,
            "historic_311_regex_ambiguities_seen": total_ambiguous,
            "ambiguities_without_bounded_grammar_candidate": sum(
                1 for row in cases
                if row["historic_english_ambiguity"] and not row["evidence"]
            ),
            "english_grammar_candidates_unverified": total_candidates,
            "review_case_records": len(cases),
            "candidate_reason_counts": dict(sorted(count_by_reason.items())),
            "unflagged_verses_grammar_certified": False,
            "ches_vs_hebrew_revalidation_performed": False,
            "original_ches_source_modified": False,
            "owner_verified_english_reader_modified": False,
            "automatically_applied_edits": 0,
            "private_text_printed": False,
            "private_output_status": output_state,
            "publication_status": "BLOCKED",
        }
    except DanMek025Error:
        raise
    except Exception:
        raise DanMek025Error("PRIVATE_ENGLISH_GRAMMAR_REVIEW_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-025 local English-only grammar proposal review"
    )
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument("--confirm-machine-readable-use-permission",
                        action="store_true")
    parser.add_argument("--require-311", action="store_true")
    parser.add_argument("--write-private-report", action="store_true",
                        help="Opt in to immutable private JSON and offline HTML proposals")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private source use authorization required")
    try:
        outcome = review_private_english_grammar(
            args.private_root, require_311=args.require_311,
            write_private_report=args.write_private_report,
        )
    except DanMek025Error:
        parser.exit(2, "DANMEK_025_PRIVATE_ENGLISH_GRAMMAR_REVIEW_FAILED\n")
    print(json.dumps(outcome, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
