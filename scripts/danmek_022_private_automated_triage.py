"""DANMEK-022: automatic offline triage and private read-only review HTML.

This does NOT identify original-language grammatical subjects, align licensed
CHES glosses to Hebrew words, translate, or change the owner-locked reader.
The entire review stays under the user's private .olt-private directory.
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

from olt_core.sources import load_ot_book, read_provenance
from scripts.ches_014_offline_english_bridge import (
    _load_private_source, _private_archive_root,
)
from scripts.danmek_011_owner_order import apply_owner_approved_candidates
from scripts.danmek_020_private_ambiguous_order_review import (
    REVISION as QUEUE_REVISION, SOURCE_BOOK_CANDIDATES,
    _original_candidate, _private_write_once, build_ambiguous_order_queue,
)

REVISION = "DANMEK-022-PRIVATE-AUTOMATED-REVIEW-v1"
CASE_REF = re.compile(r"([A-Za-z0-9_-]{1,20})\.([1-9][0-9]*)\.([1-9][0-9]*)\Z")
QUEUE_NAME = re.compile(
    re.escape(QUEUE_REVISION.lower()) + r"-([0-9a-f]{20})\.json\Z"
)
MAX_PRIVATE_QUEUE_BYTES = 40_000_000
MAX_CASES = 2500


class DanMek022Error(ValueError):
    """Fixed diagnostics only: never expose original source words or paths."""


def _load_saved_queue(folder: Path, queue_file: Path | None) -> dict:
    if (folder.is_symlink() or not folder.is_dir()
            or stat.S_IMODE(folder.stat().st_mode) & 0o077):
        raise DanMek022Error("PRIVATE_REVIEW_QUEUE_FOLDER_UNSAFE")
    if queue_file is None:
        files = [file for file in folder.iterdir() if QUEUE_NAME.fullmatch(file.name)]
        if len(files) != 1:
            raise DanMek022Error("EXACTLY_ONE_PRIVATE_QUEUE_REQUIRED")
        path = files[0]
    else:
        if not isinstance(queue_file, Path) or not queue_file.is_absolute():
            raise DanMek022Error("PRIVATE_QUEUE_PATH_UNSAFE")
        path = queue_file
        if path.parent != folder:
            raise DanMek022Error("PRIVATE_QUEUE_OUTSIDE_ALLOWED_FOLDER")
    if (not QUEUE_NAME.fullmatch(path.name) or path.is_symlink()
            or not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077):
        raise DanMek022Error("PRIVATE_QUEUE_FILE_UNSAFE")
    size = path.stat().st_size
    if not (0 < size <= MAX_PRIVATE_QUEUE_BYTES):
        raise DanMek022Error("PRIVATE_QUEUE_SIZE_INVALID")
    raw = path.read_bytes()
    if len(raw) != size or hashlib.sha256(raw).hexdigest()[:20] != (
        QUEUE_NAME.fullmatch(path.name).group(1)
    ):
        raise DanMek022Error("PRIVATE_QUEUE_CONTENT_DIGEST_MISMATCH")
    try:
        from scripts.ches_local_archive_audit import _strict_json_pairs
        payload = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_strict_json_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(
                DanMek022Error("PRIVATE_QUEUE_NONFINITE_JSON_REFUSED")
            ),
        )
    except (ValueError, UnicodeError, TypeError) as exc:
        raise DanMek022Error("PRIVATE_QUEUE_JSON_INVALID") from None
    if (not isinstance(payload, dict)
            or payload.get("checkpoint") != QUEUE_REVISION
            or payload.get("scope") != "PRIVATE_ENGLISH_WORD_ORDER_EXCEPTION_REVIEW"
            or payload.get("source_book_prefix_crosswalk_verified") is not False
            or payload.get("hebrew_aramaic_word_alignment_verified") is not False
            or payload.get("approved_english_reorders_from_queue") != 0
            or payload.get("owner_approved_reader_mutated") is not False
            or payload.get("original_source_files_modified") is not False
            or payload.get("human_review_complete") is not False
            or payload.get("publication_status") != "BLOCKED"
            or not isinstance(payload.get("cases"), list)
            or len(payload["cases"]) > MAX_CASES
            or payload.get("total_ambiguous_cases") != len(payload["cases"])):
        raise DanMek022Error("PRIVATE_QUEUE_SAFETY_CONTRACT_INVALID")
    return payload


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _render_private_review(rows: list[dict], *, snapshot: str) -> bytes:
    """Static HTML only; no JS, remote assets, forms or edit controls."""
    blocks = []
    last_prefix = None
    for row in rows:
        ref = row["ref"]
        prefix = ref.split(".", 1)[0]
        if prefix != last_prefix:
            blocks.append("<h2>Source prefix: " + _escape(prefix) + "</h2>")
            last_prefix = prefix
        english = "".join(
            "<li><span class='gloss'>" + _escape(text) + "</span></li>"
            for text in row["english"]
        )
        candidate = row["candidate"]
        if candidate["status"] == "SAME_REFERENCE_ORIGINAL_SOURCE_CANDIDATE_UNREVIEWED":
            words = "".join(
                "<tr><td>" + _escape(token["ordinal"]) + "</td><td lang='he' dir='rtl'>" +
                _escape(token["original_script"]) + "</td><td>" +
                _escape(token["raw_morphology_unreviewed"]) + "</td><td>" +
                _escape(token["raw_lemma_annotation_unreviewed"]) + "</td></tr>"
                for token in candidate["original_source_words_unaligned"]
            )
            source_view = (
                "<p>Candidate: " + _escape(candidate["candidate_source_ref"]) +
                " — same-number lookup ONLY; word and subject alignment NOT VERIFIED.</p>"
                "<table><thead><tr><th>Ordinal</th><th>Original script</th>"
                "<th>Unreviewed raw morphology</th><th>Unreviewed lemma</th>"
                "</tr></thead><tbody>" + words + "</tbody></table>"
            )
        else:
            source_view = "<p>NO SAME-NUMBER ORIGINAL REFERENCE LOCATED. No safe alignment.</p>"
        blocks.append(
            "<details><summary>" + _escape(ref) + " — " +
            _escape(row["class"]) + "</summary>"
            "<p><strong>English regex ambiguity:</strong> multiple patterns detected; "
            "NO editorial change authorized.</p>"
            "<h3>Original CHES English fragments — private, UNALIGNED</h3><ol>" +
            english + "</ol><h3>Original language research candidate</h3>" +
            source_view +
            "<p>Raw verbal morphology tag hints in candidate: " +
            _escape(row["raw_verb_hints"]) +
            ". Counts do NOT identify a grammatical subject, tense or "
            "CHES-to-original match.</p>"
            "<p class='warning'>STATUS: UNREVIEWED — reorder_permitted=false; "
            "word_alignment_verified=false; publication BLOCKED.</p></details>"
        )
    text = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta name='robots' content='noindex,nofollow,noarchive'>"
        "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; "
        "style-src 'unsafe-inline'; img-src 'none'; object-src 'none'; "
        "base-uri 'none'; form-action 'none'\">"
        "<title>OLT private 311-case English ambiguity review — UNVERIFIED</title>"
        "<style>body{font:16px/1.55 system-ui,sans-serif;max-width:1000px;margin:auto;"
        "padding:2rem;background:#fbfaf7;color:#222}details{margin:1rem 0;"
        "border:1px solid #ddd;padding:.75rem;border-radius:.45rem}summary{cursor:pointer;"
        "font-weight:600}h2{margin-top:2rem;border-bottom:2px solid #aaa}"
        "table{border-collapse:collapse;width:100%;font-size:14px}"
        "th,td{border-bottom:1px solid #ddd;padding:.3rem;text-align:left}"
        ".gloss{white-space:pre-wrap;overflow-wrap:anywhere}"
        ".warning{font-weight:700;color:#6b371b}li{margin:.2rem 0}</style></head><body>"
        "<h1>OLT — private English word-order research</h1>"
        "<p>Locally generated, offline, read-only. Not a verified translation. "
        "English CHES source fragments are licensed/private research data. "
        "Original book mapping and same-number reference identity are research "
        "candidates, NOT a certified Hebrew/Aramaic crosswalk. Nothing on this "
        "page can change the previously owner-approved reader.</p>"
        "<p>Reader snapshot: " + _escape(snapshot) +
        ". Cases: " + str(len(rows)) + ". Publication BLOCKED.</p>" +
        "".join(blocks) + "</body></html>\n"
    )
    return text.encode("utf-8")


def triage_private_ambiguities(
    private_root: Path, *, queue_file: Path | None = None,
    write_private_html: bool = False, require_311: bool = False,
) -> dict:
    """Revalidate stored queue against current locked reader and pinned source.

    All results on stdout are metadata only. Private HTML is immutable and
    created only after *every* case passes fail-closed integrity checks.
    """
    if type(write_private_html) is not bool or type(require_311) is not bool:
        raise DanMek022Error("INVALID_AUTOMATED_REVIEW_OPTIONS")
    try:
        archive = _private_archive_root(private_root)
        folder = archive.parent / "ches-order-review"
        queue = _load_saved_queue(folder, queue_file)
        current = build_ambiguous_order_queue(
            archive, write_private=False, require_311=require_311,
        )
        if (queue["reader_snapshot_id"] != current["reader_snapshot_id"]
                or queue["source_verse_count"] != current["source_verses_seen"]
                or queue["total_ambiguous_cases"] != current["ambiguous_english_verses_queued"]
                or queue["original_verse_locator_candidates_unreviewed"] !=
                   current["original_source_same_reference_candidates_unreviewed"]
                or queue["original_verse_locators_missing"] !=
                   current["original_source_reference_missing"]):
            raise DanMek022Error("PRIVATE_QUEUE_READER_SNAPSHOT_MISMATCH")
        if require_311 and len(queue["cases"]) != 311:
            raise DanMek022Error("PRIVATE_REVIEW_COUNT_NOT_311")
        original_registry = read_provenance()
        names = {b["book"] for b in original_registry["ot"]["books"]}
        if set(SOURCE_BOOK_CANDIDATES.values()) != names:
            raise DanMek022Error("ORIGINAL_SOURCE_REGISTRY_CHANGED")
        checked_chapter = None
        loaded_chapter = None
        checked_prefix = None
        source_by_reference = {}
        seen: set[str] = set()
        per_prefix: Counter[str] = Counter()
        classes: Counter[str] = Counter()
        verb_hint_total = 0
        display = []
        for case in queue["cases"]:
            ref = case["source_ches_verse_reference"]
            match = CASE_REF.fullmatch(ref)
            if match is None or ref in seen:
                raise DanMek022Error("INVALID_OR_DUPLICATED_QUEUE_REFERENCE")
            seen.add(ref)
            prefix, chapter_no, verse_no = match.group(1), int(match.group(2)), int(match.group(3))
            book = SOURCE_BOOK_CANDIDATES.get(prefix)
            if book is None:
                raise DanMek022Error("UNKNOWN_SOURCE_PREFIX")
            chapter_key = (prefix, chapter_no)
            if chapter_key != checked_chapter:
                loaded_chapter, source_sha = _load_private_source(
                    archive, prefix=prefix, chapter=chapter_no,
                )
                checked_chapter = chapter_key
            if source_sha != case["source_ches_chapter_json_sha256"]:
                raise DanMek022Error("PRIVATE_CHAPTER_DIGEST_NOT_CURRENT")
            verses = [v for v in loaded_chapter["verses"] if v["reference"] == ref]
            if len(verses) != 1:
                raise DanMek022Error("PRIVATE_CHES_VERSE_NOT_IDENTICAL")
            english = [
                part["original_ches_line_text"]
                for part in verses[0]["source_ches_spans_NOT_OLT_TRANSLATION"]
            ]
            stored = case["private_source_english_fragments_unaligned"]
            if stored != [
                {"fragment_ordinal": i, "private_ches_text": txt}
                for i, txt in enumerate(english, 1)
            ]:
                raise DanMek022Error("PRIVATE_ENGLISH_SOURCE_FRAGMENTS_CHANGED")
            result, reason = apply_owner_approved_candidates(
                reference=ref, chapter_sha256=source_sha, original=english,
                visible=list(english),
            )
            if reason != "AMBIGUOUS" or result != english:
                raise DanMek022Error("PRIVATE_ORDER_AMBIGUITY_NOT_REPRODUCIBLE")
            if (case["english_order_status"] != "AMBIGUOUS_MULTIPLE_PATTERNS_UNCHANGED"
                    or case["english_order_edit_proposed"] is not False
                    or case["human_original_language_subject_review"] != "NOT_DONE"
                    or case["source_english_fragment_to_original_word_links"] != []
                    or case["source_to_original_book_mapping_verified"] is not False
                    or case["original_source_subject_verified"] is not False
                    or case["word_alignment_verified"] is not False
                    or case["reorder_permitted"] is not False
                    or case["publication_status"] != "BLOCKED"):
                raise DanMek022Error("PRIVATE_CASE_UNSAFE_APPROVAL_STATUS")
            if checked_prefix != prefix:
                original = load_ot_book(book, registry=original_registry)
                originals = original["verses"]
                source_by_reference = {v["reference"]: v for v in originals}
                if len(source_by_reference) != len(originals):
                    raise DanMek022Error("DUPLICATE_ORIGINAL_VERSE_IDS")
                checked_prefix = prefix
            candidate_ref = f"{book}.{chapter_no}.{verse_no}"
            evidence, present = _original_candidate(
                original_book=book, reference=candidate_ref,
                by_reference=source_by_reference,
            )
            if case["original_source_verse_candidate"] != evidence:
                raise DanMek022Error("ORIGINAL_SOURCE_CANDIDATE_CHANGED")
            hints = sum(
                word["raw_morphology_unreviewed"].startswith(("HV", "AV"))
                for word in evidence["original_source_words_unaligned"]
            )
            verb_hint_total += hints
            classification = (
                "REFERENCE_CANDIDATE_PRESENT_UNALIGNED"
                if present else "NO_SAFE_ORIGINAL_REFERENCE"
            )
            classes[classification] += 1
            per_prefix[prefix] += 1
            display.append({
                "ref": ref, "english": english, "candidate": evidence,
                "class": classification, "raw_verb_hints": hints,
            })
        if (dict(sorted(per_prefix.items())) != current["by_source_prefix_ambiguous_count"]
                or classes["REFERENCE_CANDIDATE_PRESENT_UNALIGNED"] !=
                   current["original_source_same_reference_candidates_unreviewed"]
                or classes["NO_SAFE_ORIGINAL_REFERENCE"] !=
                   current["original_source_reference_missing"]):
            raise DanMek022Error("PRIVATE_QUEUE_CASE_COUNTS_DIVERGED")
        # Re-read source snapshot to ensure no source-chapter mutation.
        repeated = build_ambiguous_order_queue(
            archive, write_private=False, require_311=require_311,
        )
        if repeated != current:
            raise DanMek022Error("PRIVATE_SOURCE_CHANGED_DURING_REVIEW")
        html_status = "AUDIT_ONLY_NO_HTML_WRITTEN"
        if write_private_html:
            page = _render_private_review(display, snapshot=current["reader_snapshot_id"])
            filename = REVISION.lower() + "-" + hashlib.sha256(page).hexdigest()[:20] + ".html"
            html_status = _private_write_once(folder, filename, page)
        return {
            "checkpoint": REVISION,
            "mode": "OFFLINE_PRIVATE_AUTOMATED_TRIAGE_NO_EDITS",
            "locked_reader_snapshot_id": current["reader_snapshot_id"],
            "ambiguous_cases_rechecked": len(display),
            "source_reference_candidates_present_unaligned":
                classes["REFERENCE_CANDIDATE_PRESENT_UNALIGNED"],
            "missing_original_reference_cases": classes["NO_SAFE_ORIGINAL_REFERENCE"],
            "raw_original_verb_morphology_tag_hints_unreviewed": verb_hint_total,
            "by_source_prefix_ambiguous_count": dict(sorted(per_prefix.items())),
            "candidate_original_book_mapping_verified": False,
            "original_word_subject_alignment_verified": False,
            "grammatical_subjects_verified": 0,
            "english_editorial_changes_applied": 0,
            "all_cases_still_require_evidence_review": True,
            "private_original_files_modified": False,
            "owner_verified_html_modified": False,
            "private_review_html_status": html_status,
            "private_text_printed": False,
            "publication_status": "BLOCKED",
        }
    except DanMek022Error:
        raise
    except Exception:
        raise DanMek022Error("PRIVATE_AUTOMATED_TRIAGE_FAILED") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DANMEK-022 offline, private English ambiguity triage"
    )
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument("--queue-file", type=Path)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    parser.add_argument("--require-311", action="store_true")
    parser.add_argument(
        "--write-private-html", action="store_true",
        help="Opt in to immutable private HTML with licensed CHES and original-language source",
    )
    opts = parser.parse_args()
    if not opts.confirm_machine_readable_use_permission:
        parser.error("Owner-reported private source-use permission required")
    try:
        report = triage_private_ambiguities(
            opts.private_root, queue_file=opts.queue_file,
            write_private_html=opts.write_private_html,
            require_311=opts.require_311,
        )
    except DanMek022Error:
        parser.exit(2, "DANMEK_022_PRIVATE_TRIAGE_FAILED\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
