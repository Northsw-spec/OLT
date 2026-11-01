"""DANMEK-020 regression tests: invented English and fake Hebrew/Aramaic only."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.ches_015_direct_private_reader import build_private_reader
from scripts.danmek_020_private_ambiguous_order_review import (
    DanMek020Error, SOURCE_BOOK_CANDIDATES,
    build_ambiguous_order_queue, main,
)
from test_ches_015_direct_private_reader import invented_chapter


def fake_original_word(reference: str, *, language: str = "H") -> dict:
    return {
        "reference": reference,
        "ordinal": 1,
        "source_id": "FAKE_WORD_ID_" + reference,
        "hebrew": "סִימָן" if language == "H" else "סִמָן",
        "morph_raw": language + "Vqp3ms",
        "lemma_raw": "01234",
        "source_status": "IMPORTED_UNREVIEWED",
    }


class TestDanMek020AmbiguousOrderQueue(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / ".olt-private"
        self.root.mkdir(mode=0o700)
        self.folder = self.root / "ches"
        self.folder.mkdir(mode=0o700)
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker she-is-building Leader"
        gen["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "Nothing to reorder"
        exo = invented_chapter("exo", 1, source_sha="f" * 64)
        exo["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "No candidate here"
        exo["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker she-is-building Leader"
        write_private_json(gen, self.folder / "gen.1.json")
        write_private_json(exo, self.folder / "exo.1.json")
        self.saved_bytes = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        self.fake_registry = {
            "ot": {"books": [{"book": b} for b in SOURCE_BOOK_CANDIDATES.values()]}
        }
        self.original = {
            "Gen": {"book": "Gen", "verses": [
                {"reference": "Gen.1.1", "words": [
                    fake_original_word("Gen.1.1", language="H"),
                ]},
            ]},
            "Exod": {"book": "Exod", "verses": [
                {"reference": "Exod.1.1", "words": [
                    fake_original_word("Exod.1.1", language="A"),
                ]},
            ]},
        }
        self.reader_before = build_private_reader(
            self.folder, render=False, olt_display_faces=True,
            olt_owner_approved_candidates=True,
        )
        self.assertEqual(
            self.reader_before["olt_owner_candidate_ambiguous_verses_unchanged"], 2,
        )

    def run_queue(self, *, write_private: bool = False, require_311: bool = False):
        with (
            patch("scripts.danmek_020_private_ambiguous_order_review.read_provenance",
                  return_value=self.fake_registry),
            patch("scripts.danmek_020_private_ambiguous_order_review.load_ot_book",
                  side_effect=lambda book, registry: self.original[book]),
            patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")),
        ):
            return build_ambiguous_order_queue(
                self.folder, write_private=write_private, require_311=require_311,
            )

    def test_read_only_summary_counts_and_no_source_text_or_paths(self):
        output = self.run_queue()
        self.assertEqual(output["ambiguous_english_verses_queued"], 2)
        self.assertEqual(output["source_verses_seen"], 4)
        self.assertEqual(
            output["original_source_same_reference_candidates_unreviewed"], 1,
        )
        self.assertEqual(output["original_source_reference_missing"], 1)
        self.assertEqual(
            output["by_source_prefix_ambiguous_count"], {"exo": 1, "gen": 1},
        )
        self.assertEqual(
            output["private_output_status"], "AUDIT_ONLY_NO_PRIVATE_QUEUE_WRITTEN",
        )
        self.assertFalse(output["source_book_mapping_independently_verified"])
        self.assertFalse(output["original_source_word_alignment_verified"])
        self.assertFalse(output["original_language_subject_verified"])
        self.assertEqual(output["english_reorders_applied"], 0)
        self.assertFalse(output["owner_verified_english_html_changed"])
        self.assertEqual(output["publication_status"], "BLOCKED")
        self.assertEqual(output["reader_snapshot_id"], self.reader_before["snapshot_id"])
        self.assertEqual(
            self.reader_before,
            build_private_reader(
                self.folder, render=False, olt_display_faces=True,
                olt_owner_approved_candidates=True,
            ),
        )
        self.assertEqual(
            self.saved_bytes, {p.name: p.read_bytes() for p in self.folder.iterdir()},
        )
        self.assertFalse((self.root / "ches-order-review").exists())
        self.assertFalse((self.root / "ches-direct-reader").exists())
        safe = json.dumps(output)
        for forbidden in ("Worker", "Leader", "סִימָן", str(self.folder)):
            self.assertNotIn(forbidden, safe)

    def test_opt_in_private_queue_contains_review_only_evidence_immutable(self):
        out = self.run_queue(write_private=True)
        self.assertEqual(out["private_output_status"], "NEW_PRIVATE_QUEUE")
        folder = self.root / "ches-order-review"
        self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        files = list(folder.iterdir())
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].stat().st_mode & 0o777, 0o600)
        raw = files[0].read_bytes()
        body = json.loads(raw)
        self.assertEqual(body["total_ambiguous_cases"], 2)
        self.assertFalse(body["source_book_prefix_crosswalk_verified"])
        self.assertFalse(body["hebrew_aramaic_word_alignment_verified"])
        self.assertEqual(body["approved_english_reorders_from_queue"], 0)
        self.assertEqual(body["publication_status"], "BLOCKED")
        self.assertEqual(len(body["cases"]), 2)
        self.assertIn(
            "he-is-making Worker she-is-building Leader", raw.decode("utf-8")
        )
        gen = next(row for row in body["cases"]
                   if row["source_ches_verse_reference"] == "gen.1.1")
        self.assertFalse(gen["reorder_permitted"])
        self.assertFalse(gen["word_alignment_verified"])
        self.assertEqual(gen["human_original_language_subject_review"], "NOT_DONE")
        original = gen["original_source_verse_candidate"]
        self.assertEqual(
            original["status"],
            "SAME_REFERENCE_ORIGINAL_SOURCE_CANDIDATE_UNREVIEWED",
        )
        self.assertEqual(original["candidate_source_ref"], "Gen.1.1")
        self.assertFalse(original["candidate_book_mapping_verified"])
        self.assertFalse(original["original_to_ches_word_alignment_verified"])
        self.assertEqual(
            original["original_source_words_unaligned"][0]["source_language_candidate"],
            "hbo",
        )
        self.assertIn("סִימָן", raw.decode("utf-8"))
        exo = next(row for row in body["cases"]
                   if row["source_ches_verse_reference"] == "exo.1.2")
        self.assertEqual(
            exo["original_source_verse_candidate"]["status"],
            "NO_SAME_REFERENCE_ORIGINAL_VERSE_FOUND",
        )
        self.assertEqual(
            exo["original_source_verse_candidate"]["original_source_words_unaligned"],
            [],
        )
        same = self.run_queue(write_private=True)
        self.assertEqual(
            same["private_output_status"], "EXISTING_IDENTICAL_PRIVATE_QUEUE",
        )
        self.assertEqual(files[0].read_bytes(), raw)
        self.assertEqual(self.saved_bytes, {
            p.name: p.read_bytes() for p in self.folder.iterdir()
        })
        self.assertFalse((self.root / "ches-direct-reader").exists())

    def test_require_311_blocks_partial_synthetic_archive_without_writes(self):
        with self.assertRaisesRegex(DanMek020Error, "OWNER_REPORTED_311_COUNT_MISMATCH"):
            self.run_queue(write_private=True, require_311=True)
        self.assertFalse((self.root / "ches-order-review").exists())

    def test_invalid_original_token_cannot_be_silently_certified(self):
        self.original["Gen"]["verses"][0]["words"][0]["ordinal"] = 2
        with self.assertRaisesRegex(DanMek020Error, "MALFORMED_ORIGINAL_SOURCE_TOKEN"):
            self.run_queue(write_private=True)
        self.assertFalse((self.root / "ches-order-review").exists())

    def test_rejects_proposed_source_mapping_registry_drift(self):
        self.fake_registry["ot"]["books"].pop()
        with self.assertRaisesRegex(DanMek020Error, "SOURCE_BOOK_CANDIDATE_REGISTRY_CHANGED"):
            self.run_queue(write_private=True)
        self.assertFalse((self.root / "ches-order-review").exists())

    def test_private_read_only_cli_prints_metadata_without_words(self):
        with (
            patch("scripts.danmek_020_private_ambiguous_order_review.read_provenance",
                  return_value=self.fake_registry),
            patch("scripts.danmek_020_private_ambiguous_order_review.load_ot_book",
                  side_effect=lambda book, registry: self.original[book]),
            patch("sys.argv", [
                "danmek-020", "--private-root", str(self.folder),
                "--confirm-machine-readable-use-permission",
            ]),
            patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK")),
        ):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        result = json.loads(out.getvalue())
        self.assertEqual(result["ambiguous_english_verses_queued"], 2)
        self.assertEqual(
            result["private_output_status"], "AUDIT_ONLY_NO_PRIVATE_QUEUE_WRITTEN",
        )
        for forbidden in ("Worker", "Leader", str(self.folder), "סִימָן"):
            self.assertNotIn(forbidden, out.getvalue())
        self.assertFalse((self.root / "ches-order-review").exists())

    def test_refuses_bad_directory_and_never_overwrites_existing_queue(self):
        existing = self.root / "ches-order-review"
        existing.mkdir(mode=0o700)
        existing.chmod(0o755)
        with self.assertRaisesRegex(DanMek020Error, "PRIVATE_REVIEW_QUEUE_DIRECTORY_UNSAFE"):
            self.run_queue(write_private=True)
        existing.chmod(0o700)
        first = self.run_queue(write_private=True)
        self.assertEqual(first["private_output_status"], "NEW_PRIVATE_QUEUE")
        file = next(existing.iterdir())
        old = file.read_bytes()
        file.write_bytes(b"EXISTING_OWNER_NOTES_DO_NOT_OVERWRITE")
        with self.assertRaisesRegex(DanMek020Error, "PRIVATE_REVIEW_QUEUE_DIFFERENT_NO_OVERWRITE"):
            self.run_queue(write_private=True)
        self.assertEqual(file.read_bytes(), b"EXISTING_OWNER_NOTES_DO_NOT_OVERWRITE")
        self.assertNotEqual(file.read_bytes(), old)

    def test_malformed_source_raises_only_fixed_diagnostic(self):
        file = self.folder / "gen.1.json"
        file.write_text("PRIVATE-DO-NOT-PRINT", encoding="utf-8")
        with self.assertRaises(DanMek020Error) as caught:
            self.run_queue(write_private=True)
        self.assertNotIn("PRIVATE-DO-NOT-PRINT", str(caught.exception))
        self.assertFalse((self.root / "ches-order-review").exists())


if __name__ == "__main__":
    unittest.main()
