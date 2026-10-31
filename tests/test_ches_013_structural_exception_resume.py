"""CHES-013 synthetic-only fail-closed incremental import tests.

No actual licensed source PDF or source English text is checked into Git.
"""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from scripts.ches_013_structural_exceptions import (
    CHES013ExceptionError, structural_code,
)
from scripts.ches_index import parse_index
from scripts.ches_private_batch import private_batch

FAKE_INDEX = parse_index(b"""
<a href="OTpdf/gen1.pdf">One</a>
<a href="OTpdf/gen2.pdf">Two</a>
<a href="OTpdf/gen3.pdf">Three</a>
""")
BAD_MARKERS = "Original PDF verse markers are absent, duplicate or out of sequence"
ARTIFICIAL_ONLY = "SYNTHETIC-ENGLISH-NOT-COPIED"


def fake_pdf(url: str, _limit: int) -> bytes:
    basename = url.split("/")[-1].encode("ascii")
    return (b"%PDF-" + basename).ljust(1300, b"X")


def fake_source(pdf: bytes, prefix: str, number: int) -> dict:
    if number == 2:
        raise ValueError(BAD_MARKERS)
    return {
        "book": prefix,
        "chapter": number,
        "source_origin_url": FAKE_INDEX["chapter_links"][number-1]["original_pdf_url"],
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "original_source_pdf_sha256": hashlib.sha256(pdf).hexdigest(),
        "source_pdf_byte_length": len(pdf),
        "source_pdf_page_count": 1,
        "verses_extracted": 1,
        "ches_pdf_green_spans": 1,
        "verses": [
            {
                "reference": f"{prefix}.{number}.1",
                "source_ches_spans_NOT_OLT_TRANSLATION": [ARTIFICIAL_ONLY],
                "publication_status": "BLOCKED",
            }
        ],
        "publication_status": "BLOCKED",
    }


