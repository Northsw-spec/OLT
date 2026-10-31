"""CHES-LOCAL-001: invented private data only; no source PDF or licensed CHES text."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts.ches_local_archive_audit import (
    CHESArchiveError, audit_private_archive, _validate_chapter,
)
from scripts.ches_import import NEH7_PRIMARY_VERSES


def fake_chapter(chapter: int = 1, *, prefix: str = "gen", sha_number: int = 1) -> dict:
    ref = f"{prefix}.{chapter}"
    return {
        "book": prefix,
        "chapter": chapter,
        "source_origin_url": (
            f"https://www.scripture4all.org/OnlineInterlinear/OTpdf/"
            f"{prefix}{chapter}.pdf"
        ),
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "independent_grammar_or_sense_approved": False,
        "olt_english_translation_approved": False,
        "owner_attested_machine_readable_permission_no_public_distribution": True,
        "source_chapter_verse_count_independent_oshb_qa": "NOT_DONE",
        "publication_status": "BLOCKED",
        "original_source_pdf_sha256": f"{sha_number:064x}",
        "source_original_index_sha256": "b" * 64,
        "source_pdf_byte_length": 2048,
        "source_pdf_page_count": 1,
        "verses_extracted": 2,
        "ches_pdf_green_spans": 2,
        "verses": [
            {
                "reference": f"{ref}.{number}",
                "explicit_original_pdf_verse_anchor_page": 1,
                "explicit_original_pdf_verse_anchor_y": number * 20.0,
                "source_ches_spans_NOT_OLT_TRANSLATION": [{
                    "page": 1,
                    "pdf_x": 120.0,
                    "pdf_y": number * 20.0 + 10.0,
                    "original_ches_line_text": "SYNTHETIC-UNLICENSED-TEST-ONLY",
                }],
                "english_draft_status": "CHES_SOURCE_ONLY_UNALIGNED",
                "publication_status": "BLOCKED",
            }
            for number in (1, 2)
        ],
    }


class CHESLocalPrivateArchiveAuditTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / ".olt-private" / "ches"
        self.root.mkdir(parents=True, mode=0o700)
        self.root.chmod(0o700)

    def write(self, doc: dict) -> Path:
        filename = f"{doc['book']}.{doc['chapter']}.json"
        path = self.root / filename
        path.write_text(json.dumps(doc), encoding="utf-8")
        path.chmod(0o600)
        return path

    def test_single_private_chapter_is_valid_but_not_929_or_english_approved(self):
        self.write(fake_chapter())
        report = audit_private_archive(self.root)
        self.assertEqual(report["private_source_chapter_json_files_observed"], 1)
        self.assertEqual(report["original_pdf_verse_markers_recorded"], 2)
        self.assertEqual(report["private_ches_green_typography_spans_recorded_not_word_aligned"], 2)
        self.assertFalse(report["full_929_39_coverage_by_count_only"])
        self.assertFalse(report["full_index_membership_independently_verified"])
        self.assertFalse(report["original_pdf_bytes_rehashed_by_this_audit"])
        self.assertFalse(report["hebrew_to_english_word_alignment_verified"])
        self.assertFalse(report["english_olt_translation_owner_approved"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertNotIn("SYNTHETIC-UNLICENSED-TEST-ONLY", json.dumps(report))
        self.assertNotIn(str(self.root), json.dumps(report))
        with self.assertRaises(CHESArchiveError):
            audit_private_archive(self.root, require_929=True)

    def test_numeric_chapter_order_independent_of_lexicographic_filename_order(self):
        for number in range(1, 11):
            self.write(fake_chapter(number, sha_number=number))
        report = audit_private_archive(self.root)
        self.assertEqual(report["private_source_chapter_json_files_observed"], 10)
        self.assertEqual(report["distinct_original_filename_prefixes_observed"], 1)

    def test_nehemiah_seven_original_primary_and_alternate_verse_scheme(self):
        synthetic = fake_chapter(chapter=7, prefix="neh")
        synthetic["verses"] = []
        for number in NEH7_PRIMARY_VERSES:
            row = copy.deepcopy(fake_chapter()["verses"][0])
            row["reference"] = f"neh.7.{number}"
            if number >= 69:
                row["original_pdf_alternate_verse_number_not_oshb_crosswalk"] = number - 1
            synthetic["verses"].append(row)
        synthetic["verses_extracted"] = len(NEH7_PRIMARY_VERSES)
        synthetic["ches_pdf_green_spans"] = len(NEH7_PRIMARY_VERSES)
        self.assertEqual(
            _validate_chapter(synthetic, prefix="neh", chapter=7)[:2], (72, 72)
        )
        for index, wrong in (
            (67, {"reference": "neh.7.68"}),
            (68, {"original_pdf_alternate_verse_number_not_oshb_crosswalk": 70}),
            (71, {"original_pdf_alternate_verse_number_not_oshb_crosswalk": None}),
        ):
            with self.subTest(index=index):
                mutated = copy.deepcopy(synthetic)
                mutated["verses"][index].update(wrong)
                with self.assertRaises(CHESArchiveError):
                    _validate_chapter(mutated, prefix="neh", chapter=7)
        missing = copy.deepcopy(synthetic)
        missing["verses"].pop()
        missing["verses_extracted"] -= 1
        missing["ches_pdf_green_spans"] -= 1
        with self.assertRaises(CHESArchiveError):
            _validate_chapter(missing, prefix="neh", chapter=7)

    def test_gap_in_source_chapter_numbers_must_not_be_accepted(self):
        self.write(fake_chapter(1))
        self.write(fake_chapter(3, sha_number=3))
        with self.assertRaisesRegex(CHESArchiveError, "MISSING_DUPLICATE"):
            audit_private_archive(self.root)

    def test_mixed_original_index_snapshots_are_rejected(self):
        self.write(fake_chapter(1))
        other = fake_chapter(2, sha_number=2)
        other["source_original_index_sha256"] = "a" * 64
        self.write(other)
        with self.assertRaisesRegex(CHESArchiveError, "MIXED_ORIGINAL"):
            audit_private_archive(self.root)

    def test_duplicate_original_pdf_digest_is_rejected(self):
        self.write(fake_chapter(1))
        self.write(fake_chapter(2))
        with self.assertRaisesRegex(CHESArchiveError, "DUPLICATE_ORIGINAL"):
            audit_private_archive(self.root)

    def test_hostile_approval_reference_geometry_and_span_tampering_fail_closed(self):
        baseline = fake_chapter()
        variants = [
            ("publication_status", "PUBLIC"),
            ("full_source_text_in_public_git_permitted", True),
            ("alignment_with_oshb_words_verified", True),
            ("olt_english_translation_approved", True),
            ("source_origin_url", "https://evil.invalid/untrusted.pdf"),
            ("original_source_pdf_sha256", "not-a-digest"),
            ("ches_pdf_green_spans", 3),
            ("verses_extracted", 3),
            ("owner_attested_machine_readable_permission_no_public_distribution", False),
            ("source_chapter_verse_count_independent_oshb_qa", "DONE"),
            ("chapter", True),
        ]
        for key, value in variants:
            with self.subTest(field=key):
                variant = copy.deepcopy(baseline)
                variant[key] = value
                self.write(variant)
                with self.assertRaises(CHESArchiveError):
                    audit_private_archive(self.root)
        for key, value in [
            ("reference", "gen.1.99"),
            ("publication_status", "PUBLIC"),
            ("english_draft_status", "APPROVED"),
            ("explicit_original_pdf_verse_anchor_y", float("nan")),
            ("source_ches_spans_NOT_OLT_TRANSLATION", []),
        ]:
            with self.subTest(field=key):
                variant = copy.deepcopy(baseline)
                variant["verses"][0][key] = value
                self.write(variant)
                with self.assertRaises(CHESArchiveError):
                    audit_private_archive(self.root)

    def test_private_chapter_permissions_symlink_and_unexpected_file_rejected(self):
        path = self.write(fake_chapter())
        path.chmod(0o644)
        with self.assertRaisesRegex(CHESArchiveError, "PERMISSIONS"):
            audit_private_archive(self.root)
        path.chmod(0o600)
        unexpected = self.root / "unexpected.txt"
        unexpected.write_text("synthetic")
        with self.assertRaisesRegex(CHESArchiveError, "UNKNOWN_PRIVATE"):
            audit_private_archive(self.root)
        unexpected.unlink()
        link = self.root / "gen.2.json"
        os.symlink(path, link)
        with self.assertRaisesRegex(CHESArchiveError, "SYMLINKED"):
            audit_private_archive(self.root)

    def test_non_private_directory_and_broad_directory_permissions_rejected(self):
        private_path = self.write(fake_chapter())
        self.root.chmod(0o755)
        with self.assertRaisesRegex(CHESArchiveError, "PERMISSIONS"):
            audit_private_archive(self.root)
        self.root.chmod(0o700)
        public_dir = self.root.parent.parent / "public"
        public_dir.mkdir()
        (public_dir / "gen.1.json").write_bytes(private_path.read_bytes())
        with self.assertRaisesRegex(CHESArchiveError, "PRIVATE_ARCHIVE"):
            audit_private_archive(public_dir)

    def test_duplicate_json_keys_and_nonfinite_json_values_rejected(self):
        path = self.write(fake_chapter())
        path.write_text('{"book":"gen","book":"gen"}', encoding="utf-8")
        path.chmod(0o600)
        with self.assertRaisesRegex(CHESArchiveError, "DUPLICATE_JSON"):
            audit_private_archive(self.root)
        path.write_text('{"chapter":NaN}', encoding="utf-8")
        path.chmod(0o600)
        with self.assertRaisesRegex(CHESArchiveError, "INVALID_NONFINITE"):
            audit_private_archive(self.root)

    def test_source_text_never_in_error_message(self):
        fake = fake_chapter()
        fake["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "NOT-FOR-LOGS-SYNTHETIC"
        fake["verses"][0]["reference"] = "WRONG"
        self.write(fake)
        with self.assertRaises(CHESArchiveError) as caught:
            audit_private_archive(self.root)
        self.assertNotIn("NOT-FOR-LOGS-SYNTHETIC", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
