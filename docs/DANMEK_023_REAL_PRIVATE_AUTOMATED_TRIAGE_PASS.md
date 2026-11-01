# DANMEK-023 — Real owner-executed private English-ambiguity triage (2026-11-01)

**Result:** The owner successfully ran DANMEK-022 against the **real private**
311-case ledger on Parrot. Its offline research HTML was generated privately;
no previously owner-approved English reading was changed.

## Exact provenance

The owner first updated local `main` from
`c4c9303` to `85f61f9` (full merge commit
`85f61f963203fb0bd067da21e8d58f1503a4228f`).
Then the owner ran:

```bash
"$HOME/.local/share/olt-ches-venv/bin/python" \
    -m scripts.danmek_022_private_automated_triage \
    --private-root "$HOME/.olt-private/ches" \
    --confirm-machine-readable-use-permission \
    --require-311 \
    --write-private-html
```

The script reported **DANMEK-022-PRIVATE-AUTOMATED-REVIEW-v1**,
`NEW_PRIVATE_QUEUE` for the private HTML, and `BLOCKED` publication.

This evidence is the **owner's pasted local terminal result**, not a GitHub
Actions run on private data. The private case queue and HTML were **not**
uploaded, read by the assistant, or placed in GitHub.

## Owner-reported results

| Verified technical observation | Value |
| --- | ---: |
| English-order ambiguity cases rechecked against current private source | **311** |
| Same-number original-language candidate verse references present | **311** |
| Original-language candidate references missing | **0** |
| Raw `HV`/`AV` verb-morphology prefix occurrences in candidate words | **701** |
| Independently verified grammatical subjects | **0** |
| Independently verified CHES-to-original word/subject alignments | **0** |
| English editorial changes applied | **0** |
| Original CHES JSON files modified | **No** |
| Previously owner-approved English reader HTML modified | **No** |
| New private, read-only research HTML produced | **Yes** |
| Original-language evidence review still needed for all 311 | **Yes** |
| Publication status | **BLOCKED** |

The same 24 CHES filename prefix totals reported by DANMEK-020 were
reproduced and sum to **311**. See
[`data/observations/danmek_023_owner_reported_311_case_automated_triage_20261101.json`](../data/observations/danmek_023_owner_reported_311_case_automated_triage_20261101.json)
for the **numeric-only** observation.

**The 701 count is not 701 correct original-language verbs, 701 correct
English verb correspondences, 701 distinct cases, or 701 approved
morphological decisions.** It is simply the number of original-source
word records whose unreviewed morphology **string starts with `HV`
or `AV`** across the 311 provisional same-number verse candidates.
Multiple hits can occur in a single candidate verse. The entire original
verse may differ in source segmentation or numbering. Neither the
candidate book-ID crosswalk nor the English fragment-to-original word
relationship was authenticated by this run.

## Superseding owner instruction — DANMEK-026 (2026-11-01)

The research and figures below describe **historical work actually executed**,
not a mandatory future plan. Owner has since decided CHES's English reading and
its Hebrew/Aramaic correspondence are **accepted as authoritative for DANMEK**.
Do **not** continue the comparative OSHB/WLC alignment, morphology or
source-verse authentication campaign as part of DANMEK-025. The new priority is
English-only grammatical-error triage with no-change by default. This avoids
the unnecessary additional philological verification process. Retain the old
results unchanged and do not claim they showed CHES errors.

## Next evidence-driven development (historical, now superseded by DANMEK-026)

The next useful step is **not** another read-only copy of the 311-case
list. It is an **evidence-graded** and still non-mutating review engine
that:

1. Checks book/chapter/verse reference mappings against separate source
   edition metadata, tracks known numbering differences and fails
   closed when the crosswalk cannot be established;
2. Distinguishes an original-language raw morphology code from a
   **documented parsed morphology feature**, without assuming any
   English-fragment pairing;
3. Separates *no safe source alignment*, *candidate with partial
   evidence* and *candidate with independently verified mapping*;
4. Reports only **count summaries and fixed status codes** to stdout;
   keeps actual licensed CHES words and imported original-language
   context private, and leaves unreviewable cases unresolved;
5. Never changes the owner-verified DANMEK-013/014 English HTML,
   automatically fixes a verb, or claims expert scholarly approval.

The owner need not manually inspect the entire 311-case queue to
continue developing these automated checks. Human linguistic review
remains necessary wherever the source evidence does not unambiguously
support a proposed grammatical conclusion, and final editorial changes
require separate explicit owner approval.

**Status:** TECHNICAL AUTO-TRIAGE SUCCESS (OWNER REPORTED).
PHILOLOGICAL REVIEW AND ENGLISH EDIT APPROVAL NOT DONE.
PUBLICATION BLOCKED.
