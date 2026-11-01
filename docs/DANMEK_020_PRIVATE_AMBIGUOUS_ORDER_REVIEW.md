# DANMEK-020 — Private review queue for ambiguous English subject order

**Purpose:** After the owner-run DANMEK-016 audit recorded 311 English
verses with multiple competing editorial order patterns, create a
privacy-preserving, **read-only research queue**. Do not silently edit
any of the verified DANMEK-013/014 English HTML reading.

## Implementation

`scripts.danmek_020_private_ambiguous_order_review` iterates the
fully validated local CHES archive. For each verse it invokes the
**existing** `apply_owner_approved_candidates` function with the
source text unchanged and **only** queues those whose result is
`AMBIGUOUS`. It verifies this yields precisely the same ambiguous
count as the locked private reader. Optional `--require-311` refuses
a corpus whose count differs from the real owner's prior snapshot.

The new tool reads the existing **SHA-pinned, imported OSHB/WLC OT
source book files** from the OLT checkout and attaches a **provisional
same-number verse candidate** when one exists. For each such
candidate, the private review file may include the imported Hebrew or
Aramaic text, token IDs, word ordinals and raw morphology annotations.
This allows an editor to inspect the ambiguity *in context*.

**CRITICAL:** The source index checks a CHES filename prefix/chapter
against its own PDF index only; it does NOT verify that prefix
corresponds to a particular OSHB book. The prefix-to-OSHB book table
in DANMEK-020 is therefore a **candidate research lookup**, NOT an
independently authenticated mapping. A matching verse number is also
NOT proof that the verse's original-language syntax or morphology
aligns with a particular CHES English source fragment. No word
alignment is generated or inferred. Missing verses, including
possible numbering disagreements (e.g. Nehemiah 7), remain explicitly
unmatched. All cases remain unreviewed and **reorder_permitted=false**.

The original-language imported corpus counts and CHES verse-row counts
need not agree; e.g. existing imported OT provenance reports **23,213**
original source verse rows, versus **23,144** observed CHES verse
rows. Do not silently adjust verse numbers to hide that difference.

## Run on Parrot (no manual code testing required)

After PR merge, update the checkout on `main` and run:

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" \
  -m scripts.danmek_020_private_ambiguous_order_review \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --require-311
```

This prints **metadata only**: number of English ambiguities, source
prefix counts, how many same-reference original-language candidate
verses can be located and how many are missing. It creates NO files.

To create the actual review ledger for subsequent analysis, explicitly
add `--write-private-queue`. The tool then creates exactly one
immutable `0600` private JSON under
`~/.olt-private/ches-order-review/` (directory `0700`).
The filename is deterministic and revisioned by content digest; an
existing identical file is reused, an existing modified file is never
overwritten. The private ledger contains all 311 CHES English
source readings and only provisional original-language side-by-side
research candidates, so it **must never be uploaded to GitHub or
pasted into chat**. The command prints neither words nor paths.

No network access. No source JSON or HTML edits. No publication.
New queue entries cannot certify grammatical subject/word alignment,
grant editorial approval, or modify the verified reading.

## Quality and editorial boundaries

- `AMBIGUOUS` means multiple English *regex patterns*, not
  necessarily a Biblical Hebrew linguistic error.
- Original script and morph strings are imported, SHA-pinned source
  annotations; no independent expert review is implied.
- Verses without a same-number original-source candidate stay
  `NO_SAME_REFERENCE_ORIGINAL_VERSE_FOUND`; never invent the
  missing words, subject or verse mapping.
- Private file entries include a fixed `NOT_DONE` human-review
  status and `reorder_permitted=false` for every case.
- The tool has **no code path to apply** a revised English sentence.
  Any later approved rule must be separately grounded and tested in
  a new versioned private snapshot, with distinct owner sign-off.
- Python unit tests use invented CHES English and fake original words,
  including contradictory and missing candidate references. GitHub
  Actions cannot inspect the user's private 311 real cases.

**Owner-run update (2026-11-01):** The owner actually executed
`--require-311 --write-private-queue` on Parrot, reporting **311**
English ambiguity cases and **311** provisional same-reference
original-language candidates with **0** missing references. A new
private ledger was created (`NEW_PRIVATE_QUEUE`). Philological
verification and English corrections remain **NOT DONE**. See
[DANMEK-021](DANMEK_021_OWNER_REPORTED_PRIVATE_311_QUEUE.md).
DANMEK-013/014 visually verified presentation remains LOCKED.
Complete 66-book OLT translation NOT APPROVED. Publication BLOCKED.
