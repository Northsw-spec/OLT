"""DANMEK-015 owner-verified reader invariants (synthetic, no CHES text).

This verifies that future development cannot silently change the accepted
DANMEK-014 English presentation. Owner's real local snapshot is PRIVATE and
cannot be reproduced in CI; synthetic invariants are not linguistic proof.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_015_direct_private_reader import build_private_reader, main
from scripts.ches_import import write_private_json
from scripts.danmek_011_owner_order import REVISION as ORDER_REVISION
from scripts.danmek_012_display import REVISION as C_MARKER_REVISION
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek015OwnerVerifiedReaderContract(unittest.TestCase):
    """Pin the accepted opt-in English reader; do not approve whole OT."""

    def test_verified_revisions_are_explicit_not_silent_replacements(self):
        self.assertEqual(
            ORDER_REVISION, "DANMEK-013-AND-LED-OTHER-SUBJECTS-v3",
        )
        self.assertEqual(
            C_MARKER_REVISION,
            "DANMEK-014-HIDE-WHITESPACE-BOUND-LOWERCASE-C-v2",
        )

    def test_private_reading_exact_synthetic_contract_and_source_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / ".olt-private"
            private.mkdir(mode=0o700)
            source_dir = private / "ches"
            source_dir.mkdir(mode=0o700)
            chapter = invented_chapter("gen", 1)

            first = chapter["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
            first[0]["original_ches_line_text"] = "and·he-cameDavidfrom·Town"
            first.append({
                "page": 1, "pdf_x": 17.5, "pdf_y": 6.5,
                "original_ches_line_text": "sur faces",
            })
            second = chapter["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"]
            second[0]["original_ches_line_text"] = (
                "c c and·the·king cc city C c. c·"
            )
            second.append({
                "page": 1, "pdf_x": 17.5, "pdf_y": 11.5,
                "original_ches_line_text": "c",
            })
            chapter["ches_pdf_green_spans"] = 4
            path = source_dir / "gen.1.json"
            write_private_json(chapter, path)
            frozen_source = path.read_bytes()

            with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")):
                original = build_private_reader(source_dir, render=True)
                faces_only = build_private_reader(
                    source_dir, render=True, olt_display_faces=True,
                )
                verified = build_private_reader(
                    source_dir, render=True,
                    olt_display_faces=True,
                    olt_owner_approved_candidates=True,
                )
                repeated = build_private_reader(
                    source_dir, render=True,
                    olt_display_faces=True,
                    olt_owner_approved_candidates=True,
                )

            self.assertEqual(verified["snapshot_id"], repeated["snapshot_id"])
            self.assertNotEqual(original["snapshot_id"], verified["snapshot_id"])
            self.assertNotEqual(faces_only["snapshot_id"], verified["snapshot_id"])
            self.assertEqual(verified["olt_owner_approved_candidate_reorders_applied"], 1)
            self.assertEqual(verified["olt_display_sur_faces_to_faces_count"], 1)
            self.assertEqual(verified["olt_isolated_lowercase_c_fragments_hidden"], 1)
            self.assertEqual(verified["olt_standalone_lowercase_c_letters_hidden"], 5)
            self.assertFalse(verified["olt_owner_candidate_original_language_subject_verified"])
            self.assertFalse(verified["full_corpus_english_translation_reviewed"])
            self.assertFalse(verified["independent_english_olt_translation_produced"])
            self.assertFalse(verified["public_distribution_permitted_by_this_tool"])
            self.assertEqual(verified["publication_status"], "BLOCKED")
            self.assertEqual(path.read_bytes(), frozen_source)

            output = private / "ches-direct-reader"
            original_page = (output / original["snapshot_id"] / "gen.1.html").read_text()
            faces_page = (output / faces_only["snapshot_id"] / "gen.1.html").read_text()
            current_page = (output / verified["snapshot_id"] / "gen.1.html").read_text()
            index = (output / verified["snapshot_id"] / "index.html").read_text()

            self.assertIn("and·he-cameDavidfrom·Town", original_page)
            self.assertIn("sur faces", original_page)
            self.assertIn("c c and·the·king cc city C c. c·", original_page)
            self.assertIn("sur faces", original_page)
            self.assertIn("and·he-cameDavidfrom·Town", faces_page)
            self.assertNotIn("And David — he came", faces_page)
            self.assertIn('>And David — he came from·Town</span>', current_page)
            self.assertIn('>faces</span>', current_page)
            self.assertIn('>and·the·king city C c. c·</span>', current_page)
            self.assertNotIn('>c</span>', current_page)
            self.assertIn("default-src 'none'", current_page)
            self.assertIn('name="robots" content="noindex', current_page)
            self.assertIn("not", index.lower())
            self.assertEqual(path.read_bytes(), frozen_source)

            with patch("sys.argv", [
                "reader", "--private-root", str(source_dir),
                "--confirm-machine-readable-use-permission",
                "--audit-only", "--olt-display-faces",
                "--olt-owner-approved-candidates",
            ]):
                out = io.StringIO()
                with redirect_stdout(out):
                    self.assertEqual(main(), 0)
            safe = json.loads(out.getvalue())
            self.assertEqual(safe["olt_standalone_lowercase_c_letters_hidden"], 5)
            self.assertEqual(safe["olt_owner_approved_candidate_reorders_applied"], 1)
            for private_word in ("David", "Town", "city", "the·king", str(source_dir)):
                self.assertNotIn(private_word, out.getvalue())
            self.assertEqual(path.read_bytes(), frozen_source)


if __name__ == "__main__":
    unittest.main()
