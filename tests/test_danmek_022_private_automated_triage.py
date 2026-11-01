"""DANMEK-022 synthetic, private-only triage regression and negative tests."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_import import write_private_json
from scripts.danmek_020_private_ambiguous_order_review import (
    SOURCE_BOOK_CANDIDATES, build_ambiguous_order_queue,
)
from scripts.danmek_022_private_automated_triage import (
    DanMek022Error, triage_private_ambiguities, main,
)
from test_ches_015_direct_private_reader import invented_chapter


SYNTHETIC_ENGLISH = 'he-is-making Worker she-is-building Leader <script>alert(1)</script>'


def original_word(reference: str, *, morph: str = "HVqp3ms") -> dict:
    return {
        "reference": reference, "ordinal": 1,
        "source_id": "SYNTHETIC_" + reference,
        "hebrew": 'סִימָן<img src=x onerror=alert(1)>',
        "morph_raw": morph,
        "lemma_raw": "01234",
        "source_status": "IMPORTED_UNREVIEWED",
    }


class TestDanMek022PrivateAutomatedTriage(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / ".olt-private"
        self.root.mkdir(mode=0o700)
        self.archive = self.root / "ches"
        self.archive.mkdir(mode=0o700)
        gen = invented_chapter("gen", 1)
        gen["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = SYNTHETIC_ENGLISH
        exo = invented_chapter("exo", 1, source_sha="f" * 64)
        exo["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker she-is-building Leader"
        write_private_json(gen, self.archive / "gen.1.json")
        write_private_json(exo, self.archive / "exo.1.json")
        self.original_files = {
            p.name: p.read_bytes() for p in self.archive.iterdir()
        }
        self.provenance = {"ot": {"books": [
            {"book": b} for b in SOURCE_BOOK_CANDIDATES.values()
        ]}}
        self.books = {
            "Gen": {"book": "Gen", "verses": [
                {"reference": "Gen.1.1", "words": [
                    original_word("Gen.1.1"),
                ]},
            ]},
            "Exod": {"book": "Exod", "verses": [
                {"reference": "Exod.1.1", "words": [
                    original_word("Exod.1.1", morph="AVqp3ms"),
                ]},
            ]},
        }
        with self.mock_originals():
            info = build_ambiguous_order_queue(self.archive, write_private=True)
        self.assertEqual(info["ambiguous_english_verses_queued"], 2)
        self.assertEqual(info["private_output_status"], "NEW_PRIVATE_QUEUE")
        self.review_folder = self.root / "ches-order-review"
        self.queue_path = next(self.review_folder.iterdir())
        self.original_queue_bytes = self.queue_path.read_bytes()

    def mock_originals(self):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(patch(
            "scripts.danmek_020_private_ambiguous_order_review.read_provenance",
            return_value=self.provenance,
        ))
        stack.enter_context(patch(
            "scripts.danmek_020_private_ambiguous_order_review.load_ot_book",
            side_effect=lambda book, registry: self.books[book],
        ))
        stack.enter_context(patch(
            "scripts.danmek_022_private_automated_triage.read_provenance",
            return_value=self.provenance,
        ))
        stack.enter_context(patch(
            "scripts.danmek_022_private_automated_triage.load_ot_book",
            side_effect=lambda book, registry: self.books[book],
        ))
        stack.enter_context(patch(
            "urllib.request.urlopen",
            side_effect=AssertionError("NO_NETWORK"),
        ))
        return stack

    def triage(self, **opts):
        with self.mock_originals():
            return triage_private_ambiguities(self.archive, **opts)

    def test_metadata_only_rechecks_source_immutability_and_morph_hints(self):
        a = self.triage()
        b = self.triage()
        self.assertEqual(a, b)
        self.assertEqual(a["checkpoint"], "DANMEK-022-PRIVATE-AUTOMATED-REVIEW-v1")
        self.assertEqual(a["ambiguous_cases_rechecked"], 2)
        self.assertEqual(a["source_reference_candidates_present_unaligned"], 1)
        self.assertEqual(a["missing_original_reference_cases"], 1)
        self.assertEqual(a["raw_original_verb_morphology_tag_hints_unreviewed"], 1)
        self.assertEqual(a["by_source_prefix_ambiguous_count"], {"exo": 1, "gen": 1})
        self.assertFalse(a["candidate_original_book_mapping_verified"])
        self.assertFalse(a["original_word_subject_alignment_verified"])
        self.assertEqual(a["grammatical_subjects_verified"], 0)
        self.assertEqual(a["english_editorial_changes_applied"], 0)
        self.assertEqual(a["private_review_html_status"], "AUDIT_ONLY_NO_HTML_WRITTEN")
        self.assertTrue(a["all_cases_still_require_evidence_review"])
        self.assertEqual(a["publication_status"], "BLOCKED")
        self.assertFalse(a["private_text_printed"])
        self.assertEqual(
            self.original_files, {
                p.name: p.read_bytes() for p in self.archive.iterdir()
            },
        )
        self.assertEqual(self.queue_path.read_bytes(), self.original_queue_bytes)
        self.assertEqual(list(self.review_folder.iterdir()), [self.queue_path])
        for forbidden in ("Worker", "Leader", "סִימָן", str(self.archive)):
            self.assertNotIn(forbidden, json.dumps(a))

    def test_private_html_is_escaped_csp_disabled_scripts_and_write_once(self):
        report = self.triage(write_private_html=True)
        self.assertEqual(report["private_review_html_status"], "NEW_PRIVATE_QUEUE")
        pages = list(self.review_folder.glob("danmek-022-*.html"))
        self.assertEqual(len(pages), 1)
        path = pages[0]
        self.assertEqual(self.review_folder.stat().st_mode & 0o777, 0o700)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        content = path.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)
        self.assertIn("noindex,nofollow,noarchive", content)
        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
        self.assertNotIn("<img src=x onerror=alert(1)>", content)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", content)
        self.assertIn("Worker", content)
        self.assertIn("UNREVIEWED", content)
        self.assertIn("No safe alignment", content.lower().replace("no safe", "No safe"))
        self.assertIn("reorder_permitted=false", content)
        self.assertIn("word_alignment_verified=false", content)
        self.assertIn("Publication BLOCKED", content)
        self.assertNotIn("<script ", content)
        self.assertNotIn("https://", content)
        first_bytes = path.read_bytes()
        same = self.triage(write_private_html=True)
        self.assertEqual(same["private_review_html_status"], "EXISTING_IDENTICAL_PRIVATE_QUEUE")
        self.assertEqual(path.read_bytes(), first_bytes)
        self.assertEqual(self.original_files, {
            p.name: p.read_bytes() for p in self.archive.iterdir()
        })

    def test_source_english_tampering_blocks_render_without_new_html(self):
        changed = invented_chapter("gen", 1)
        changed["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "he-is-making Worker she-is-building Leader CHANGED"
        write_private_json(changed, self.archive / "gen.1.json")
        with self.assertRaises(DanMek022Error):
            self.triage(write_private_html=True)
        self.assertEqual(list(self.review_folder.iterdir()), [self.queue_path])

    def test_changed_original_token_cannot_silently_pass(self):
        self.books["Gen"]["verses"][0]["words"][0]["hebrew"] = "DIFFERENT"
        with self.assertRaisesRegex(DanMek022Error, "ORIGINAL_SOURCE_CANDIDATE_CHANGED"):
            self.triage(write_private_html=True)
        self.assertFalse(list(self.review_folder.glob("danmek-022-*.html")))

    def test_queue_byte_tampering_digest_and_permissions_fail_closed(self):
        self.queue_path.write_bytes(self.original_queue_bytes + b"EVIL_DATA")
        with self.assertRaisesRegex(DanMek022Error, "PRIVATE_QUEUE_CONTENT_DIGEST_MISMATCH"):
            self.triage(write_private_html=True)
        self.queue_path.write_bytes(self.original_queue_bytes)
        self.queue_path.chmod(0o644)
        with self.assertRaisesRegex(DanMek022Error, "PRIVATE_QUEUE_FILE_UNSAFE"):
            self.triage(write_private_html=True)
        self.queue_path.chmod(0o600)
        self.assertFalse(list(self.review_folder.glob("danmek-022-*.html")))

    def test_refuse_unsafe_queue_path_and_multiple_candidate_files(self):
        outside = self.root / "elsewhere.json"
        outside.write_bytes(self.original_queue_bytes)
        with self.assertRaisesRegex(DanMek022Error, "PRIVATE_QUEUE_OUTSIDE_ALLOWED_FOLDER"):
            self.triage(queue_file=outside)
        explicit = self.triage(queue_file=self.queue_path)
        self.assertEqual(explicit["ambiguous_cases_rechecked"], 2)
        second = self.review_folder / self.queue_path.name.replace(".json", "1.json")
        # Invalid extra name is ignored but not treated as a valid queue.
        second.write_bytes(self.original_queue_bytes)
        second.chmod(0o600)
        self.assertEqual(self.triage()["ambiguous_cases_rechecked"], 2)

    def test_explicit_311_required_for_real_corpus_not_two_synthetic_cases(self):
        with self.assertRaises(DanMek022Error):
            self.triage(require_311=True, write_private_html=True)
        self.assertFalse(list(self.review_folder.glob("danmek-022-*.html")))

    def test_cli_prints_safe_aggregate_json_and_never_private_text(self):
        with (
            self.mock_originals(),
            patch("sys.argv", [
                "danmek-022", "--private-root", str(self.archive),
                "--confirm-machine-readable-use-permission",
            ]),
        ):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["ambiguous_cases_rechecked"], 2)
        self.assertNotIn("Worker", out.getvalue())
        self.assertNotIn("סִימָן", out.getvalue())
        self.assertNotIn(str(self.archive), out.getvalue())
        self.assertFalse(list(self.review_folder.glob("danmek-022-*.html")))

    def test_no_html_overwrite_even_if_existing_private_owner_edited(self):
        self.triage(write_private_html=True)
        path = next(self.review_folder.glob("danmek-022-*.html"))
        path.write_text("OWNER EDIT MUST REMAIN", encoding="utf-8")
        path.chmod(0o600)
        with self.assertRaisesRegex(DanMek022Error, "PRIVATE_AUTOMATED_TRIAGE_FAILED"):
            self.triage(write_private_html=True)
        self.assertEqual(path.read_text(), "OWNER EDIT MUST REMAIN")


if __name__ == "__main__":
    unittest.main()
