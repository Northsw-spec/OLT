"""DANMEK-010: offline private CHES subject/verb proposal and review queue.

Heuristics suggest English presentation edits ONLY. They do not certify any
Hebrew subject, syntax or PDF-to-word correspondence, and NEVER auto-approve.
Private source words may appear in private review files but NEVER CLI output,
public tests, logs, repository files or Actions artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import stat
import tempfile

from scripts.ches_014_offline_english_bridge import (
    CHES014BridgeError, _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import NAME
from scripts.danmek_009_english_order import (
    SCHEMA as APPROVED_SCHEMA, DanMek009Error, apply_reviewed_order,
    load_private_order_rules,
)

REVISION = "DANMEK-010-PRIVATE-ORDER-REVIEW-v1"
CANDIDATE_SCHEMA = "DANMEK-010-private-candidates-v1"
MAX_SAVED = 2_000
ID = re.compile(r"review-[0-9a-f]{20}\Z")
REF = re.compile(r"[A-Za-z0-9_-]{1,20}\.[1-9][0-9]*\.[1-9][0-9]*\Z")
# Search English gloss typography conservatively. These patterns are
# deliberately NOT a grammatical or Hebrew morphology analyzer.
VERB = (r"(?:[Aa]nd[· ])?"
        r"(?:[Hh]e|[Ss]he|[Tt]hey|[Ww]e|[Tt]hou|[Yy]ou|[Yy]e)-"
        r"(?:(?:is|are|was|were|shall|will|have|had)-)?"
        r"[a-z]+(?:-[a-z]+){0,5}")
SUBJECT = r"[A-Z][A-Za-z'’-]{1,49}"
WHOLE_VERB = re.compile(VERB + r"\Z")
WHOLE_SUBJECT = re.compile(SUBJECT + r"\Z")
INLINE = re.compile(
    r"(?<![A-Za-z-])(?P<verb>" + VERB + r")[ \t]*"
    r"(?P<subject>" + SUBJECT + r")(?![A-Za-z-])"
)


class DanMek010Error(ValueError):
    """Never interpolate original text or local paths into an error."""


def _safe_dir(path: Path, *, create: bool = False) -> None:
    if path.is_symlink():
        raise DanMek010Error("PRIVATE_REVIEW_SYMLINK_REFUSED")
    if create and not path.exists():
        path.mkdir(mode=0o700)
    if (not path.is_dir() or stat.S_IMODE(path.stat().st_mode) & 0o077):
        raise DanMek010Error("PRIVATE_REVIEW_DIRECTORY_UNSAFE")


def _private_output_directory(folder: Path) -> Path:
    parent = folder.parent / "olt-english-order"
    _safe_dir(parent, create=True)
    return parent


def _write_once(path: Path, content: bytes) -> None:
    if path.is_symlink():
        raise DanMek010Error("PRIVATE_REVIEW_SYMLINK_REFUSED")
    if path.exists():
        if (not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077
                or path.read_bytes() != content):
            raise DanMek010Error("PRIVATE_REVIEW_OUTPUT_CONFLICT")
        return
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise DanMek010Error("PRIVATE_REVIEW_OUTPUT_CONFLICT") from exc
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _json_bytes(doc: dict) -> bytes:
    return (json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) +
            "\n").encode("utf-8")


def discover_candidates(
    reference: str, chapter_sha256: str, texts: list[str],
) -> tuple[list[dict], bool]:
    """Zero or ONE candidate per verse. Multiple possibilities are ambiguous."""
    found = []
    for index, text in enumerate(texts):
        if (index + 1 < len(texts) and WHOLE_VERB.fullmatch(text)
                and WHOLE_SUBJECT.fullmatch(texts[index + 1])):
            found.append({
                "reference": reference, "chapter_json_sha256": chapter_sha256,
                "mode": "adjacent", "source_syntax_reviewed": False,
                "review_note": "NOT_REVIEWED",
                "verb_fragment_index": index + 1,
                "subject_fragment_index": index + 2,
                "original_verb": text, "original_subject": texts[index + 1],
            })
        for match in INLINE.finditer(text):
            found.append({
                "reference": reference, "chapter_json_sha256": chapter_sha256,
                "mode": "inline", "source_syntax_reviewed": False,
                "review_note": "NOT_REVIEWED",
                "verb_fragment_index": index + 1,
                "original_fragment": text,
                "original_verb": match["verb"],
                "original_subject": match["subject"],
            })
    return (found if len(found) == 1 else []), len(found) > 1


def _html_review(rows: list[tuple[dict, list[str]]], summary: dict) -> bytes:
    snippets = []
    for candidate, fragments in rows:
        # Run the same existing rendering transform to preview, but not approve.
        try:
            suggestion, moved = apply_reviewed_order(
                reference=candidate["reference"],
                chapter_sha256=candidate["chapter_json_sha256"],
                original=fragments, visible=fragments,
                rules={candidate["reference"]: candidate},
            )
        except DanMek009Error as exc:
            raise DanMek010Error("PREVIEW_ORDER_CANDIDATE_INCONSISTENT") from exc
        if moved != 1:
            raise DanMek010Error("PREVIEW_ORDER_CANDIDATE_NOT_APPLIED")
        raw = " | ".join(fragments)
        proposed = " | ".join(suggestion)
        esc = lambda value: html.escape(value, quote=True)
        snippets.append(
            "<section><h2>" + esc(candidate["reference"]) +
            "</h2><p>Not reviewed. A suggestion, not an OLT translation.</p>"
            "<div><strong>Original CHES display</strong><pre>" + esc(raw) +
            "</pre></div><div><strong>Proposed OLT English display</strong><pre>" +
            esc(proposed) + "</pre></div></section>"
        )
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'" +
        '"><title>Private OLT candidate review</title>'
        '<style>body{font:17px/1.5 system-ui;max-width:900px;margin:2rem auto;'
        'padding:0 1rem;background:#faf9f7;color:#262626}'
        'section{border-top:1px solid #ccc;padding:1rem 0}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eee;'
        'padding:.8rem}p{max-width:850px}</style></head><body>'
        '<h1>Private, unreviewed OLT word-order candidates</h1>'
        '<p>Not verified Hebrew syntax. Do not approve without inspecting '
        'the original language and exact CHES source fragments. Nothing here '
        'is published or changed in the original JSON. English pronoun casing '
        'is not altered for divine referents.</p>'
        f'<p>Saved {summary["candidates_saved"]} of '
        f'{summary["eligible_single_candidate_verses"]} candidate verses. '
        'Other verses remain unchanged.</p>' + "".join(snippets) +
        '</body></html>\n'
    )
    return page.encode("utf-8")


def scan_private_order_candidates(
    private_root: Path, *, build_review: bool = False,
    prefix_filter: str | None = None, chapter_filter: int | None = None,
    max_saved: int = MAX_SAVED,
) -> dict:
    """Read authentic local JSON, write only a private immutable review queue."""
    if (type(build_review) is not bool or type(max_saved) is not int
            or not 1 <= max_saved <= MAX_SAVED
            or (prefix_filter is not None and not re.fullmatch(
                r"[A-Za-z0-9_-]{1,20}", prefix_filter))
            or (chapter_filter is not None and (
                type(chapter_filter) is not int or not 1 <= chapter_filter <= 250))
            or (chapter_filter is not None and prefix_filter is None)):
        raise DanMek010Error("INVALID_PRIVATE_SCAN_FILTERS")
    try:
        folder = _private_archive_root(private_root)
    except CHES014BridgeError as exc:
        raise DanMek010Error("PRIVATE_SOURCE_ROOT_UNSAFE") from exc
    digest = hashlib.sha256(REVISION.encode("ascii"))
    digest.update(f"max={max_saved};filter={prefix_filter};chapter={chapter_filter}".encode("ascii"))
    records = []
    chapters = verses = ambiguous = eligible = 0
    rows: list[tuple[dict, list[str]]] = []
    for file in sorted(folder.iterdir()):
        if file.is_symlink() or not file.is_file():
            raise DanMek010Error("UNEXPECTED_PRIVATE_SOURCE_ENTRY")
        match = NAME.fullmatch(file.name)
        if match is None:
            raise DanMek010Error("INVALID_PRIVATE_SOURCE_ENTRY_NAME")
        prefix, raw_chapter = match.groups()
        chapter = int(raw_chapter)
        if (prefix_filter is not None and prefix != prefix_filter or
                chapter_filter is not None and chapter != chapter_filter):
            continue
        try:
            source, source_sha = _load_private_source(
                folder, prefix=prefix, chapter=chapter,
            )
        except Exception as exc:
            raise DanMek010Error("PRIVATE_SOURCE_VALIDATION_FAILED") from exc
        records.append((prefix, chapter))
        digest.update(f"{prefix}.{chapter}:{source_sha}\n".encode("ascii"))
        chapters += 1
        for verse in source["verses"]:
            verses += 1
            fragments = [
                span["original_ches_line_text"]
                for span in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
            ]
            proposals, multiple = discover_candidates(
                verse["reference"], source_sha, fragments,
            )
            if multiple:
                ambiguous += 1
            if proposals:
                eligible += 1
                if len(rows) < max_saved:
                    rows.append((proposals[0], fragments))
    if not chapters:
        raise DanMek010Error("PRIVATE_SOURCE_FILTER_HAS_NO_CHAPTERS")
    snapshot = "review-" + digest.hexdigest()[:20]
    report = {
        "checkpoint": "DANMEK-010",
        "review_id": snapshot,
        "chapters_scanned": chapters,
        "verses_scanned": verses,
        "eligible_single_candidate_verses": eligible,
        "ambiguous_candidate_verses_left_unchanged": ambiguous,
        "candidates_saved": len(rows),
        "candidate_queue_truncated": eligible > len(rows),
        "source_syntax_independently_verified": False,
        "candidates_automatically_approved": 0,
        "original_private_ches_source_modified": False,
        "private_review_files_written_or_verified": 2 if build_review else 0,
        "publication_status": "BLOCKED",
    }
    if build_review:
        output = _private_output_directory(folder) / snapshot
        _safe_dir(output, create=True)
        doc = {
            "schema": CANDIDATE_SCHEMA,
            "revision": REVISION,
            "candidates": [candidate for candidate, _ in rows],
        }
        _write_once(output / "candidates.json", _json_bytes(doc))
        _write_once(output / "review.html", _html_review(rows, report))
    return report


def approve_private_candidate(
    private_root: Path, *, review_id: str, reference: str,
    review_note: str, original_language_review_attested: bool = False,
) -> dict:
    """Explicit human attestation; never infer syntax or approve from regex."""
    if (type(review_id) is not str or not ID.fullmatch(review_id)
            or type(reference) is not str or not REF.fullmatch(reference)
            or type(review_note) is not str or not 15 <= len(review_note) <= 2_000
            or not review_note.strip()
            or original_language_review_attested is not True):
        raise DanMek010Error("EXPLICIT_ORIGINAL_LANGUAGE_REVIEW_REQUIRED")
    try:
        folder = _private_archive_root(private_root)
    except CHES014BridgeError as exc:
        raise DanMek010Error("PRIVATE_SOURCE_ROOT_UNSAFE") from exc
    parent = folder.parent / "olt-english-order"
    _safe_dir(parent)
    review_dir = parent / review_id
    _safe_dir(review_dir)
    source = review_dir / "candidates.json"
    if (source.is_symlink() or not source.is_file()
            or stat.S_IMODE(source.stat().st_mode) & 0o077
            or not 0 < source.stat().st_size <= 15_000_000):
        raise DanMek010Error("PRIVATE_REVIEW_CANDIDATE_FILE_UNSAFE")
    try:
        doc = json.loads(source.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise DanMek010Error("INVALID_PRIVATE_REVIEW_CANDIDATES") from exc
    if (type(doc) is not dict or set(doc) != {"schema", "revision", "candidates"}
            or doc["schema"] != CANDIDATE_SCHEMA or doc["revision"] != REVISION
            or type(doc["candidates"]) is not list
            or len(doc["candidates"]) > MAX_SAVED):
        raise DanMek010Error("PRIVATE_REVIEW_CANDIDATE_SCHEMA_MISMATCH")
    matches = [
        candidate for candidate in doc["candidates"]
        if type(candidate) is dict and candidate.get("reference") == reference
    ]
    if len(matches) != 1:
        raise DanMek010Error("PRIVATE_REVIEW_REFERENCE_NOT_UNIQUE")
    candidate = matches[0]
    if (candidate.get("source_syntax_reviewed") is not False or
            candidate.get("review_note") != "NOT_REVIEWED"):
        raise DanMek010Error("PRIVATE_CANDIDATE_PREAPPROVED_OR_INVALID")
    parts = reference.split(".")
    prefix, chapter = parts[0], int(parts[1])
    try:
        chapter_doc, current_sha = _load_private_source(
            folder, prefix=prefix, chapter=chapter,
        )
    except Exception as exc:
        raise DanMek010Error("PRIVATE_APPROVAL_SOURCE_VALIDATION_FAILED") from exc
    if current_sha != candidate["chapter_json_sha256"]:
        raise DanMek010Error("PRIVATE_CANDIDATE_STALE_SOURCE_SHA")
    rows = [v for v in chapter_doc["verses"] if v["reference"] == reference]
    if len(rows) != 1:
        raise DanMek010Error("PRIVATE_CANDIDATE_ORIGINAL_VERSE_MISSING")
    fragments = [
        span["original_ches_line_text"]
        for span in rows[0]["source_ches_spans_NOT_OLT_TRANSLATION"]
    ]
    expected, ambiguous = discover_candidates(reference, current_sha, fragments)
    if ambiguous or expected != [candidate]:
        raise DanMek010Error("PRIVATE_CANDIDATE_CHANGED_OR_AMBIGUOUS")
    try:
        _, applied = apply_reviewed_order(
            reference=reference, chapter_sha256=current_sha,
            original=fragments, visible=fragments,
            rules={reference: candidate},
        )
    except DanMek009Error as exc:
        raise DanMek010Error("PRIVATE_CANDIDATE_ORDER_ANCHOR_INVALID") from exc
    if applied != 1:
        raise DanMek010Error("PRIVATE_CANDIDATE_ORDER_NOT_APPLIED")
    approved_path = parent / "approved.json"
    before = b""
    if approved_path.exists() or approved_path.is_symlink():
        try:
            existing, _ = load_private_order_rules(folder)
        except DanMek009Error as exc:
            raise DanMek010Error("EXISTING_APPROVED_RULES_INVALID") from exc
        before = approved_path.read_bytes()
    else:
        existing = {}
    if reference in existing or len(existing) >= 20_000:
        raise DanMek010Error("PRIVATE_REVIEW_ALREADY_APPROVED_OR_FULL")
    approved = dict(candidate)
    approved["source_syntax_reviewed"] = True
    approved["review_note"] = review_note
    existing[reference] = approved
    content = _json_bytes({
        "schema": APPROVED_SCHEMA,
        "rules": [existing[key] for key in sorted(existing)],
    })
    if len(content) > 4_000_000:
        raise DanMek010Error("PRIVATE_APPROVED_RULE_FILE_TOO_LARGE")
    # Preserve immutable prior approval bytes before any replacement.
    if before:
        backup = parent / (
            "approved-backup-" + hashlib.sha256(before).hexdigest()[:20] + ".json"
        )
        _write_once(backup, before)
        if approved_path.read_bytes() != before:
            raise DanMek010Error("PRIVATE_APPROVED_RULE_FILE_CHANGED")
    fd, temporary = tempfile.mkstemp(
        prefix=".approved-", suffix=".tmp", dir=parent,
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        if approved_path.is_symlink() or (
            before and approved_path.read_bytes() != before
        ) or (not before and approved_path.exists()):
            raise DanMek010Error("PRIVATE_APPROVAL_CONCURRENT_MODIFICATION")
        os.replace(temporary, approved_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {
        "checkpoint": "DANMEK-010",
        "status": "PRIVATE_REVIEW_ATTESTATION_RECORDED",
        "approved_rule_count": len(existing),
        "source_syntax_independently_machine_verified": False,
        "operator_attested_original_language_review": True,
        "original_private_ches_source_modified": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline private subject/verb proposals, not automatic translation"
    )
    parser.add_argument("--private-root", type=Path,
                        default=Path.home() / ".olt-private" / "ches")
    parser.add_argument("--confirm-machine-readable-use-permission",
                        action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--build-review", action="store_true")
    mode.add_argument("--approve-reference", type=str)
    parser.add_argument("--book-prefix", type=str)
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--max-candidates", type=int, default=MAX_SAVED)
    parser.add_argument("--review-id", type=str)
    parser.add_argument("--review-note", type=str)
    parser.add_argument("--attest-original-language-syntax-reviewed",
                        action="store_true")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Private machine-readable CHES use permission must be confirmed")
    try:
        if args.approve_reference is not None:
            if (not args.review_id or not args.review_note
                    or args.book_prefix is not None or args.chapter is not None):
                raise DanMek010Error("INVALID_PRIVATE_APPROVAL_ARGUMENTS")
            result = approve_private_candidate(
                args.private_root, review_id=args.review_id,
                reference=args.approve_reference, review_note=args.review_note,
                original_language_review_attested=(
                    args.attest_original_language_syntax_reviewed),
            )
        else:
            if (args.review_id or args.review_note
                    or args.attest_original_language_syntax_reviewed):
                raise DanMek010Error("INVALID_PRIVATE_SCAN_ARGUMENTS")
            result = scan_private_order_candidates(
                args.private_root, build_review=args.build_review,
                prefix_filter=args.book_prefix, chapter_filter=args.chapter,
                max_saved=args.max_candidates,
            )
    except Exception:
        parser.exit(2, "DANMEK_010_PRIVATE_ORDER_REVIEW_FAILED\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
