"""CHES-003: only synthetic copyrighted-source substitutes are committed."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.ches_import import write_private_json
from scripts.ches_private_alignment_review import (
    CHESReviewError, add_unverified_alignment_proposal,
    build_private_genesis_1_review_queue, private_file,
)

ROOT = Path(__file__).resolve().parents[1]


def fake_genesis_one_pdf_extract():
    """Fake English text and per-verse span counts; original source PDF SHA pinned."""
    x = json.loads((ROOT / "data/engine/olt_ches_source_manifest.json").read_text())
    expected = x["source_reference"]
    rows = []
    for n in range(1, 32):
        count = 16 if n == 1 else 17
        rows.append({
            "reference": f"Gen.1.{n}",
            "publication_status": "BLOCKED",
            "source_ches_spans_NOT_OLT_TRANSLATION": [
                {"page": 1 + (n - 1) // 8, "pdf_x": 10.0 + i,
                 "pdf_y": 40.0 + n, "original_ches_line_text": f"FAKE{i}"}
                for i in range(count)
            ],
        })
    return {
        "book": "Gen",
        "chapter": 1,
        "original_source_pdf_sha256": expected["source_pdf_sha256"],
        "source_pdf_byte_length": expected["source_pdf_bytes"],
        "source_pdf_page_count": expected["source_pdf_pages"],
        "verses_extracted": 31,
        "ches_pdf_green_spans": 526,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }


class TestPrivateCHESReviewQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = build_private_genesis_1_review_queue(fake_genesis_one_pdf_extract())

    def test_full_genesis_queue_has_no_auto_linkages_or_approvals(self):
        queue = self.queue
        self.assertEqual(len(queue["verses"]), 31)
        self.assertEqual(queue["original_hebrew_word_token_count"], 434)
        self.assertEqual(queue["private_pdf_green_span_count"], 526)
        self.assertEqual(queue["proposed_alignment_group_count"], 0)
        self.assertEqual(queue["independently_approved_alignment_count"], 0)
        self.assertFalse(queue["all_word_alignments_verified"])
        self.assertFalse(queue["english_translation_approved"])
        self.assertEqual(queue["publication_status"], "BLOCKED")
        self.assertTrue(all(not row["proposed_alignment_groups"] for row in queue["verses"]))
        self.assertEqual(len(queue["verses"][0]["original_hebrew_source_words"]), 7)
        self.assertEqual(len(queue["verses"][0]["private_green_pdf_source_spans"]), 16)

    def make_proposal(self, q, verse_index=0):
        v = q["verses"][verse_index]
        return {
            "reference": v["reference"],
            "green_span_ids": [v["private_green_pdf_source_spans"][0]["span_id"]],
            "oshb_token_ids": [v["original_hebrew_source_words"][0]["source_token_id"]],
            "segmentation": "ONE_SPAN_TO_ONE_TOKEN_UNVERIFIED",
            "original_pdf_hebrew_line_checked": True,
            "reviewer_evidence_note": "Manual comparison only, independently unreviewed.",
            "approved": False,
        }

    def test_proposal_stays_unverified_and_prevents_spurious_duplicate_mapping(self):
        q = copy.deepcopy(self.queue)
        request = self.make_proposal(q)
        add_unverified_alignment_proposal(q, request)
        self.assertEqual(q["proposed_alignment_group_count"], 1)
        saved = q["verses"][0]["proposed_alignment_groups"][0]
        self.assertEqual(saved["word_alignment_status"], "MANUAL_PROPOSAL_UNVERIFIED")
        self.assertFalse(saved["approved"])
        self.assertEqual(saved["independent_source_linguistic_review"], "NOT_DONE")
        with self.assertRaises(CHESReviewError):
            add_unverified_alignment_proposal(q, request)

    def test_reject_nonexistent_ids_cross_verse_and_automatic_approval(self):
        base = self.queue
        good = self.make_proposal(base)
        other = base["verses"][1]
        cases = [
            {**good, "green_span_ids": ["unknown"]},
            {**good, "green_span_ids": [other["private_green_pdf_source_spans"][0]["span_id"]]},
            {**good, "oshb_token_ids": [other["original_hebrew_source_words"][0]["source_token_id"]]},
            {**good, "oshb_token_ids": ["unknown"]},
            {**good, "oshb_token_ids": good["oshb_token_ids"] * 2},
            {**good, "approved": True},
            {**good, "original_pdf_hebrew_line_checked": False},
            {**good, "reviewer_evidence_note": "short"},
            {**good, "segmentation": "MULTIPLE_SPANS_OR_TOKENS_UNVERIFIED"},
            {**good, "reference": "Gen.2.1"},
        ]
        for candidate in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaises(CHESReviewError):
                    add_unverified_alignment_proposal(copy.deepcopy(base), candidate)

    def test_explicit_one_to_many_proposal_requires_segmentation_warning(self):
        q = copy.deepcopy(self.queue)
        proposal = self.make_proposal(q)
        proposal["oshb_token_ids"].append(q["verses"][0]["original_hebrew_source_words"][1]["source_token_id"])
        proposal["segmentation"] = "MULTIPLE_SPANS_OR_TOKENS_UNVERIFIED"
        add_unverified_alignment_proposal(q, proposal)
        self.assertEqual(q["proposed_alignment_group_count"], 1)
        self.assertFalse(q["all_word_alignments_verified"])

    def test_private_path_only_and_rights_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(CHESReviewError):
                private_file(root / "public" / "source.json")
            output = root / ".olt-private" / "ches" / "review.json"
            write_private_json(self.queue, private_file(output))
            self.assertEqual(json.loads(output.read_text())["private_licensed_data"], True)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)

    def test_refuse_private_pdf_source_with_missing_spans_or_modified_license_flag(self):
        a = fake_genesis_one_pdf_extract()
        a["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0]["original_ches_line_text"] = ""
        with self.assertRaises(CHESReviewError):
            build_private_genesis_1_review_queue(a)
        b = fake_genesis_one_pdf_extract()
        b["full_source_text_in_public_git_permitted"] = True
        with self.assertRaises(ValueError):
            build_private_genesis_1_review_queue(b)


if __name__ == "__main__":
    unittest.main()
