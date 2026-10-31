"""CHES-003: private original-source-linked word review ledger, no automatic alignment.

Only Genesis 1 with exact PDF pin and OSHB hashes is in scope. Green PDF
text and any reviewer annotations are never published in this tool's CLI logs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from olt_core.sources import ROOT, load_ot_book, read_provenance
from scripts.ches_import import import_private_pdf, write_private_json
from scripts.ches_oshb_verse_qa import verify_genesis_1_verse_locators

SEGMENTATIONS = frozenset({
    "ONE_SPAN_TO_ONE_TOKEN_UNVERIFIED",
    "MULTIPLE_SPANS_OR_TOKENS_UNVERIFIED",
})


class CHESReviewError(ValueError):
    """Private word review proposal refers to unverified or unsafe source data."""


def private_file(path: Path) -> Path:
    target = path.expanduser().resolve()
    if ".olt-private" not in target.parts:
        raise CHESReviewError("Review files must remain inside a .olt-private directory")
    return target


def build_private_genesis_1_review_queue(
    original_chapter: dict[str, Any], root: Path = ROOT
) -> dict[str, Any]:
    """Keep *all* 526 licensed spans private; identify exact source Hebrew tokens.

    Recording a possible same-verse pair is NOT verifying lexical equivalence.
    """
    qa = verify_genesis_1_verse_locators(original_chapter, root=root)
    book = load_ot_book("Gen", root, read_provenance(root))
    source_verses = {
        row["reference"]: row for row in book["verses"]
        if row["reference"].startswith("Gen.1.")
    }
    queue: list[dict[str, Any]] = []
    counts = {"original_tokens": 0, "green_pdf_spans": 0}
    for index, verse in enumerate(original_chapter["verses"], 1):
        reference = f"Gen.1.{index}"
        source_words = source_verses[reference]["words"]
        raw_spans = verse["source_ches_spans_NOT_OLT_TRANSLATION"]
        green = []
        for ordinal, span in enumerate(raw_spans, 1):
            if (not isinstance(span, dict) or
                not isinstance(span.get("original_ches_line_text"), str) or
                not span["original_ches_line_text"].strip() or
                not isinstance(span.get("page"), int) or
                not all(isinstance(span.get(key), (int, float)) and
                        not isinstance(span.get(key), bool)
                        for key in ("pdf_x", "pdf_y"))):
                raise CHESReviewError(f"{reference}: malformed private source PDF span")
            if span["page"] < 1 or span["page"] > original_chapter["source_pdf_page_count"]:
                raise CHESReviewError(f"{reference}: invalid original PDF page")
            green.append({
                "span_id": f"{reference}:green:{ordinal}",
                "original_pdf_page": span["page"],
                "original_pdf_x": span["pdf_x"],
                "original_pdf_y": span["pdf_y"],
                "licensed_source_text_private": span["original_ches_line_text"],
                "status": "UNALIGNED_GREEN_SOURCE_SPAN",
            })
        hebrew = []
        for ordinal, token in enumerate(source_words, 1):
            if (token.get("reference") != reference or token.get("ordinal") != ordinal or
                not isinstance(token.get("source_id"), str) or
                not isinstance(token.get("hebrew"), str) or
                not isinstance(token.get("morph_raw"), str)):
                raise CHESReviewError(f"{reference}: invalid source token identity")
            hebrew.append({
                "source_token_id": token["source_id"],
                "original_ordinal": ordinal,
                "original_hebrew": token["hebrew"],
                "original_lemma_annotation_unreviewed": token["lemma_raw"],
                "original_morphology_annotation_unreviewed": token["morph_raw"],
                "status": "ORIGINAL_OSHB_SOURCE_NOT_CHES_ALIGNED",
            })
        counts["original_tokens"] += len(hebrew)
        counts["green_pdf_spans"] += len(green)
        queue.append({
            "reference": reference,
            "original_hebrew_source_words": hebrew,
            "private_green_pdf_source_spans": green,
            "proposed_alignment_groups": [],
            "word_alignment_status": "NO_LINKS_PROPOSED",
            "reviewer_approval": False,
            "publication_status": "BLOCKED",
        })
    if counts != {"original_tokens": 434, "green_pdf_spans": 526}:
        raise CHESReviewError("Pinned Genesis chapter token/span totals changed")
    return {
        "checkpoint": "CHES-003",
        "original_source_pdf_sha256": original_chapter["original_source_pdf_sha256"],
        "original_oshb_source": "PINNED_OSHB_WLC",
        "scope": "GENESIS_1_ONLY",
        "private_licensed_data": True,
        "all_word_alignments_verified": False,
        "independently_approved_alignment_count": 0,
        "proposed_alignment_group_count": 0,
        "english_translation_approved": False,
        "target_languages": ["en"],
        "publication_status": "BLOCKED",
        "source_verse_qa": qa,
        "original_hebrew_word_token_count": counts["original_tokens"],
        "private_pdf_green_span_count": counts["green_pdf_spans"],
        "verses": queue,
    }


def add_unverified_alignment_proposal(
    queue: dict[str, Any], request: dict[str, Any]
) -> dict[str, Any]:
    """Validate an explicitly reviewed grouping by ID, but NEVER certify meaning.

    The operator can propose many-to-one/many-to-many correspondences. A
    follow-up independent linguistic review remains mandatory. No automatic
    association from span order or word order is permitted.
    """
    if (queue.get("checkpoint") != "CHES-003" or
        queue.get("scope") != "GENESIS_1_ONLY" or
        queue.get("private_licensed_data") is not True or
        queue.get("all_word_alignments_verified") is not False or
        queue.get("publication_status") != "BLOCKED"):
        raise CHESReviewError("Invalid or improperly approved private review ledger")
    if not isinstance(request, dict):
        raise CHESReviewError("Reviewer proposal must be an object")
    if request.get("approved") is not False:
        raise CHESReviewError("This workflow cannot approve word or translation alignments")
    ref = request.get("reference")
    verses = queue.get("verses")
    if not isinstance(ref, str) or not isinstance(verses, list):
        raise CHESReviewError("Missing source verse or review ledger")
    candidates = [v for v in verses if v.get("reference") == ref]
    if len(candidates) != 1 or not ref.startswith("Gen.1."):
        raise CHESReviewError("Reviewer verse absent or ambiguous")
    verse = candidates[0]
    existing = verse.get("proposed_alignment_groups")
    if not isinstance(existing, list):
        raise CHESReviewError("Malformed existing reviewer proposals")
    green_ids = {s["span_id"] for s in verse["private_green_pdf_source_spans"]}
    word_ids = {t["source_token_id"] for t in verse["original_hebrew_source_words"]}
    spans = request.get("green_span_ids")
    tokens = request.get("oshb_token_ids")
    if (not isinstance(spans, list) or not spans or
        not isinstance(tokens, list) or not tokens or
        not all(isinstance(x, str) for x in spans + tokens) or
        len(set(spans)) != len(spans) or len(set(tokens)) != len(tokens) or
        not set(spans).issubset(green_ids) or not set(tokens).issubset(word_ids)):
        raise CHESReviewError("Cross-verse, empty, duplicate or nonexistent source IDs")
    shape = request.get("segmentation")
    expected = ("ONE_SPAN_TO_ONE_TOKEN_UNVERIFIED" if len(spans) == len(tokens) == 1
                else "MULTIPLE_SPANS_OR_TOKENS_UNVERIFIED")
    if shape not in SEGMENTATIONS or shape != expected:
        raise CHESReviewError("Segmentation must explicitly describe span/token cardinality")
    note = request.get("reviewer_evidence_note")
    if (not isinstance(note, str) or len(note.strip()) < 12 or len(note) > 4000 or
        request.get("original_pdf_hebrew_line_checked") is not True):
        raise CHESReviewError("Require substantive manual original-PDF Hebrew evidence")
    for row in existing:
        if set(spans) & set(row["green_span_ids"]):
            raise CHESReviewError("Green source span already belongs to another proposal")
        if set(tokens) & set(row["oshb_token_ids"]):
            raise CHESReviewError("Hebrew source token already belongs to another proposal")

    saved = {
        "reference": ref,
        "green_span_ids": list(spans),
        "oshb_token_ids": list(tokens),
        "segmentation": shape,
        "original_pdf_hebrew_line_checked_by_submitter": True,
        "reviewer_evidence_note_private": note.strip(),
        "independent_source_linguistic_review": "NOT_DONE",
        "word_alignment_status": "MANUAL_PROPOSAL_UNVERIFIED",
        "approved": False,
        "publication_status": "BLOCKED",
    }
    existing.append(saved)
    verse["word_alignment_status"] = "PROPOSALS_EXIST_UNVERIFIED"
    queue["proposed_alignment_group_count"] += 1
    return queue


def _summary(queue: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in queue.items()
            if key in {"checkpoint", "scope", "original_hebrew_word_token_count",
                       "private_pdf_green_span_count", "proposed_alignment_group_count",
                       "independently_approved_alignment_count",
                       "all_word_alignments_verified", "publication_status"}}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Private CHES ↔ original Hebrew manual review queue; NO publication")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--confirm-machine-readable-use-permission", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--output-private", type=Path)
    parser.add_argument("--proposal-private", type=Path, help="Optional one-proposal JSON file in .olt-private")
    args = parser.parse_args()
    if not args.confirm_machine_readable_use_permission:
        parser.error("Explicit licensed machine-readable use confirmation required")
    if args.proposal_private is not None and args.output_private is None:
        parser.error("Reviewer proposal requires an explicitly private output path")
    original = import_private_pdf(args.pdf.read_bytes(), "Gen", 1, expected_verses=31)
    ledger = build_private_genesis_1_review_queue(original)
    if args.proposal_private is not None:
        request = json.loads(private_file(args.proposal_private).read_text(encoding="utf-8"))
        ledger = add_unverified_alignment_proposal(ledger, request)
    if args.output_private is not None:
        write_private_json(ledger, private_file(args.output_private))
    print(json.dumps(_summary(ledger), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
