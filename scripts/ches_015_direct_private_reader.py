"""CHES-015: minimal OFFLINE private reader of the original extracted source.

This is deliberately NOT a new Hebrew->English translator. Every original
green-source PDF fragment is preserved as its own HTML text node, in source
verse order; there are no lexical substitutions, morphology rules, invented
crosswalks, verse-number fixes, or paraphrases. Generated pages stay inside
.olt-private/ and must never become GitHub pages/artifacts.
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
    CHES014BridgeError, _private_archive_root, _load_private_source,
)
from scripts.ches_local_archive_audit import CHAPTERS_EXPECTED, PREFIXES_EXPECTED
from scripts.danmek_008_english_display import REVISION as OLT_DISPLAY_REVISION, simplify_sur_faces_for_olt_view
from scripts.danmek_ylt import (
    REVISION as YLT_OVERLAY_REVISION, DanMekYLTError,
    load_private_ylt, propose_ylt_verse_overrides,
)

NAME = re.compile(r"([A-Za-z0-9_-]{1,20})\.([1-9][0-9]*)\.json\Z")
REVISION = "CHES-015-PRIVATE-DIRECT-READER-v1"
CSS = """body{font:17px/1.55 Georgia,serif;max-width:850px;margin:2rem auto;padding:0 1.3rem;background:#faf9f6;color:#232323}
h1,h2{line-height:1.25}nav{padding:1rem 0}nav a{margin-right:1.1rem}
.verse{padding:.65rem 0;border-bottom:1px solid #e1ded7}
.ref{display:inline-block;font:600 13px system-ui,sans-serif;color:#616161;margin-right:1rem;min-width:70px}
.gloss{white-space:pre-wrap;display:inline-block;margin-right:.35em}
.muted{font:13px/1.6 system-ui,sans-serif;color:#555}
a{color:#125bb0} .contents a{display:inline-block;padding:.4rem .75rem}
"""


class CHES015ReaderError(ValueError):
    """Privacy/safety or private archive integrity stop, never source text."""


def _frame(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
        'style-src \'unsafe-inline\'; img-src \'none\'; object-src \'none\'; '
        'base-uri \'none\'; form-action \'none\'">'
        '<title>' + html.escape(title) + '</title><style>' + CSS +
        '</style></head><body>' + body + '</body></html>\n'
    )


def _render_chapter(source: dict, *, prefix: str, chapter: int,
                    previous: str | None, following: str | None,
                    ylt_edits: dict[tuple[str, int], str] | None = None,
                    ylt_mode: bool = False,
                    olt_display_faces: bool = False) -> bytes:
    ref = f"{prefix}.{chapter}"
    if olt_display_faces:
        description = (
            'Separate private OLT English display: exact "sur faces" is '
            'simplified to "faces" for reading. The original CHES files '
            'and source Hebrew word order are unchanged. Source-to-Hebrew '
            'lemma correspondence is not verified. No public distribution.'
        )
    elif ylt_mode:
        description = (
            'YLT 1898 guided editorial overlay (nouns and tense only). '
            'Unchanged CHES fragments where no unique verse-level YLT match '
            'exists. Hebrew word-to-English fragment alignment NOT verified. '
            'No independent OLT translation or public distribution.'
        )
    else:
        description = (
            'Unmodified source fragment text. '
            'No word-level alignment, grammar corrections or new OLT translation. '
            'Personal offline reading only; not for distribution.'
        )
    header = ('<h1>Private source ' + html.escape(ref) + '</h1>'
              '<p class="muted">' + description + '</p>')
    nav = '<nav><a href="index.html">Contents</a>'
    if previous:
        nav += '<a href="' + html.escape(previous) + '.html">Previous</a>'
    if following:
        nav += '<a href="' + html.escape(following) + '.html">Next</a>'
    nav += '</nav>'
    rows = []
    for verse in source["verses"]:
        label = verse["reference"]
        alt = verse.get("original_pdf_alternate_verse_number_not_oshb_crosswalk")
        if alt is not None:
            label += f" (source alternate {alt})"
        # The optional OLT display changes only a literal English phrase,
        # after any YLT noun/tense edits. Original CHES JSON is untouched.
        texts = [
            (ylt_edits or {}).get((verse["reference"], i),
                span["original_ches_line_text"])
            for i, span in enumerate(
                verse["source_ches_spans_NOT_OLT_TRANSLATION"], 1
            )
        ]
        visible = (simplify_sur_faces_for_olt_view(texts)[0]
                   if olt_display_faces else texts)
        fragments = "".join(
            '<span class="gloss">' + html.escape(text, quote=True) + '</span>'
            for text in visible if text is not None
        )
        rows.append('<section class="verse"><span class="ref">' +
                    html.escape(label) + '</span>' + fragments + '</section>')
    return _frame(f"Private CHES source {ref}", header + nav + "".join(rows) + nav).encode("utf-8")


def _render_index(
    records: list[tuple[str, int]], missing: int, *, ylt_mode: bool = False,
    olt_display_faces: bool = False,
) -> bytes:
    links = "".join(
        '<a href="' + html.escape(f"{prefix}.{number}") + '.html">' +
        html.escape(f"{prefix}.{number}") + '</a>'
        for prefix, number in records
    )
    source_statement = (
        'Owner-selected English display-only simplification: exact '
        '"sur faces" appears as "faces". Original CHES remains unchanged. '
        'Hebrew lemma correspondence is not verified.'
        if olt_display_faces else (
            'YLT 1898 guided noun/tense corrections where one-to-one verse-word '
            'evidence is unambiguous; other CHES text preserved.' if ylt_mode else
            'Original English source fragment text is presented unchanged.'
        )
    )
    body = (
        '<h1>Private source reader</h1><p class="muted">Offline only. ' +
        source_statement +
        ' These pages are neither an independently translated OLT Bible '
        'nor a licensed public edition.</p>'
        f'<p>Imported chapters observed: {len(records)} / {CHAPTERS_EXPECTED}; '
        f'internal numbering gaps observed: {missing}.</p>'
        '<p class="muted">Numbers here do not independently verify the upstream '
        'index, complete coverage, word alignment or publication rights.</p>'
        '<div class="contents">' + links + '</div>'
    )
    return _frame("Private source contents", body).encode("utf-8")


def _safe_folder(path: Path) -> None:
    if path.is_symlink():
        raise CHES015ReaderError("SYMLINKED_PRIVATE_OUTPUT_DIRECTORY")
    if path.exists():
        if not path.is_dir() or stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise CHES015ReaderError("UNSAFE_PRIVATE_OUTPUT_DIRECTORY")
    else:
        path.mkdir(mode=0o700)


def _write_once(path: Path, content: bytes) -> None:
    if path.is_symlink():
        raise CHES015ReaderError("SYMLINKED_PRIVATE_READER_OUTPUT")
    if path.exists():
        if (not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077
                or path.read_bytes() != content):
            raise CHES015ReaderError("PRIVATE_READER_OUTPUT_CONFLICT")
        return
    fd, temp = tempfile.mkstemp(prefix=".ches-reader-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as dest:
            dest.write(content)
        os.chmod(temp, 0o600)
        # No source data ever appears in Git; private only. No operator files
        # are overwritten; a different prior output is a hard stop.
        if path.exists() or path.is_symlink():
            raise CHES015ReaderError("PRIVATE_READER_OUTPUT_CONFLICT")
        os.rename(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def build_private_reader(
    source_root: Path, *, render: bool = False, use_ylt_authority: bool = False,
    olt_display_faces: bool = False,
) -> dict:
    """Inspect all present private chapters, optionally write static HTML.

    Only counts and status flags are returned. Partial archives are allowed
    but never called complete; any malformed chapter is a hard error.
    """
    if (type(render) is not bool or type(use_ylt_authority) is not bool
            or type(olt_display_faces) is not bool):
        raise CHES015ReaderError("INVALID_RENDER_MODE")
    try:
        folder = _private_archive_root(source_root)
    except CHES014BridgeError as exc:
        raise CHES015ReaderError("UNSAFE_PRIVATE_ARCHIVE_ROOT") from exc
    records = []
    digest = hashlib.sha256(REVISION.encode("ascii"))
    ylt_data = None
    ylt_sha = None
    if use_ylt_authority:
        try:
            ylt_data, ylt_sha = load_private_ylt(folder)
        except DanMekYLTError as exc:
            raise CHES015ReaderError("PINNED_PUBLIC_DOMAIN_YLT_SOURCE_REQUIRED") from exc
        digest.update((YLT_OVERLAY_REVISION + ":" + ylt_sha).encode("ascii"))
    if olt_display_faces:
        # The option creates a distinct immutable snapshot. Original CHES
        # and YLT-only snapshots retain their existing IDs and bytes.
        digest.update(OLT_DISPLAY_REVISION.encode("ascii"))
    edits_by_chapter = {}
    count_noun_edits = count_tense_edits = count_unmapped = count_ambiguous = 0
    count_display_faces = 0
    unmapped_by_source_prefix: dict[str, int] = {}
    index_hashes: set[str] = set()
    seen_pdf_hashes: set[str] = set()
    chapters_by_prefix: dict[str, set[int]] = {}
    total_verses = total_fragments = 0
    for file in sorted(folder.iterdir(), key=lambda p: p.name):
        if file.is_symlink() or not file.is_file():
            raise CHES015ReaderError("UNEXPECTED_PRIVATE_ARCHIVE_ENTRY")
        match = NAME.fullmatch(file.name)
        if match is None:
            raise CHES015ReaderError("UNKNOWN_PRIVATE_ARCHIVE_ENTRY")
        prefix, raw_chapter = match.groups()
        chapter = int(raw_chapter)
        if chapter > 250:
            raise CHES015ReaderError("INVALID_PRIVATE_SOURCE_CHAPTER_NUMBER")
        try:
            item, json_sha = _load_private_source(folder, prefix=prefix, chapter=chapter)
        except Exception as exc:
            raise CHES015ReaderError("PRIVATE_SOURCE_SCHEMA_VALIDATION_FAILED") from exc
        source_pdf_sha = item["original_source_pdf_sha256"]
        if source_pdf_sha in seen_pdf_hashes:
            raise CHES015ReaderError("DUPLICATE_ORIGINAL_PDF_IDENTITY")
        seen_pdf_hashes.add(source_pdf_sha)
        index_hashes.add(item["source_original_index_sha256"])
        chapters_by_prefix.setdefault(prefix, set()).add(chapter)
        total_verses += len(item["verses"])
        total_fragments += item["ches_pdf_green_spans"]
        records.append((prefix, chapter))
        digest.update(f"{prefix}.{chapter}:{json_sha}\n".encode("ascii"))
        if use_ylt_authority:
            edits, stats = propose_ylt_verse_overrides(
                item, prefix=prefix, chapter=chapter, ylt=ylt_data,
            )
            edits_by_chapter[(prefix, chapter)] = edits
            count_noun_edits += stats["noun_changes"]
            count_tense_edits += stats["tense_changes"]
            count_unmapped += stats["unmapped_verses_left_unchanged"]
            if stats["unmapped_verses_left_unchanged"]:
                unmapped_by_source_prefix[prefix] = (
                    unmapped_by_source_prefix.get(prefix, 0) +
                    stats["unmapped_verses_left_unchanged"]
                )
            count_ambiguous += stats["ambiguous_verses_left_unchanged"]
        if olt_display_faces:
            active_ylt_edits = edits_by_chapter.get((prefix, chapter), {})
            for verse in item["verses"]:
                texts = [
                    active_ylt_edits.get(
                        (verse["reference"], i),
                        span["original_ches_line_text"],
                    )
                    for i, span in enumerate(
                        verse["source_ches_spans_NOT_OLT_TRANSLATION"], 1
                    )
                ]
                _, changed = simplify_sur_faces_for_olt_view(texts)
                count_display_faces += changed
        if len(records) > CHAPTERS_EXPECTED or len(chapters_by_prefix) > PREFIXES_EXPECTED:
            raise CHES015ReaderError("IMPOSSIBLE_SOURCE_ARCHIVE_SIZE")
    if not records:
        raise CHES015ReaderError("EMPTY_PRIVATE_SOURCE_ARCHIVE")
    # Source-directory lexicographic filenames place chapter 10 before 2;
    # read snapshots always display each source-book chapter numerically.
    records.sort(key=lambda item: (item[0], item[1]))
    if len(index_hashes) != 1:
        raise CHES015ReaderError("MIXED_SOURCE_INDEX_SNAPSHOT_HASHES")

    # Missing chapter numbers are observed local gaps only; the last chapters
    # of each book and the upstream 929-file inventory remain unverified.
    missing = sum(
        len(set(range(1, max(numbers) + 1)) - numbers)
        for numbers in chapters_by_prefix.values()
    )
    snapshot = "snapshot-" + digest.hexdigest()[:20]
    if render:
        output = folder.parent / "ches-direct-reader"
        _safe_folder(output)
        final_dir = output / snapshot
        _safe_folder(final_dir)
        for i, (prefix, chapter) in enumerate(records):
            source, _ = _load_private_source(folder, prefix=prefix, chapter=chapter)
            before = (f"{records[i - 1][0]}.{records[i - 1][1]}"
                      if i else None)
            after = (f"{records[i + 1][0]}.{records[i + 1][1]}"
                     if i + 1 < len(records) else None)
            _write_once(
                final_dir / f"{prefix}.{chapter}.html",
                _render_chapter(
                    source, prefix=prefix, chapter=chapter,
                    previous=before, following=after,
                    ylt_edits=edits_by_chapter.get((prefix, chapter)),
                    ylt_mode=use_ylt_authority,
                    olt_display_faces=olt_display_faces,
                ),
            )
        _write_once(
            final_dir / "index.html",
            _render_index(
                records, missing, ylt_mode=use_ylt_authority,
                olt_display_faces=olt_display_faces,
            ),
        )
    return {
        "checkpoint": "CHES-015-DIRECT",
        "mode": ("PRIVATE_OLT_ENGLISH_DISPLAY" if olt_display_faces
                 else "PRIVATE_OFFLINE_ORIGINAL_SOURCE_READER"),
        "observed_chapter_count": len(records),
        "expected_ot_chapter_count": CHAPTERS_EXPECTED,
        "observed_source_prefix_groups": len(chapters_by_prefix),
        "local_internal_numbering_gaps": missing,
        "observed_verse_count": total_verses,
        "observed_source_fragment_count": total_fragments,
        "ylt_1898_public_domain_verse_comparison_used": use_ylt_authority,
        "olt_display_faces_enabled": olt_display_faces,
        "olt_display_sur_faces_to_faces_count": count_display_faces,
        "olt_display_hebrew_lemma_alignment_verified": False,
        "ylt_noun_edit_count": count_noun_edits,
        "ylt_tense_edit_count": count_tense_edits,
        "ylt_verses_unmapped_left_unchanged": count_unmapped,
        "ylt_unmapped_verses_by_source_prefix":
            dict(sorted(unmapped_by_source_prefix.items())),
        "ylt_ambiguous_verses_left_unchanged": count_ambiguous,
        "ylt_verse_context_not_word_alignment_certified": use_ylt_authority,
        "snapshot_id": snapshot,
        "private_html_pages_written_or_reused": len(records) + 1 if render else 0,
        "all_929_39_present_by_count_only":
            len(records) == CHAPTERS_EXPECTED and len(chapters_by_prefix) == PREFIXES_EXPECTED
            and missing == 0,
        "source_fragment_text_linguistically_modified":
            bool(count_noun_edits + count_tense_edits + count_display_faces),
        "original_pdf_bytes_independently_rehashed": False,
        "upstream_source_index_independently_checked": False,
        "independent_english_olt_translation_produced": False,
        "full_corpus_english_translation_reviewed": False,
        "public_distribution_permitted_by_this_tool": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Private offline chapter-reader for untouched CHES source fragments"
    )
    parser.add_argument("--private-root", type=Path,
                        default=Path.home() / ".olt-private" / "ches")
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--build-private-reader", action="store_true")
    parser.add_argument(
        "--use-ylt-authority", action="store_true",
        help="Compare local CHES verse fragments to pinned public-domain YLT "
             "and apply only unique noun/tense decisions offline",
    )
    parser.add_argument(
        "--olt-display-faces", action="store_true",
        help="Create a separate private English OLT display simplifying only "
             "exact 'sur faces' to 'faces'; never rewrite CHES original data",
    )
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Owner-reported private machine-readable use permission required")
    try:
        result = build_private_reader(
            args.private_root,
            render=args.build_private_reader,
            use_ylt_authority=args.use_ylt_authority,
            olt_display_faces=args.olt_display_faces,
        )
    except Exception:
        parser.exit(2, "CHES-015_PRIVATE_SOURCE_READER_VALIDATION_FAILED\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
