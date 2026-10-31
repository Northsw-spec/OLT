"""CHES-013: private, content-free evidence for deferred PDF verse-layout anomalies.

Only three known verse-layout validation failures are deferrable, and only
when explicitly selected by the owner. Network errors, malformed PDFs,
unexpected parser exceptions and source-index failures remain fatal.
No third-party English text, PDF bytes or source paths are reported.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from scripts.ches_import import write_private_json

_STRUCTURAL_CODES = {
    "Original PDF verse markers are absent, duplicate or out of sequence":
        "ORIGINAL_VERSE_MARKERS_NONCONTIGUOUS_OR_UNREADABLE",
    "Original PDF verse inventory disagrees with required verse count":
        "ORIGINAL_VERSE_INVENTORY_MISMATCH",
    "No CHES green source spans for one or more explicitly marked verses":
        "ORIGINAL_VERSE_WITHOUT_GREEN_SOURCE_SPANS",
    "Nehemiah 7 original primary numbering differs from known source":
        "NEHEMIAH_7_PRIMARY_VERSE_SCHEME_CHANGED",
    "Nehemiah 7 original alternate numbering missing or altered":
        "NEHEMIAH_7_ALTERNATE_VERSE_SCHEME_CHANGED",
    "Nehemiah 7 original black alternative locator mismatch":
        "NEHEMIAH_7_ALTERNATE_LOCATOR_MISMATCH",
}
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_SOURCE = re.compile(r"[A-Za-z0-9_-]{1,20}\Z")


class CHES013ExceptionError(ValueError):
    """The private diagnostic ledger cannot be trusted or safely persisted."""


def structural_code(exc: Exception) -> str | None:
    """Never defer unrecognized parser errors, validation or network failures."""
    if type(exc) is not ValueError:
        return None
    return _STRUCTURAL_CODES.get(str(exc))


def _ledger_file(private_root: Path, prefix: str, chapter: int) -> Path:
    root = private_root.expanduser()
    if not root.is_absolute():
        root = root.resolve()
    if not _SOURCE.fullmatch(prefix) or type(chapter) is not int or chapter < 1:
        raise CHES013ExceptionError("UNTRUSTED_ORIGINAL_SOURCE_CHAPTER")
    private_home = next((part for part in (root, *root.parents)
                         if part.name == ".olt-private"), None)
    if private_home is None or root == private_home:
        raise CHES013ExceptionError("PRIVATE_ROOT_OUTSIDE_PRIVATE_STORAGE")
    return private_home / "ches-013-exceptions" / f"{prefix}.{chapter}.json"


def _existing(path: Path, *, original_source_sha: str) -> dict[str, Any] | None:
    if path.is_symlink():
        raise CHES013ExceptionError("SYMLINKED_EXCEPTION_LEDGER_REFUSED")
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > 5000:
        raise CHES013ExceptionError("UNSAFE_EXCEPTION_LEDGER_FILE")
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CHES013ExceptionError("INVALID_EXCEPTION_LEDGER_JSON") from exc
    if (not isinstance(item, dict) or
        item.get("checkpoint") != "CHES-013" or
        item.get("original_pdf_sha256") != original_source_sha or
        item.get("publication_status") != "BLOCKED" or
        item.get("private_source_text_stored") is not False or
        item.get("english_translation_approved") is not False or
        item.get("state") not in ("UNRESOLVED", "RESOLVED_BY_REIMPORT")):
        raise CHES013ExceptionError("EXISTING_EXCEPTION_LEDGER_CONFLICT")
    return item


def record_structural_exception(
    private_root: Path, *, prefix: str, chapter: int,
    pdf_data: bytes, index_sha256: str, diagnostic_code: str,
) -> None:
    """Atomically record only numeric/source identity metadata, no source text."""
    if (diagnostic_code not in _STRUCTURAL_CODES.values() or
        type(pdf_data) is not bytes or
        not 1000 <= len(pdf_data) <= 30_000_000 or
        not pdf_data.startswith(b"%PDF-") or
        type(index_sha256) is not str or
        _HEX.fullmatch(index_sha256) is None):
        raise CHES013ExceptionError("UNVERIFIED_EXCEPTION_SOURCE_METADATA")
    path = _ledger_file(private_root, prefix, chapter)
    source_sha = hashlib.sha256(pdf_data).hexdigest()
    old = _existing(path, original_source_sha=source_sha)
    if old is not None and old.get("source_index_sha256") != index_sha256:
        raise CHES013ExceptionError("EXCEPTION_INDEX_SNAPSHOT_CHANGED")
    report = {
        "checkpoint": "CHES-013",
        "original_source_prefix": prefix,
        "original_source_chapter": chapter,
        "original_pdf_sha256": source_sha,
        "original_pdf_bytes": len(pdf_data),
        "source_index_sha256": index_sha256,
        "diagnostic_code": diagnostic_code,
        "state": "UNRESOLVED",
        "private_source_text_stored": False,
        "source_pdf_bytes_stored": False,
        "english_translation_approved": False,
        "word_alignment_verified": False,
        "publication_status": "BLOCKED",
    }
    write_private_json(report, path)


def verify_reimport_does_not_conflict_with_private_exception(
    private_root: Path, *, prefix: str, chapter: int, pdf_data: bytes,
) -> None:
    """Preflight before any chapter output is written, fail on changed source."""
    path = _ledger_file(private_root, prefix, chapter)
    if not path.exists() and not path.is_symlink():
        return
    old = _existing(path, original_source_sha=hashlib.sha256(pdf_data).hexdigest())
    if (not isinstance(old, dict) or
        old.get("original_source_prefix") != prefix or
        old.get("original_source_chapter") != chapter or
        old.get("diagnostic_code") not in _STRUCTURAL_CODES.values() or
        old.get("word_alignment_verified") is not False):
        raise CHES013ExceptionError("EXCEPTION_SOURCE_IDENTITY_CHANGED")


def resolve_structural_exception(
    private_root: Path, *, prefix: str, chapter: int, pdf_data: bytes,
) -> None:
    """Resolve only an exception for the same original PDF after it parsed."""
    verify_reimport_does_not_conflict_with_private_exception(
        private_root, prefix=prefix, chapter=chapter, pdf_data=pdf_data
    )
    path = _ledger_file(private_root, prefix, chapter)
    if path.exists():
        old = _existing(path, original_source_sha=hashlib.sha256(pdf_data).hexdigest())
        write_private_json(dict(old, state="RESOLVED_BY_REIMPORT"), path)