class TestCHES013PrivateDeferredStructuralErrors(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.private = Path(scratch.name) / ".olt-private" / "ches"
        self.exceptions = self.private.parent / "ches-013-exceptions"

    def execute(self, *, continue_on_structural_error: bool, generator=fake_source,
                fetch=fake_pdf, limit: int = 3):
        printed = io.StringIO()
        with patch("scripts.ches_private_batch.import_private_pdf", generator), patch(
            "scripts.ches_private_batch.time.sleep"
        ) as sleeper, redirect_stdout(printed):
            result = private_batch(
                FAKE_INDEX, self.private, limit=limit, fetch=fetch,
                continue_on_structural_error=continue_on_structural_error,
            )
        return result, printed.getvalue(), sleeper

    def test_default_mode_still_stops_and_never_creates_exception_ledger(self):
        with self.assertRaisesRegex(ValueError, "verse markers"):
            self.execute(continue_on_structural_error=False)
        self.assertTrue((self.private / "gen.1.json").is_file())
        self.assertFalse((self.private / "gen.2.json").exists())
        self.assertFalse((self.private / "gen.3.json").exists())
        self.assertFalse(self.exceptions.exists())

    def test_explicit_mode_defers_only_known_structural_error_and_marks_incomplete(self):
        report, output, sleeper = self.execute(continue_on_structural_error=True)
        self.assertEqual(report["newly_imported_to_private_storage"], 2)
        self.assertEqual(report["deferred_structurally_unreadable_source_chapters"], 1)
        self.assertEqual(report["source_pdf_fetch_attempts"], 3)
        self.assertEqual(report["selected_chapter_files_present_after_run"], 2)
        self.assertFalse(report["all_selected_chapter_files_present_by_count_only"])
        self.assertEqual(report["import_run_status"], "INCOMPLETE_UNRESOLVED_STRUCTURAL_EXCEPTIONS")
        self.assertFalse(report["whole_old_testament_chapter_coverage_qa_complete"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertEqual(sleeper.call_count, 2)
        self.assertFalse((self.private / "gen.2.json").exists())
        self.assertTrue((self.private / "gen.3.json").exists())
        ledger = self.exceptions / "gen.2.json"
        record = json.loads(ledger.read_text(encoding="utf-8"))
        self.assertEqual(ledger.stat().st_mode & 0o777, 0o600)
        self.assertEqual(ledger.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(record["state"], "UNRESOLVED")
        self.assertEqual(record["diagnostic_code"], "ORIGINAL_VERSE_MARKERS_NONCONTIGUOUS_OR_UNREADABLE")
        self.assertEqual(record["original_pdf_sha256"], hashlib.sha256(
            fake_pdf("https://x/gen2.pdf", 3000)).hexdigest())
        self.assertFalse(record["private_source_text_stored"])
        self.assertFalse(record["source_pdf_bytes_stored"])
        self.assertEqual(record["publication_status"], "BLOCKED")
        self.assertNotIn(ARTIFICIAL_ONLY, json.dumps(record) + output + json.dumps(report))
        self.assertNotIn(str(self.private), json.dumps(record) + output + json.dumps(report))
        self.assertEqual(len(list(self.private.glob("*.json"))), 2)

    def test_repeated_run_retries_only_missing_chapter_and_can_resolve_same_pdf(self):
        self.execute(continue_on_structural_error=True)
        second, _, _ = self.execute(continue_on_structural_error=True)
        self.assertEqual(second["existing_private_chapters_validated_for_resume_only"], 2)
        self.assertEqual(second["source_pdf_fetch_attempts"], 1)
        self.assertEqual(second["deferred_structurally_unreadable_source_chapters"], 1)
        def now_fixed(pdf: bytes, prefix: str, chapter: int) -> dict:
            if chapter == 2:
                result = fake_source(pdf, prefix, 1)
                result["chapter"] = 2
                result["source_origin_url"] = FAKE_INDEX["chapter_links"][1]["original_pdf_url"]
                result["verses"][0]["reference"] = "gen.2.1"
                return result
            return fake_source(pdf, prefix, chapter)
        final, _, _ = self.execute(
            continue_on_structural_error=True, generator=now_fixed
        )
        self.assertEqual(final["newly_imported_to_private_storage"], 1)
        self.assertEqual(final["existing_private_chapters_validated_for_resume_only"], 2)
        self.assertEqual(final["deferred_structurally_unreadable_source_chapters"], 0)
        self.assertTrue(final["all_selected_chapter_files_present_by_count_only"])
        record = json.loads((self.exceptions / "gen.2.json").read_text(encoding="utf-8"))
        self.assertEqual(record["state"], "RESOLVED_BY_REIMPORT")
        self.assertFalse(record["english_translation_approved"])

    def test_unknown_parser_errors_and_network_errors_remain_fatal(self):
        for error in (
            ValueError("Unexpected PDF source ink color"),
            ValueError("Invalid or oversized original chapter PDF"),
            RuntimeError("parser programming error"),
            URLError("Network is unreachable"),
        ):
            with self.subTest(exception=type(error).__name__):
                def broken(_pdf, _prefix, chapter):
                    if chapter == 2:
                        raise error
                    return fake_source(_pdf, _prefix, chapter)
                with self.assertRaises(type(error)):
                    self.execute(continue_on_structural_error=True, generator=broken)
                self.assertFalse((self.exceptions / "gen.2.json").exists())

    def test_source_hash_change_is_not_silently_accepted_on_retry(self):
        self.execute(continue_on_structural_error=True)
        original = (self.exceptions / "gen.2.json").read_bytes()
        def modified_pdf(url, size):
            return fake_pdf(url, size) + b"M"
        with self.assertRaises(CHES013ExceptionError):
            self.execute(continue_on_structural_error=True, fetch=modified_pdf)
        self.assertEqual(original, (self.exceptions / "gen.2.json").read_bytes())

    def test_different_original_pdf_cannot_create_recovered_chapter_file(self):
        self.execute(continue_on_structural_error=True)
        def changed_source(url, limit):
            data = fake_pdf(url, limit)
            return data + b"X" if url.endswith("/gen2.pdf") else data
        def fixed_after_upstream_change(pdf, prefix, chapter):
            if chapter == 2:
                item = fake_source(pdf, prefix, 1)
                item["chapter"] = 2
                item["verses"][0]["reference"] = "gen.2.1"
                return item
            return fake_source(pdf, prefix, chapter)
        with self.assertRaises(CHES013ExceptionError):
            self.execute(continue_on_structural_error=True,
                         fetch=changed_source, generator=fixed_after_upstream_change)
        self.assertFalse((self.private / "gen.2.json").exists())
        self.assertEqual(
            json.loads((self.exceptions / "gen.2.json").read_text(encoding="utf-8"))["state"],
            "UNRESOLVED"
        )

    def test_structural_classifier_has_explicit_allowlist_not_generic_valueerror(self):
        self.assertEqual(structural_code(ValueError(BAD_MARKERS)),
                         "ORIGINAL_VERSE_MARKERS_NONCONTIGUOUS_OR_UNREADABLE")
        self.assertIsNone(structural_code(ValueError("unknown layout error")))
        self.assertIsNone(structural_code(RuntimeError(BAD_MARKERS)))

    def test_symlinked_metadata_ledger_does_not_get_overwritten(self):
        self.exceptions.mkdir(parents=True)
        arbitrary = self.exceptions / "arbitrary.txt"
        arbitrary.write_text("UNTOUCHED", encoding="utf-8")
        (self.exceptions / "gen.2.json").symlink_to(arbitrary)
        with self.assertRaises(CHES013ExceptionError):
            self.execute(continue_on_structural_error=True)
        self.assertEqual(arbitrary.read_text(encoding="utf-8"), "UNTOUCHED")

    def test_partial_archive_is_never_mislabeled_complete(self):
        result, _, _ = self.execute(continue_on_structural_error=True, limit=2)
        self.assertEqual(result["selected_chapter_count"], 2)
        self.assertFalse(result["all_selected_chapter_files_present_by_count_only"])
        self.assertFalse(result["original_source_to_oshb_alignment_certified"])


if __name__ == "__main__":
    unittest.main()
