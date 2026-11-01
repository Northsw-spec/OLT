"""DANMEK-030: English-only, explicitly reviewed private subject-order exceptions.

CHES vocabulary is accepted by the owner; no Hebrew/Aramaic verification.
DANMEK-029 candidates do not establish grammatical roles and never authorize
automatic edits. A private, explicit reviewer attestation may permit an
EXACT pinned English-only word-order move in a *new* versioned reader.
The original CHES, DANMEK-013/014, and DANMEK-028 remain immutable.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import stat

from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.ches_015_direct_private_reader import (
    NAME as CHES_FILE_NAME, build_private_reader,
)
from scripts.danmek_027_multiclause_subject_first import (
    _legacy_candidate_guard, reorder_postverbal_subjects,
    _format_subject_before_verb, _safe_dir, _write_once, DanMek027Error,
)
from scripts.danmek_008_english_display import simplify_sur_faces_for_olt_view
from scripts.danmek_012_display import hide_isolated_c
from scripts.danmek_029_private_english_clause_review import (
    classify_english_clause_pairs, PATTERN_SUBJECT, OBJECT_RISK, UNRESOLVED,
)
from scripts.danmek_025_private_english_grammar import _private_write_once

REVISION = "DANMEK-030-REVIEWED-ENGLISH-SUBJECT-ORDER-v1"
SCHEMA = "DANMEK-030-private-subject-role-attestations-v1"
MAX_CHAPTERS = 1100
MAX_RULES = 100000
MAX_MANIFEST_BYTES = 40_000_000
MAX_REVIEW_HTML_BYTES = 60_000_000
REF = re.compile(r"[A-Za-z0-9_-]{1,20}\.[1-9][0-9]*\.[1-9][0-9]*\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
ALLOWED_CANDIDATE_CLASSES = frozenset({OBJECT_RISK, UNRESOLVED})
RULE_KEYS = frozenset({
    "reference", "source_chapter_sha256", "expected_verse_english_sha256",
    "candidate_ordinal", "observed_verb_gloss", "observed_adjacent_noun_phrase",
    "english_role_class", "english_subject_role_reviewed", "review_note",
})


class DanMek030Error(ValueError):
    """A fixed error code; never quote private source words or paths."""


def _verse_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_source_text(
    original: list[str], *, reference: str, chapter_sha256: str,
) -> tuple[str, str]:
    guarded, old_reason, _ = _legacy_candidate_guard(
        reference=reference, chapter_sha256=chapter_sha256,
        original=original,
    )
    guarded, _ = simplify_sur_faces_for_olt_view(guarded)
    guarded, _ = hide_isolated_c(guarded)
    displayed, _, _ = reorder_postverbal_subjects(guarded)
    return " ".join(span or "" for span in displayed), old_reason


def _candidate_rules(
    *, reference: str, chapter_sha256: str, verse: str,
) -> list[dict]:
    result = []
    for candidate in classify_english_clause_pairs([verse]):
        if candidate["english_role_class"] == PATTERN_SUBJECT:
            # These patterns are already controlled by 028. An extra manual
            # exception is neither warranted nor automatically authorized.
            continue
        if candidate["english_role_class"] not in ALLOWED_CANDIDATE_CLASSES:
            raise DanMek030Error("UNKNOWN_CLAUSE_REVIEW_CLASS")
        result.append({
            "reference": reference,
            "source_chapter_sha256": chapter_sha256,
            "expected_verse_english_sha256": _verse_hash(verse),
            "candidate_ordinal": candidate["ordinal"],
            "observed_verb_gloss": candidate["observed_verb_gloss"],
            "observed_adjacent_noun_phrase":
                candidate["observed_adjacent_noun_phrase"],
            "english_role_class": candidate["english_role_class"],
            "english_subject_role_reviewed": False,
            "review_note": "",
        })
    return result


def apply_reviewed_english_subjects(
    text: str, *, reference: str, chapter_sha256: str, rules: list[dict],
) -> tuple[str, int]:
    """Review attestation + exact source/snapshot/candidate match required.

    Multiple distinct subject moves per verse supported; nonadjacent words,
    unreviewed proposals, and ambiguous/changed source are never modified.
    """
    if (type(text) is not str or type(reference) is not str
            or type(chapter_sha256) is not str or not SHA.fullmatch(chapter_sha256)
            or not REF.fullmatch(reference) or type(rules) is not list
            or len(rules) > MAX_RULES):
        raise DanMek030Error("INVALID_REVIEWED_ENGLISH_ORDER_INPUT")
    candidates = {
        row["ordinal"]: row
        for row in classify_english_clause_pairs([text])
    }
    seen: set[int] = set()
    edits: list[tuple[int, int, str]] = []
    for rule in rules:
        if type(rule) is not dict or set(rule) != RULE_KEYS:
            raise DanMek030Error("INVALID_ENGLISH_REVIEW_RULE_FIELDS")
        ordinal = rule["candidate_ordinal"]
        if type(ordinal) is not int or ordinal in seen or ordinal < 1:
            raise DanMek030Error("DUPLICATE_OR_INVALID_ENGLISH_CANDIDATE")
        seen.add(ordinal)
        note = rule["review_note"]
        approved = rule["english_subject_role_reviewed"]
        if (type(approved) is not bool or type(note) is not str
                or len(note) > 2000
                or (approved and len(note.strip()) < 24)
                or (not approved and note != "")):
            raise DanMek030Error("ENGLISH_SUBJECT_ATTESTATION_MISSING_OR_INVALID")
        if (rule["reference"] != reference
                or rule["source_chapter_sha256"] != chapter_sha256
                or rule["expected_verse_english_sha256"] != _verse_hash(text)
                or rule["english_role_class"] not in ALLOWED_CANDIDATE_CLASSES):
            raise DanMek030Error("STALE_OR_FORGED_ENGLISH_REVIEW_CONTEXT")
        c = candidates.get(ordinal)
        if (c is None or c["english_role_class"] != rule["english_role_class"]
                or c["observed_verb_gloss"] != rule["observed_verb_gloss"]
                or c["observed_adjacent_noun_phrase"] !=
                    rule["observed_adjacent_noun_phrase"]):
            raise DanMek030Error("REVIEWED_ENGLISH_CLAUSE_PAIR_MISMATCH")
        if not approved:
            continue
        left, right = (
            c["source_english_position_start"],
            c["source_english_position_end"],
        )
        verb = c["observed_verb_gloss"]
        subject = c["observed_adjacent_noun_phrase"]
        # Do not accept fuzzy substring matches, or a shifted candidate.
        matched = re.fullmatch(
            re.escape(verb) + r"[ \t]+" + re.escape(subject),
            text[left:right],
        )
        if matched is None:
            raise DanMek030Error("REVIEWED_ENGLISH_CLAUSE_CONTEXT_CHANGED")
        edits.append((left, right, _format_subject_before_verb(verb, subject)))

    ordered_edits = sorted(edits)
    for i, (left, right, _) in enumerate(ordered_edits):
        if i and left < ordered_edits[i - 1][1]:
            raise DanMek030Error("REVIEWED_ENGLISH_CLAUSE_EDIT_OVERLAP")
    updated = text
    for left, right, new in reversed(ordered_edits):
        updated = updated[:left] + new + updated[right:]
    return updated, len(edits)


def _unique_json(pairs: list[tuple[str, object]]) -> dict:
    data = {}
    for key, value in pairs:
        if key in data:
            raise DanMek030Error("DUPLICATE_PRIVATE_ATTESTATION_JSON_KEY")
        data[key] = value
    return data


def _approved_manifest(folder: Path, *, expected_snapshot: str) -> tuple[dict, bytes]:
    """Only fixed private path, only 0700 parent/0600 JSON, no symlinks."""
    root = folder.parent / "ches-subject-review"
    target = root / "approved.json"
    if (root.is_symlink() or not root.is_dir()
            or stat.S_IMODE(root.stat().st_mode) & 0o077
            or target.is_symlink() or not target.is_file()
            or stat.S_IMODE(target.stat().st_mode) & 0o077):
        raise DanMek030Error("PRIVATE_APPROVAL_MANIFEST_MISSING_OR_UNSAFE")
    size = target.stat().st_size
    if size < 1 or size > MAX_MANIFEST_BYTES:
        raise DanMek030Error("PRIVATE_ENGLISH_APPROVAL_MANIFEST_SIZE")
    raw = target.read_bytes()
    if len(raw) != size:
        raise DanMek030Error("PRIVATE_ENGLISH_APPROVAL_MANIFEST_CHANGED")
    try:
        data = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_json,
            parse_constant=lambda _x: (_ for _ in ()).throw(
                DanMek030Error("PRIVATE_ENGLISH_APPROVAL_NONFINITE")
            ),
        )
    except (UnicodeError, ValueError):
        raise DanMek030Error("PRIVATE_ENGLISH_APPROVAL_INVALID_JSON") from None
    if (type(data) is not dict
            or set(data) != {"schema", "source_owner_reader_snapshot", "rules"}
            or data["schema"] != SCHEMA
            or data["source_owner_reader_snapshot"] != expected_snapshot
            or type(data["rules"]) is not list
            or not 1 <= len(data["rules"]) <= MAX_RULES):
        raise DanMek030Error("PRIVATE_ENGLISH_APPROVAL_SCHEMA_OR_SNAPSHOT")
    seen: set[tuple[str, int]] = set()
    for rule in data["rules"]:
        if type(rule) is not dict or set(rule) != RULE_KEYS:
            raise DanMek030Error("PRIVATE_ENGLISH_APPROVAL_RULE_SHAPE")
        ref, ordinal = rule["reference"], rule["candidate_ordinal"]
        if (type(ref) is not str or not REF.fullmatch(ref)
                or type(ordinal) is not int or ordinal < 1
                or (ref, ordinal) in seen):
            raise DanMek030Error("PRIVATE_ENGLISH_APPROVAL_DUPLICATE_OR_REFERENCE")
        seen.add((ref, ordinal))
    return data, raw


def _review_html(
    entries: list[dict], historically_ambiguous: list[tuple[str, str]],
    english_contexts: dict[str, str],
    *, snapshot: str,
) -> bytes:
    cards = []
    for rule in entries:
        cards.append(
            "<li>" +
            html.escape(rule["reference"], quote=True) + ", pair " +
            str(rule["candidate_ordinal"]) + ": " +
            html.escape(rule["observed_verb_gloss"], quote=True) + " / " +
            html.escape(rule["observed_adjacent_noun_phrase"], quote=True) +
            " — " + html.escape(rule["english_role_class"], quote=True) +
            " — UNAPPROVED<pre>" +
            html.escape(english_contexts[rule["reference"]], quote=True) +
            "</pre></li>"
        )
    legacy = "".join(
        "<details><summary>" + html.escape(ref, quote=True) +
        " — historical ambiguous English</summary><pre>" +
        html.escape(verse, quote=True) + "</pre></details>"
        for ref, verse in historically_ambiguous
    )
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; "
        "object-src 'none'; base-uri 'none'; form-action 'none'\">"
        "<title>Private DANMEK-030 English-subject review</title>"
        "<style>body{font:16px/1.5 Georgia,serif;max-width:960px;"
        "margin:2rem auto;padding:1rem;background:#faf9f7;color:#242424}"
        "li{padding:.35rem}pre{white-space:pre-wrap;overflow-wrap:anywhere}"
        "details{border:1px solid #ccc;padding:.5rem;margin:.5rem}</style>"
        "</head><body><h1>DANMEK-030 private candidate queue</h1>"
        "<p>Snapshot: " + html.escape(snapshot, quote=True) +
        ". None of these candidates are approved by generation. "
        "A direct-object risk is NOT a proven subject. Original source and "
        "approved readers remain unchanged. No publication rights.</p>"
        "<ol>" + "".join(cards) + "</ol><h2>Historical ambiguity context</h2>" +
        legacy + "</body></html>\n"
    ).encode("utf-8")
    if len(page) > MAX_REVIEW_HTML_BYTES:
        raise DanMek030Error("PRIVATE_ENGLISH_REVIEW_HTML_TOO_LARGE")
    return page


def run_private_reviewed_subject_order(
    private_root: Path, *, mode: str,
    require_311: bool = False,
) -> dict:
    """Audit, build review queue, or apply explicit private approval to v3.

    Does NOT write to original CHES, earlier owner HTML, or GitHub.
    """
    if mode not in {"audit", "review", "render"} or type(require_311) is not bool:
        raise DanMek030Error("INVALID_PRIVATE_SUBJECT_ORDER_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        prior = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        snapshot = prior["snapshot_id"]
        manifest, manifest_raw = (
            _approved_manifest(folder, expected_snapshot=snapshot)
            if mode == "render" else (None, b"")
        )
        per_reference: dict[str, list[dict]] = {}
        if manifest is not None:
            for r in manifest["rules"]:
                per_reference.setdefault(r["reference"], []).append(r)
        count_chapters = count_verses = old_ambiguous = possible = 0
        approved = changed_verses = 0
        case_entries: list[dict] = []
        ambiguous_cases: list[tuple[str, str]] = []
        english_contexts: dict[str, str] = {}
        pages: list[tuple[str, bytes]] = []
        seen: set[str] = set()
        digest = hashlib.sha256(
            (REVISION + ":" + snapshot).encode("ascii")
        )
        digest.update(hashlib.sha256(manifest_raw).digest())
        for path in sorted(folder.iterdir(), key=lambda p: p.name):
            if path.is_symlink() or not path.is_file():
                raise DanMek030Error("PRIVATE_SUBJECT_REVIEW_SOURCE_ENTRY_UNSAFE")
            match = CHES_FILE_NAME.fullmatch(path.name)
            if not match:
                raise DanMek030Error("PRIVATE_SUBJECT_REVIEW_SOURCE_ENTRY_INVALID")
            prefix, chapter = match.groups()
            source, sha = _load_private_source(
                folder, prefix=prefix, chapter=int(chapter),
            )
            digest.update((path.name + ":" + sha + "\n").encode("ascii"))
            count_chapters += 1
            if count_chapters > MAX_CHAPTERS:
                raise DanMek030Error("PRIVATE_SUBJECT_REVIEW_CHAPTER_LIMIT")
            sections = []
            for verse in source["verses"]:
                count_verses += 1
                ref = verse["reference"]
                seen.add(ref)
                original = [
                    span["original_ches_line_text"]
                    for span in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                english, previous_status = _read_source_text(
                    original, reference=ref, chapter_sha256=sha,
                )
                if previous_status == "AMBIGUOUS":
                    old_ambiguous += 1
                    if mode == "review":
                        ambiguous_cases.append((ref, english))
                entries = _candidate_rules(
                    reference=ref, chapter_sha256=sha, verse=english,
                )
                possible += len(entries)
                if mode == "review":
                    if entries:
                        english_contexts[ref] = english
                    case_entries.extend(entries)
                    if len(case_entries) > MAX_RULES:
                        raise DanMek030Error("PRIVATE_SUBJECT_REVIEW_RULE_LIMIT")
                if manifest is not None:
                    edited, moved = apply_reviewed_english_subjects(
                        english, reference=ref, chapter_sha256=sha,
                        rules=per_reference.get(ref, []),
                    )
                    approved += moved
                    changed_verses += int(bool(moved))
                    sections.append(
                        "<section><b>" + html.escape(ref, quote=True) +
                        "</b> <span>" + html.escape(edited, quote=True) +
                        "</span></section>"
                    )
            if manifest is not None:
                pages.append((
                    prefix + "." + chapter + ".html",
                    ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                     '<meta http-equiv="Content-Security-Policy" content="'
                     "default-src 'none'; style-src 'unsafe-inline'; "
                     "base-uri 'none'; form-action 'none'\">"
                     "<title>Private OLT English reviewed reading</title>"
                     "<style>body{font:17px/1.6 Georgia,serif;max-width:980px;"
                     "margin:2rem auto}section{border-bottom:1px solid #ccc;"
                     "padding:.5rem 0}b{font:13px system-ui}</style>"
                     "</head><body><h1>Private English reviewed subject-order "
                     "reading — not approved for publication</h1>" +
                     "".join(sections) + "</body></html>\n").encode("utf-8"),
                ))
        if (count_verses != prior["observed_verse_count"]
                or old_ambiguous !=
                prior["olt_owner_candidate_ambiguous_verses_unchanged"]):
            raise DanMek030Error("PRIVATE_SUBJECT_REVIEW_BASELINE_COUNT_CHANGED")
        if require_311 and old_ambiguous != 311:
            raise DanMek030Error("PRIVATE_SUBJECT_REVIEW_EXPECTED_311_CHANGED")
        if manifest is not None:
            if not set(per_reference) <= seen:
                raise DanMek030Error("PRIVATE_SUBJECT_APPROVAL_UNKNOWN_VERSE")
            if approved == 0:
                raise DanMek030Error("PRIVATE_SUBJECT_APPROVAL_NO_REVIEWED_MOVES")
        if prior != build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek030Error("PRIVATE_SUBJECT_REVIEW_SOURCE_CHANGED")
        snapshot_id = "snapshot-" + digest.hexdigest()[:24]
        if mode == "review":
            payload = {
                "schema": SCHEMA, "source_owner_reader_snapshot": snapshot,
                "rules": case_entries,
            }
            json_data = (
                json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            ).encode("utf-8")
            html_data = _review_html(
                case_entries, ambiguous_cases, english_contexts,
                snapshot=snapshot_id,
            )
            root = folder.parent / "ches-subject-review"
            label = hashlib.sha256(json_data).hexdigest()[:20]
            _private_write_once(root, "queue-" + label + ".json", json_data)
            _private_write_once(root, "queue-" + label + ".html", html_data)
        if mode == "render":
            root = folder.parent / "ches-reviewed-subject-reading"
            _safe_dir(root)
            destination = root / snapshot_id
            _safe_dir(destination)
            for name, data in pages:
                _write_once(destination, name, data)
            _write_once(
                destination, "index.html",
                ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                 '<meta http-equiv="Content-Security-Policy" content="'
                 "default-src 'none'; base-uri 'none'; form-action 'none'\">"
                 "<title>Private subject-order reading</title></head><body>"
                 "<h1>English-only reviewed subject-first v3</h1>"
                 "<p>Owner attestations are recorded, not independent grammar "
                 "certification. No public redistribution.</p><ul>" +
                 "".join('<li><a href="' + html.escape(name, quote=True) +
                         '">' + html.escape(name[:-5], quote=True) +
                         "</a></li>" for name, _ in pages) +
                 "</ul></body></html>\n").encode("utf-8"),
            )
        return {
            "checkpoint": REVISION,
            "mode": {
                "audit": "PRIVATE_METADATA_ONLY",
                "review": "PRIVATE_REVIEW_QUEUE_UNAPPROVED",
                "render": "SEPARATE_OWNER_ATTESTED_ENGLISH_READING",
            }[mode],
            "source_owner_reader_snapshot": snapshot,
            "new_private_snapshot_id": snapshot_id,
            "chapters_scanned": count_chapters,
            "verses_scanned": count_verses,
            "historical_ambiguous_english_verses": old_ambiguous,
            "potential_subject_role_reviews_queued": possible,
            "explicitly_attested_english_subject_moves": approved,
            "verses_changed_in_separate_reading": changed_verses,
            "private_review_files_written_or_verified": 2 if mode == "review" else 0,
            "private_reading_html_files_written_or_verified":
                len(pages) + 1 if mode == "render" else 0,
            "original_private_ches_unchanged": True,
            "prior_locked_readers_unchanged": True,
            "independent_grammar_certification": False,
            "hebrew_cross_validation_performed": False,
            "private_text_on_stdout": False,
            "publication_status": "BLOCKED",
        }
    except DanMek030Error:
        raise
    except DanMek027Error as exc:
        # The earlier immutable-output implementation emits only fixed error
        # codes; pass those codes through the 030 surface without source text.
        raise DanMek030Error(str(exc)) from None
    except Exception:
        raise DanMek030Error("PRIVATE_REVIEWED_SUBJECT_ORDER_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-030 private exact subject-role attestation, English only"
    )
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--confirm-machine-readable-use-permission",
                        action="store_true")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--audit-only", action="store_true")
    modes.add_argument("--build-private-review", action="store_true")
    modes.add_argument("--build-approved-reader", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    options = parser.parse_args()
    if not options.confirm_machine_readable_use_permission:
        parser.error("Private CHES use permission must be confirmed")
    try:
        result = run_private_reviewed_subject_order(
            options.private_root,
            mode="review" if options.build_private_review else
                 "render" if options.build_approved_reader else "audit",
            require_311=options.require_311,
        )
    except DanMek030Error:
        parser.exit(2, "DANMEK_030_PRIVATE_ENGLISH_SUBJECT_REVIEW_FAILED\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
