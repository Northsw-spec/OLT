"""DANMEK-017 synthetic local 929/39 index membership audit tests.

No third-party HTML or CHES English data is stored in the repository.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.danmek_017_private_source_index_membership import (
    DanMek017Error, audit_private_index_membership, main,
)
from test_ches_015_direct_private_reader import invented_chapter


def invented_full_index() -> bytes:
    # Exactly 929 links across 39 invented source-prefix groups:
    # 55 + 38*23 = 929. These do NOT assert real Biblical chapter counts.
    entries = []
    for prefix, limit in (
        [("gen", 55)] + [(f"f{chr(97 + n // 26)}{chr(97 + n % 26)}", 23) for n in range(38)]
    ):
        for number in range(1, limit + 1):
            entries.append(
                f'<a href="/OnlineInterlinear/OTpdf/{prefix}{number}.pdf">'
                f'Invented chapter {number}</a>'
            )
    assert len(entries) == 929
    return ("<!doctype html><html><body>" +
            "\n".join(entries) + "</body></html>").encode("utf-8")


class TestDanMek017PrivateSourceIndex(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)
        self.index = self.base / "source-index.html"
        self.raw_index = invented_full_index()
        self.index.write_bytes(self.raw_index)
        self.index.chmod(0o600)
        self.source_index_sha = hashlib.sha256(self.raw_index).hexdigest()
        self.add_chapter("gen", 1)
        self.add_chapter("gen", 2)
        self.saved_source = {
            p.name: p.read_bytes() for p in self.source.iterdir()
        }

    def add_chapter(self, prefix: str, number: int) -> Path:
        item = invented_chapter(prefix, number)
        item["source_original_index_sha256"] = self.source_index_sha
        item["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "NOT-TO-BE-PUBLIC-OUTPUT-FAKE"
        item["original_source_pdf_sha256"] = f"{number:064x}"
        path = self.source / f"{prefix}.{number}.json"
        write_private_json(item, path)
        return path

    def test_partial_local_chapters_match_provided_index_without_claiming_full_corpus(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            result = audit_private_index_membership(self.source, self.index)
            again = audit_private_index_membership(self.source, self.index)
        self.assertEqual(result, again)
        self.assertEqual(result["checkpoint"], "DANMEK-017-LOCAL-SOURCE-INDEX-MEMBERSHIP-v1")
        self.assertEqual(result["mode"], "OFFLINE_METADATA_ONLY_READ_ONLY")
        self.assertEqual(result["locally_supplied_index_count"], 929)
        self.assertEqual(result["locally_supplied_index_filename_prefix_count"], 39)
        self.assertEqual(result["private_chapter_json_files_observed"], 2)
        self.assertEqual(result["present_chapter_ids_found_in_supplied_index"], 2)
        self.assertEqual(result["supplied_index_chapter_ids_missing_locally"], 927)
        self.assertFalse(result["all_supplied_index_chapter_ids_present_locally"])
        self.assertTrue(result["all_local_chapter_index_sha_values_match_supplied_index"])
        self.assertFalse(result["supplied_index_originality_independently_authenticated"])
        self.assertFalse(result["source_filename_prefix_is_verified_biblical_book_id"])
        self.assertFalse(result["pdf_source_bytes_independently_rehashed"])
        self.assertFalse(result["english_to_original_hebrew_alignment_verified"])
        self.assertFalse(result["complete_english_bible_translation_owner_approved"])
        self.assertEqual(result["private_files_written"], 0)
        self.assertFalse(result["private_text_exported"])
        self.assertEqual(result["publication_status"], "BLOCKED")
        self.assertEqual(len(result["per_source_filename_prefix"]), 39)
        self.assertEqual(
            result["per_source_filename_prefix"]["gen"],
            {
                "chapter_links_in_supplied_index": 55,
                "private_chapter_json_files_present": 2,
                "index_chapters_missing_locally": 53,
                "all_index_chapters_present_locally": False,
            },
        )
        self.assertEqual(
            result["per_source_filename_prefix"]["fbl"][
                "index_chapters_missing_locally"
            ], 23,
        )
        self.assertEqual(self.index.read_bytes(), self.raw_index)
        self.assertFalse((self.base / "ches-direct-reader").exists())
        self.assertEqual(self.saved_source, {
            p.name: p.read_bytes() for p in self.source.iterdir()
        })
        self.assertNotIn("NOT-TO-BE-PUBLIC", json.dumps(result))
        self.assertNotIn(str(self.source), json.dumps(result))

    def test_refuse_incomplete_source_index_if_explicitly_required(self):
        with self.assertRaisesRegex(DanMek017Error, "LOCAL_SOURCE_INDEX_NOT_FULLY_IMPORTED"):
            audit_private_index_membership(
                self.source, self.index, require_complete=True,
            )
        self.assertEqual(self.index.read_bytes(), self.raw_index)

    def test_refuse_valid_local_chapter_not_present_in_index(self):
        # 56 is outside synthetic gen inventory (1-55).
        path = self.add_chapter("gen", 56)
        with self.assertRaisesRegex(DanMek017Error, "LOCAL_SOURCE_CHAPTER_NOT_IN_SUPPLIED_INDEX"):
            audit_private_index_membership(self.source, self.index)
        self.assertTrue(path.exists())
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_refuse_index_sha_mismatch_even_when_all_chapter_ids_exist(self):
        # The existing CHES reader rejects mixed-index archives first.
        # Give *both* chapter files one internally consistent but wrong SHA
        # so this test reaches DANMEK-017's supplied-index comparison.
        for number in (1, 2):
            item = invented_chapter("gen", number)
            item["source_original_index_sha256"] = "a" * 64
            write_private_json(item, self.source / f"gen.{number}.json")
        with self.assertRaisesRegex(DanMek017Error, "LOCAL_SOURCE_INDEX_SHA_MISMATCH"):
            audit_private_index_membership(self.source, self.index)

    def test_refuse_source_index_outside_private_tree_or_too_broad_permissions(self):
        self.index.chmod(0o644)
        with self.assertRaisesRegex(DanMek017Error, "PRIVATE_SOURCE_INDEX_PERMISSIONS_TOO_BROAD"):
            audit_private_index_membership(self.source, self.index)
        self.index.chmod(0o600)
        public_file = self.base.parent / "index.html"
        public_file.write_bytes(self.raw_index)
        with self.assertRaisesRegex(DanMek017Error, "PRIVATE_SOURCE_INDEX_PATH_UNSAFE"):
            audit_private_index_membership(self.source, public_file)
        with self.assertRaises(DanMek017Error):
            audit_private_index_membership(self.source, self.source / "gen.1.json")
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_source_index_bytes_changed_since_chapter_import_is_rejected(self):
        self.index.write_bytes(self.raw_index.replace(
            b"Invented chapter 1", b"Invented source 1", 1
        ))
        with self.assertRaisesRegex(DanMek017Error, "LOCAL_SOURCE_INDEX_SHA_MISMATCH"):
            audit_private_index_membership(self.source, self.index)

    def test_cli_prints_only_numeric_metadata_with_no_private_write(self):
        with patch("sys.argv", [
            "audit", "--private-root", str(self.source),
            "--source-index", str(self.index),
            "--confirm-machine-readable-use-permission",
        ]), patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["private_chapter_json_files_observed"], 2)
        self.assertNotIn("NOT-TO-BE-PUBLIC", out.getvalue())
        self.assertNotIn(str(self.index), out.getvalue())
        self.assertNotIn(str(self.source), out.getvalue())
        self.assertFalse((self.base / "ches-direct-reader").exists())


if __name__ == "__main__":
    unittest.main()
