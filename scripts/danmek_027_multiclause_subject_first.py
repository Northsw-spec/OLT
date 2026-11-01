"""DANMEK-027: additional *versioned* English post-verbal-subject reading.

The owner requests a subject before its adjacent pronoun-verb gloss, including
multiple independent clauses in one verse. Preserve the full pronoun-verb
string and all other English. CHES is the accepted authoritative English
source for this project; no Hebrew/OSHB verification is part of this tool.

This code does NOT infer that every capitalized noun after a verb is its
subject: a transitive verb may have a following direct object. Only bounded
owner-directed and subject-compatible structures are changed. Any remaining
potential matches are left unchanged and counted as unresolved. This is a
NEW opt-in offline reading; DANMEK-013/014 snapshots and source are untouched.
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
from scripts.danmek_011_owner_order import (
    INLINE, JOINED_YAHWEH, JOINED_AND_SUBJECT,
    apply_owner_approved_candidates, discover_candidates,
)
from scripts.danmek_012_display import hide_isolated_c

REVISION = "DANMEK-028-GUARDED-MULTICLAUSE-SUBJECT-ORDER-v2"
MAX_CHAPTERS = 1000
MAX_VERSE_CHARS = 50000
# The same subject can have a title, a definite article, or two name parts.
# Do not infer a subject from arbitrary lowercase nouns or from a bare object.
NAME = r"[A-Z][A-Za-z'’-]{1,49}"
TITLE = r"(?:king|queen|priest|prophet|servant|messenger|men|women|people)"
SUBJECT = (
    r"(?:the[· ](?:" + NAME + r"|" + TITLE + r")(?:[ ]" + NAME + r")?"
    r"|" + NAME + r"(?:[ ]" + NAME + r"){0,2})"
)

# The owner explicitly supplied the hearing/report construction. The group
# ending -s is a constrained English plural, and the following that-clause
# is a required *context cue*. Neither a bare hearer nor a transitive object
# by itself licenses a movement.
_REPORT_HEARER = re.compile(
    r"(?<![A-Za-z-])(?P<verb>(?:and[· ])?they-(?:are|were)-hearing)[ \t]+"
    r"(?P<subject>(?:the[· ])?[A-Z][A-Za-z'’-]{1,49}s)"
    r"(?=[ \t]+that[ \t]+(?:he|she)-(?:was|is)-anointed[ \t]+(?:the[· ])?[A-Z])"
)

# Explicit passive wording can mark a postposed noun subject in the
# owner's repeated-pronoun editorial style. Avoid "called" (e.g., "called
# Rowan" can be a name complement), and never equate passive matching
# with proof from Hebrew syntax.
_PASSIVE = re.compile(
    r"(?<![A-Za-z-])(?P<verb>(?:and[· ])?"
    r"(?:he|she|they|we)-(?:is|was|were)-"
    r"(?:anointed|appointed|chosen|buried|crowned|killed|blessed))[ \t]+"
    r"(?P<subject>" + SUBJECT + r")(?![A-Za-z-])"
)

# Small list of *normally intransitive in this immediate context* predicates.
# Exclude return/returned: "he-returned Rowan" may mean Rowan is an OBJECT.
_INTRANSITIVE = re.compile(
    r"(?<![A-Za-z-])(?P<verb>(?:and[· ])?"
    r"(?:he|she|they|we|thou|you|ye)-"
    r"(?:came|come|comes|went|goes|arose|rose|rests|rested|"
    r"died|dies|lived|lives|stood|stands|slept|sleeps|sat|sits))[ \t]+"
    r"(?P<subject>" + SUBJECT + r")(?![A-Za-z-])"
)

RULES = (
    ("OWNER_REPORT_HEARING_MULTI_CLAUSE", _REPORT_HEARER),
    ("POSTPOSED_PASSIVE_SUBJECT", _PASSIVE),
    ("POSTPOSED_INTRANSITIVE_SUBJECT", _INTRANSITIVE),
)


def _legacy_candidate_guard(
    *, reference: str, chapter_sha256: str, original: list[str],
) -> tuple[list[str], str, bool]:
    """New reader guard: never inherit a *newly unknown* object-to-subject move.

    The locked prior reader itself is unchanged. Its broad older typography
    can move "he-saw Person" as if Person were the subject. That is not a
    defensible automatic grammatical conclusion. Carry forward only:
      - unmistakable intransitive/passive shapes also covered by this module;
      - the two historical owner-explicit constructions from the old mode.
    Everything else remains CHES source order in the NEW optional reader.
    The skipped count is audit metadata, not proof of a semantic error.
    """
    proposals, ambiguous = discover_candidates(
        reference, chapter_sha256, original,
    )
    visible, reason = apply_owner_approved_candidates(
        reference=reference, chapter_sha256=chapter_sha256,
        original=original, visible=list(original),
    )
    if reason != "APPLIED":
        return visible, reason, False
    if ambiguous or len(proposals) != 1:
        raise DanMek027Error("LEGACY_ENGLISH_REORDER_CANDIDATE_INCONSISTENT")
    candidate = proposals[0]
    verb = candidate["original_verb"]
    subject = candidate["original_subject"]
    pair = verb + " " + subject
    if (_INTRANSITIVE.fullmatch(pair) is not None
            or _PASSIVE.fullmatch(pair) is not None):
        return visible, reason, False
    # These are *old, explicit owner authorizations* and therefore preserved.
    # They are not a general authorization for similarly spelled verbs.
    if verb in ("and·he-shaped", "And·he-shaped") and subject == "God":
        return visible, reason, False
    if (candidate["mode"] == "inline" and
            (JOINED_YAHWEH.match(candidate["original_fragment"])
             or JOINED_AND_SUBJECT.match(candidate["original_fragment"]))):
        return visible, reason, False
    # This is a separately versioned conservative new reader, not a
    # retroactive modification of the previously approved HTML snapshot.
    return list(original), "LEGACY_UNVERIFIED_SUBJECT_UNCHANGED", True

class DanMek027Error(ValueError):
    """Fixed-code, private-data-safe failure."""


def reorder_postverbal_subjects(
    fragments: list[str | None],
) -> tuple[list[str | None], list[dict], int]:
    """Reorder every distinct *recognized subject* in one English verse.

    Multiple nonoverlapping clauses can be changed in one operation. A
    possible but unproved noun-object/subject relationship remains unchanged.
    The return count is unresolved *candidate shapes*, not grammatical errors.
    """
    if (type(fragments) is not list or not fragments or len(fragments) > 10000
            or any(value is not None and type(value) is not str for value in fragments)):
        raise DanMek027Error("INVALID_PRIVATE_ENGLISH_FRAGMENT_SEQUENCE")
    text = " ".join(x or "" for x in fragments)
    if len(text) > MAX_VERSE_CHARS:
        raise DanMek027Error("ENGLISH_VERSE_REORDER_LIMIT_EXCEEDED")
    found: list[tuple[int, int, str, str]] = []
    for code, rule in RULES:
        for match in rule.finditer(text):
            if any(not (match.end() <= left or match.start() >= right)
                   for left, right, _, _ in found):
                raise DanMek027Error("OVERLAPPING_ENGLISH_SUBJECT_RULES")
            found.append((match.start(), match.end(), code,
                          _format_subject_before_verb(
                              match.group("verb"), match.group("subject"))))
    found.sort()
    # INLINE is a *candidate* detector, not proof that a capitalized item
    # is a subject. Count unidentified shapes without moving them.
    uncertain = 0
    for guess in INLINE.finditer(text):
        if not any(left <= guess.start() and guess.end() <= right
                   for left, right, _, _ in found):
            uncertain += 1
    if not found:
        return list(fragments), [], uncertain
    changed = text
    for left, right, _, replacement in reversed(found):
        changed = changed[:left] + replacement + changed[right:]
    evidence = [
        {"reason_code": code, "status": "OWNER_DIRECTED_BOUNDED_ENGLISH_ORDER",
         "original_verb_position": left, "original_match_end": right,
         "hebrew_word_alignment_performed": False}
        for left, right, code, _ in found
    ]
    # A separate derived view may use a single English text node for a
    # changed verse. Unchanged verses retain exact source-span display.
    return [changed], evidence, uncertain


def _format_subject_before_verb(verb: str, subject: str) -> str:
    if verb.startswith(("and·", "And·", "and ", "And ")):
        separator = "·" if "·" in verb[:4] else " "
        conjunction, rest = verb.split(separator, 1)
        return conjunction + " " + subject + " -" + separator + rest
    return subject + " - " + verb


def _safe_dir(folder: Path) -> None:
    if folder.is_symlink():
        raise DanMek027Error("PRIVATE_READING_DIRECTORY_SYMLINK")
    if folder.exists():
        if not folder.is_dir() or stat.S_IMODE(folder.stat().st_mode) & 0o077:
            raise DanMek027Error("PRIVATE_READING_DIRECTORY_UNSAFE")
    else:
        folder.mkdir(mode=0o700)


def _write_once(folder: Path, name: str, data: bytes) -> None:
    """Atomic exclusive file publication, strict 0600 and no overwritten data."""
    if "/" in name or name.startswith(".") or not name:
        raise DanMek027Error("PRIVATE_READING_FILENAME_INVALID")
    target = folder / name
    if target.is_symlink():
        raise DanMek027Error("PRIVATE_READING_OUTPUT_SYMLINK")
    if target.exists():
        if (not target.is_file() or stat.S_IMODE(target.stat().st_mode) & 0o077
                or target.read_bytes() != data):
            raise DanMek027Error("PRIVATE_READING_NO_OVERWRITE")
        return
    fd, temporary = tempfile.mkstemp(prefix=".danmek027-", dir=folder)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, target, follow_symlinks=False)
        except FileExistsError as exc:
            raise DanMek027Error("PRIVATE_READING_RACE_NO_OVERWRITE") from exc
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _frame(heading: str, content: str) -> bytes:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src '
        "'none'; style-src 'unsafe-inline'; img-src 'none'; object-src "
        "'none'; base-uri 'none'; form-action 'none'\">"
        '<title>' + html.escape(heading, quote=True) + '</title>'
        '<style>body{font:17px/1.55 Georgia,serif;max-width:900px;margin:2rem auto;'
        'padding:0 1.3rem;background:#faf9f6;color:#232323}'
        'nav a{margin-right:1rem}.verse{padding:.5rem 0;border-bottom:1px solid #ddd}'
        '.ref{font:600 12px system-ui;display:inline-block;min-width:72px}'
        '.gloss{white-space:pre-wrap;display:inline-block;margin-right:.35em}'
        '.muted{font:13px system-ui;color:#555}</style></head><body>' +
        content + '</body></html>\n'
    ).encode("utf-8")


def build_subject_first_reader(
    private_root: Path, *, render: bool = False, require_311: bool = False,
) -> dict:
    """Produce a distinct reading, never mutate approved CHES/DANMEK snapshots."""
    if type(render) is not bool or type(require_311) is not bool:
        raise DanMek027Error("INVALID_POSTVERBAL_READER_OPTIONS")
    try:
        folder = _private_archive_root(private_root)
        prior = build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        pages = []
        total_verses = changed_verses = total_changes = unresolved = old_ambiguous = 0
        legacy_subject_risk_skipped = 0
        reason_totals: Counter[str] = Counter()
        digest = hashlib.sha256(
            (REVISION + ":" + prior["snapshot_id"]).encode("ascii")
        )
        for file in sorted(folder.iterdir(), key=lambda path: path.name):
            if file.is_symlink() or not file.is_file():
                raise DanMek027Error("PRIVATE_READER_SOURCE_ENTRY_UNSAFE")
            match = NAME.fullmatch(file.name)
            if match is None:
                raise DanMek027Error("PRIVATE_READER_SOURCE_NAME_INVALID")
            prefix, chapter_text = match.groups()
            chapter = int(chapter_text)
            source, sha = _load_private_source(folder, prefix=prefix, chapter=chapter)
            digest.update((file.name + ":" + sha + "\n").encode("ascii"))
            sections = []
            for verse in source["verses"]:
                total_verses += 1
                original = [
                    part["original_ches_line_text"]
                    for part in verse["source_ches_spans_NOT_OLT_TRANSLATION"]
                ]
                prior_visible, old_reason, skipped_legacy = _legacy_candidate_guard(
                    reference=verse["reference"], chapter_sha256=sha,
                    original=original,
                )
                legacy_subject_risk_skipped += int(skipped_legacy)
                old_ambiguous += int(old_reason == "AMBIGUOUS")
                prior_visible, _ = simplify_sur_faces_for_olt_view(prior_visible)
                prior_visible, _ = hide_isolated_c(prior_visible)
                after, evidence, uncertain = reorder_postverbal_subjects(prior_visible)
                unresolved += uncertain
                total_changes += len(evidence)
                changed_verses += int(bool(evidence))
                for evidence_item in evidence:
                    reason_totals[evidence_item["reason_code"]] += 1
                spans = "".join(
                    '<span class="gloss">' + html.escape(value, quote=True) +
                    "</span>" for value in after if value is not None
                )
                sections.append(
                    '<section class="verse"><span class="ref">' +
                    html.escape(verse["reference"], quote=True) +
                    '</span>' + spans + "</section>"
                )
            pages.append((
                file.name[:-5] + ".html",
                _frame(
                    "Private subject-first source " + prefix + "." + chapter_text,
                    "<h1>Private English " + html.escape(prefix + "." + chapter_text) +
                    "</h1><p class='muted'>New versioned, owner-directed subject-first "
                    "view. CHES authoritative; no Hebrew revalidation. "
                    "Some verb-noun pairs remain unresolved and certain broad "
                    "legacy typography movements are not inherited in this "
                    "new reading, to avoid treating objects as subjects. "
                    "The old approved reader remains unchanged. No publication rights.</p>"
                    '<nav><a href="index.html">Contents</a></nav>' +
                    "".join(sections),
                ),
            ))
            if len(pages) > MAX_CHAPTERS:
                raise DanMek027Error("PRIVATE_READER_CHAPTER_LIMIT")
        if total_verses != prior["observed_verse_count"]:
            raise DanMek027Error("PRIVATE_READER_VERSE_COUNT_MISMATCH")
        if old_ambiguous != prior["olt_owner_candidate_ambiguous_verses_unchanged"]:
            raise DanMek027Error("PRIVATE_READER_AMBIGUITY_COUNT_MISMATCH")
        if require_311 and old_ambiguous != 311:
            raise DanMek027Error("OWNER_REPORTED_311_AMBIGUITIES_CHANGED")
        if prior != build_private_reader(
            folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        ):
            raise DanMek027Error("PRIVATE_READER_SOURCE_CHANGED_DURING_SCAN")
        snapshot = "snapshot-" + digest.hexdigest()[:24]
        if render:
            root = folder.parent / "ches-subject-reading"
            _safe_dir(root)
            destination = root / snapshot
            _safe_dir(destination)
            contents = "".join(
                '<li><a href="' + html.escape(name, quote=True) + '">' +
                html.escape(name.removesuffix(".html")) + "</a></li>"
                for name, _ in pages
            )
            index = _frame(
                "DANMEK-027 private English reading",
                "<h1>Owner-directed English subject-first reading v2</h1>"
                "<p class='muted'>Separate from locked DANMEK-013/014 source "
                "snapshots. Original CHES unchanged. English-only editorial "
                "reorder, not Hebrew grammar verification. Publication BLOCKED.</p>"
                "<ul>" + contents + "</ul>",
            )
            # Never overwrite any previously approved reader output.
            for name, data in pages:
                _write_once(destination, name, data)
            _write_once(destination, "index.html", index)
        return {
            "checkpoint": REVISION,
            "mode": "SEPARATELY_VERSIONED_ENGLISH_MULTICLAUSE_SUBJECT_FIRST",
            "source_owner_reader_snapshot_id": prior["snapshot_id"],
            "new_private_snapshot_id": snapshot,
            "source_chapters_scanned": len(pages),
            "source_verses_scanned": total_verses,
            "historical_ambiguous_english_verses": old_ambiguous,
            "new_postverbal_subject_pairs_reordered": total_changes,
            "legacy_unverified_subject_moves_not_inherited": legacy_subject_risk_skipped,
            "locked_legacy_html_remains_available_unchanged": True,
            "verses_with_new_reorders": changed_verses,
            "unresolved_verb_noun_shapes_not_reordered": unresolved,
            "by_bounded_reason": dict(sorted(reason_totals.items())),
            "new_private_html_pages": len(pages) + 1 if render else 0,
            "hebrew_cross_validation_performed": False,
            "original_ches_source_modified": False,
            "locked_danmek_reader_modified": False,
            "publication_status": "BLOCKED",
        }
    except DanMek027Error:
        raise
    except Exception:
        raise DanMek027Error("PRIVATE_POSTVERBAL_READER_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-027 offline, private, versioned subject-first English"
    )
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--build-private-reader", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    opts = parser.parse_args()
    if not opts.confirm_machine_readable_use_permission:
        parser.error("Private CHES source use permission required")
    try:
        report = build_subject_first_reader(
            opts.private_root, render=opts.build_private_reader,
            require_311=opts.require_311,
        )
    except DanMek027Error:
        parser.exit(2, "DANMEK_027_PRIVATE_SUBJECT_FIRST_READER_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
