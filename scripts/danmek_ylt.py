"""DanMek-002: public-domain YLT (1898) is the authority for optional edits.

Default CHES contextual English remains unchanged. Only an exact source
verse's YLT wording can license a small *candidate* noun/tense substitution,
and only where there is a single English occurrence in both texts. This is
a verse-level heuristic, NOT a certified Hebrew-word crosswalk.

YLT's public-domain text is loaded from a PINNED independent JSON
transcription. Only the explicit --prepare-private-ylt command downloads it.
CHES, the comparison table, and all rendered results stay user-private.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any
from urllib.request import Request, urlopen

from scripts.ches_local_archive_audit import _strict_json_pairs

YLT_SOURCE_URL = (
    "https://raw.githubusercontent.com/malexander-ogletree/ScriptureDesk/"
    "847ee02ed0d2ee19cad3c474b96d757287c3dc0a/bible-ylt.json"
)
YLT_GIT_BLOB_SHA1 = "d98d6b775ae3f95e3e28790c324bbe65c55946ef"
YLT_SOURCE_EDITION = "YLT_1898_PUBLIC_DOMAIN"
YLT_MAX_BYTES = 10_000_000
MAX_VERSE_BYTES = 5_000
# An intentionally narrow editorial policy. A change may run ONLY when the
# specific YLT verse actually uses the proposed target and NOT the old form.
# Do not infer that every 'portal' in CHES means the same Hebrew word as
# an unrelated 'door' elsewhere in that verse.
CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("portal", "door", "MODERN_NOUN"),
    ("portals", "doors", "MODERN_NOUN"),
    ("says", "saith", "TENSE"),
    ("said", "saith", "TENSE"),
)
REVISION = "DANMEK-002-YLT-VERSE-GUARDED-v1"

# The PDF source's filename prefixes are NOT original-language book IDs.
# These familiar labels are permitted only to *look up a parallel English
# Bible verse*, never to certify a Hebrew token, morphology or edition.
# All unknown IDs and known nonmatching verse schemes stay unchanged.
YLT_BOOK_ID_BY_SOURCE_PREFIX = {
    "gen": "gen", "exo": "exo", "lev": "lev", "num": "num",
    "deu": "deu", "jos": "jos", "jdg": "jdg", "rut": "rut",
    "1sa": "1sa", "2sa": "2sa", "1ki": "1ki", "2ki": "2ki",
    "1ch": "1ch", "2ch": "2ch", "ezr": "ezr", "neh": "neh",
    "est": "est", "job": "job", "psa": "psa", "pro": "pro",
    "ecc": "ecc", "sol": "sol", "isa": "isa", "jer": "jer",
    "lam": "lam", "eze": "eze", "dan": "dan", "hos": "hos",
    "joe": "joe", "amo": "amo", "oba": "oba", "jon": "jon",
    "mic": "mic", "nah": "nah", "hab": "hab", "zep": "zep",
    "hag": "hag", "zec": "zec", "mal": "mal",
}


class DanMekYLTError(ValueError):
    """Fixed error reason: never include private CHES/YLT text in logs."""


def git_blob_sha1(value: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(value)).encode("ascii") + b"\\0" + value
    ).hexdigest()


def _public_ylt_file(source_folder: Path) -> Path:
    # Reuse the CHES archive root guard, including .olt-private and mode 0700.
    from scripts.ches_014_offline_english_bridge import _private_archive_root
    try:
        source = _private_archive_root(source_folder)
    except Exception as exc:
        raise DanMekYLTError("PRIVATE_CHES_ARCHIVE_REQUIRED") from exc
    directory = source.parent / "ylt-public-domain"
    if directory.is_symlink():
        raise DanMekYLTError("SYMLINKED_YLT_DIRECTORY")
    if directory.exists() and (
        not directory.is_dir() or stat.S_IMODE(directory.stat().st_mode) & 0o077
    ):
        raise DanMekYLTError("UNSAFE_YLT_DIRECTORY")
    return directory / "bible-ylt.json"


def _validate_ylt_document(raw: bytes, *, original_pin: bool = True) -> dict:
    if (type(raw) is not bytes or not 100 <= len(raw) <= YLT_MAX_BYTES):
        raise DanMekYLTError("INVALID_YLT_SOURCE_SIZE")
    if original_pin and git_blob_sha1(raw) != YLT_GIT_BLOB_SHA1:
        raise DanMekYLTError("YLT_PINNED_ORIGINAL_SOURCE_CHANGED")
    try:
        data = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_strict_json_pairs,
            parse_constant=lambda _v: (_ for _ in ()).throw(
                DanMekYLTError("NONFINITE_YLT_JSON")),
        )
    except (UnicodeError, ValueError, TypeError) as exc:
        raise DanMekYLTError("INVALID_YLT_JSON") from exc
    books = data.get("books") if isinstance(data, dict) else None
    if (data.get("id") != "ylt" or data.get("year") != 1898 or
        not isinstance(books, list) or len(books) != 66):
        raise DanMekYLTError("UNEXPECTED_YLT_EDITION_OR_BOOK_COUNT")
    seen: set[str] = set()
    for book in books:
        if (not isinstance(book, dict) or
            not isinstance(book.get("id"), str) or not
            re.fullmatch(r"[a-z0-9]{2,7}", book["id"]) or
            book["id"] in seen or
            book.get("testament") not in ("OT", "NT") or
            not isinstance(book.get("chapters"), list) or
            not book["chapters"]):
            raise DanMekYLTError("INVALID_YLT_BOOK_SCHEMA")
        seen.add(book["id"])
        for chapter in book["chapters"]:
            if (not isinstance(chapter, list) or not chapter or
                any(type(verse) is not str or
                    not verse.strip() or len(verse) > MAX_VERSE_BYTES
                    for verse in chapter)):
                raise DanMekYLTError("INVALID_YLT_CHAPTER_VERSE_SCHEMA")
    if len([b for b in books if b["testament"] == "OT"]) != 39:
        raise DanMekYLTError("YLT_OLD_TESTAMENT_COVERAGE_MISMATCH")
    if not any(b["id"] == "gen" and b["testament"] == "OT" for b in books):
        raise DanMekYLTError("YLT_GENESIS_MISSING")
    return data


def load_private_ylt(source_folder: Path) -> tuple[dict, str]:
    path = _public_ylt_file(source_folder)
    if (path.is_symlink() or not path.is_file() or
        stat.S_IMODE(path.stat().st_mode) & 0o077 or
        not 100 <= path.stat().st_size <= YLT_MAX_BYTES):
        raise DanMekYLTError("PINNED_PRIVATE_YLT_FILE_MISSING_OR_UNSAFE")
    raw = path.read_bytes()
    data = _validate_ylt_document(raw)
    return data, git_blob_sha1(raw)


def prepare_public_domain_ylt(source_folder: Path, *, fetch=None) -> dict:
    """One-time explicit HTTPS acquisition; never part of offline reading."""
    target = _public_ylt_file(source_folder)
    if fetch is None:
        def fetch():
            request = Request(
                YLT_SOURCE_URL,
                headers={"User-Agent": "OLT-DanMek-pinned-public-domain-YLT/1.0"},
            )
            with urlopen(request, timeout=45) as response:
                if response.geturl() != YLT_SOURCE_URL:
                    raise DanMekYLTError("UNEXPECTED_YLT_REDIRECT")
                return response.read(YLT_MAX_BYTES + 1)
    if target.is_symlink():
        raise DanMekYLTError("SYMLINKED_PRIVATE_YLT_FILE")
    if target.exists():
        load_private_ylt(source_folder)
        return {
            "checkpoint": "DANMEK-002",
            "source_edition": YLT_SOURCE_EDITION,
            "status": "EXISTING_PINNED_PUBLIC_DOMAIN_YLT_UNCHANGED",
            "no_ches_english_text_exported": True,
        }
    raw = fetch()
    _validate_ylt_document(raw)
    directory = target.parent
    directory.mkdir(mode=0o700, exist_ok=True)
    if stat.S_IMODE(directory.stat().st_mode) & 0o077:
        raise DanMekYLTError("UNSAFE_PRIVATE_YLT_DIRECTORY")
    fd, temp = tempfile.mkstemp(dir=directory, prefix=".ylt-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
        os.chmod(temp, 0o600)
        if target.is_symlink() or target.exists():
            raise DanMekYLTError("YLT_OUTPUT_ALREADY_EXISTS")
        os.rename(temp, target)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return {
        "checkpoint": "DANMEK-002",
        "source_edition": YLT_SOURCE_EDITION,
        "status": "PINNED_PUBLIC_DOMAIN_YLT_STORED_PRIVATELY",
        "no_ches_english_text_exported": True,
    }


def _word_matches(text: str, word: str) -> list[re.Match]:
    return list(re.finditer(r"(?<![a-z])" + re.escape(word) + r"(?![a-z])",
                            text, flags=re.IGNORECASE))


def _case_like(old: str, new: str) -> str:
    if old.isupper():
        return new.upper()
    if old[0].isupper():
        return new[0].upper() + new[1:]
    return new


def ylt_verse_for_source(
    ylt: dict, *, prefix: str, chapter: int, verse: int,
) -> str | None:
    if (prefix, chapter) == ("neh", 7):
        # Source PDF prints an unusual primary/alternative 72/73 scheme.
        # Never infer a Hebrew-YLT crosswalk for this chapter.
        return None
    book_id = YLT_BOOK_ID_BY_SOURCE_PREFIX.get(prefix)
    if not book_id or type(chapter) is not int or type(verse) is not int:
        return None
    matches = [book for book in ylt["books"] if book.get("id") == book_id
               and book.get("testament") == "OT"]
    if len(matches) != 1:
        return None
    chapters = matches[0]["chapters"]
    if not 1 <= chapter <= len(chapters):
        return None
    verses = chapters[chapter - 1]
    if not 1 <= verse <= len(verses):
        return None
    return verses[verse - 1]


def propose_ylt_verse_overrides(
    source: dict, *, prefix: str, chapter: int, ylt: dict,
) -> tuple[dict[tuple[str, int], str], dict[str, int]]:
    """Only unambiguous lexical candidates are applied in a single verse.

    One CHES source occurrence and exactly one target form in the matching
    YLT verse are required. All other CHES text remains byte-identical before
    HTML encoding. Hebrew/English word correspondence is still NOT certified.
    """
    suggestions: dict[tuple[str, int], str] = {}
    counts = {"noun_changes": 0, "tense_changes": 0,
              "ambiguous_verses_left_unchanged": 0,
              "unmapped_verses_left_unchanged": 0,
              "verses_without_applicable_ylt_change": 0}
    for row in source["verses"]:
        ref = row["reference"]
        number = int(ref.rsplit(".", 1)[1])
        parallel = ylt_verse_for_source(
            ylt, prefix=prefix, chapter=chapter, verse=number,
        )
        if parallel is None:
            counts["unmapped_verses_left_unchanged"] += 1
            continue
        spans = row["source_ches_spans_NOT_OLT_TRANSLATION"]
        found = []
        for old, new, kind in CANDIDATES:
            occurrences = [
                (i, m) for i, span in enumerate(spans, 1)
                for m in _word_matches(span["original_ches_line_text"], old)
            ]
            if not occurrences:
                continue
            if (len(occurrences) == 1 and
                len(_word_matches(parallel, new)) == 1 and
                not _word_matches(parallel, old)):
                found.append((old, new, kind, occurrences[0]))
        if len(found) > 1:
            # A YLT verse word is not a provable CHES-PDF fragment alignment.
            counts["ambiguous_verses_left_unchanged"] += 1
            continue
        if not found:
            counts["verses_without_applicable_ylt_change"] += 1
            continue
        old, new, kind, (position, match) = found[0]
        original = spans[position-1]["original_ches_line_text"]
        rendering = (original[:match.start()] +
                     _case_like(match.group(0), new) +
                     original[match.end():])
        suggestions[(ref, position)] = rendering
        counts["noun_changes" if kind == "MODERN_NOUN" else "tense_changes"] += 1
    return suggestions, counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Acquire one pinned public-domain YLT verse reference JSON locally"
    )
    parser.add_argument(
        "--private-root", type=Path,
        default=Path.home() / ".olt-private" / "ches",
    )
    parser.add_argument("--prepare-private-ylt", action="store_true", required=True)
    args = parser.parse_args()
    try:
        result = prepare_public_domain_ylt(args.private_root)
    except Exception:
        parser.exit(2, "DANMEK_002_YLT_SOURCE_PREPARATION_FAILED\\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
