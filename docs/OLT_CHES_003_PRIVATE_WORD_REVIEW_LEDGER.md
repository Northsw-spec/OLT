# CHES-003 — Private Hebrew word / CHES PDF-span review ledger

**Purpose:** provide a real operator workflow for Genesis 1 to inspect 434 pinned OSHB original Hebrew source word tokens alongside the independently verified **526 original green CHES PDF text spans** without pretending that each green span is a Hebrew word or publishing copyrighted text. This checkpoint is a **review ledger**, not an automatic translator.

## Strict source contracts

- Source PDF must match the exact pinned original Genesis 1 byte size, four pages, SHA-256, 31 printed verse anchors and 526 green text spans.
- All 31 verse references must correspond to the authentic imported Hebrew Gen.1.1–Gen.1.31. All 434 OSHB word tokens are read from existing Git-blob-hash-checked source files with exact original token IDs.
- Green original PDF text is *retained only in the private ledger* under `.olt-private/`. All repository tests use **invented** dummy green text. Real GitHub Actions integration generates a summary **in memory only** and logs no third-party text.
- No original Hebrew/PDF original-language glyph crosswalk is inferred merely from a common verse. PDF spans are typography fragments; token↔morpheme ↔ gloss mappings may be many-to-many or ambiguous.
- All manual proposals are strictly **UNVERIFIED**, require explicit operator checking and an evidence note, reject cross-verse/nonexistent/duplicate references, and must be independently reviewed before they could ever be promoted. No automated promotion is implemented.
- `README.md` must remain zero bytes. Technical status, copyright limits, and source attribution remain in their separate files.

## Commands (from the repository root)

Install the same pinned extractor dependency used by existing CHES-001:

```bash
python -m pip install PyMuPDF==1.26.5

# The only public output is a count/status summary, NOT any CHES source text.
python -m scripts.ches_private_alignment_review \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission --audit

# Store the private ledger with restrictive file permissions (0600).
python -m scripts.ches_private_alignment_review \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission \
  --output-private .olt-private/ches/genesis_1_review.json
```

To record **one** proposed correspondence from a manually reviewed private original-PDF Hebrew line, create a JSON input file under `.olt-private/` (use IDs from the private ledger; illustrative IDs below are not asserted to be linguistically equivalent). Do not commit that file:

```json
{
  "reference": "Gen.1.1",
  "green_span_ids": ["Gen.1.1:green:1"],
  "oshb_token_ids": ["01xeN"],
  "segmentation": "ONE_SPAN_TO_ONE_TOKEN_UNVERIFIED",
  "original_pdf_hebrew_line_checked": true,
  "reviewer_evidence_note": "Examined original Hebrew PDF glyph, segmentation and source token; pending independent review.",
  "approved": false
}
```

```bash
python -m scripts.ches_private_alignment_review \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission \
  --proposal-private .olt-private/ches/manual_proposal.json \
  --output-private .olt-private/ches/genesis_1_review_with_one_proposal.json
```

This records a *single* manually supplied, **unverified** grouping. It does **not** certify whether `Gen.1.1:green:1` and `01xeN` correspond. More than one source span or OSHB token must use `MULTIPLE_SPANS_OR_TOKENS_UNVERIFIED` and retain an explanation. A separate expert review/promotion process is not yet implemented. When this command is repeated, the queue is recreated; existing proposals must be preserved separately before re-execution. This deliberate constraint prevents accidental automatic re-approval of stale or unsupported links.

## Verification

```bash
python -m unittest discover -s tests -p 'test_ches_003_private_review.py' -v
```

The existing dedicated `ches-ingest.yml` workflow additionally parses the real pinned Genesis 1 PDF in an ephemeral runner, building the review ledger in memory and printing **counts only**.

## Next step

Implement independent review of manually proposed token/span mappings using the **original Hebrew PDF line's genuine word division**. Only explicitly supported and independently adjudicated claims may progress to a verified lexical crosswalk, which remains separate from OLT's editorial English choices. Any use of CHES as a basis for publishable English text needs rights analysis against the actual permission terms. The other 928 chapter PDFs, full GT import, word alignment, completed English Bible, owner approval and other target languages all remain outside this checkpoint.
