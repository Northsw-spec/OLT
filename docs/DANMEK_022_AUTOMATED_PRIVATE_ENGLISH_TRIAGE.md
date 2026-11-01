# DANMEK-022 — Automated, private, non-mutating review of 311 English order ambiguities

**Status:** Implemented in a standalone offline tool; the *actual* 311-case
private HTML has **not** yet been generated or read by GitHub Actions.

## Purpose and boundaries

DANMEK-020 already generated the owner's **311-item immutable private
research ledger**. All 311 items have an imported original-language
**same-number verse candidate**, but **none** has an independently
authenticated CHES-to-original-language word alignment or grammatical
subject. The original-language source corpus and CHES source corpus
also differ in number of verse rows.

The new `scripts.danmek_022_private_automated_triage` automates the
*mechanical evidence collection*, with an optional private read-only
HTML review, without asking the owner to manually inspect 311 cases
to make progress.

### What is automatically checked

1. Read only the existing `DANMEK-020` private JSON ledger, require the
   correct immutable SHA-256 content-derived file name, secure `0600`
   permissions, a private `0700` directory, and all original
   `NOT_DONE`/`BLOCKED` review gates.
2. Re-run the existing DANMEK-020 source scanner in read-only mode.
   Require its current verified reader snapshot, ambiguous count,
   per-prefix distribution and source-candidate counts to match the
   saved private queue. `--require-311` fails if the current source
   snapshot is not exactly the prior owner's 311 cases.
3. Verify each queued CHES chapter against **current original JSON bytes**
   and source chapter SHA-256, compare the exact per-verse source
   fragment sequence, and independently repeat the existing ambiguous
   **English typography** decision. A changed or no-longer-ambiguous
   verse causes a fail-closed stop.
4. Re-load SHA-pinned imported original Hebrew/Aramaic books and compare
   each original-language verse candidate's **exact word IDs, ordinals,
   original script, raw morphology and lemma tags** against the ledger.
   Missing same-number candidates stay explicitly missing.
5. Count raw original **verb-morphology code prefixes** (`HV`/`AV`)
   as *research hints only*. These are **not** decoded as proven verb
   semantics, grammatical subject, tense, word alignment or matching
   English fragment. They are merely original source string tags.
6. Re-check the source snapshot before producing a report. Output
   to the terminal is **only aggregated numbers, booleans, statuses
   and the existing opaque reader snapshot ID** — never original words,
   licensed English, private file paths or HTML content.

### What remains explicitly unresolved

- A CHES filename prefix mapped to an original-language book code is
  a **research candidate**, not independently verified book mapping.
- Equal verse numbers are not proof of matching word positions or even
  full source-verse crosswalk. For these 311 cases, they are merely
  matching candidate references.
- `HV`/`AV` source morphology codes indicate only a raw
  verb-code prefix found in one or more tokens in the *candidate*
  source verse, not which candidate English verb or subject is correct.
- No grammatical subjects are verified, and **all 311 English-order
  ambiguities remain unresolved** after this automated screening.
- Neither source English nor owner-verified HTML can be modified by
  this tool. All review decisions must be made separately with
  philological evidence. No blanket changes or release approval.

## Parrot — automatic validation, metadata only

After the GitHub PR is merged and CI is green:

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" \
  -m scripts.danmek_022_private_automated_triage \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --require-311
```

This creates **zero files**, and reports only classified numerical counts.

To also generate a private, read-only HTML research view, use the
**same command plus `--write-private-html`**. This is an explicit
local-only artifact request and writes one immutable `0600` HTML file
to `~/.olt-private/ches-order-review/` beside the original queue.
The HTML uses no JavaScript, external links, remote assets, forms, or
submit/apply controls. It HTML-escapes all text, includes a restrictive
Content Security Policy, shows source CHES English fragments and raw
original-language words side by side, and visibly marks all alignments
and grammatical subjects as **UNVERIFIED**. An existing identical
HTML is reused; an existing edited file is NEVER overwritten.
Do **not** upload the generated private HTML to GitHub or paste its
contents into chat.

**Multiple private queues?** The command fails closed unless exactly
one DANMEK-020 versioned queue exists. If several valid snapshots
exist, supply the intended *private absolute path* with
`--queue-file`. The chosen file must reside directly inside the
allowed private queue directory and match its internal SHA-256 filename.
Never guess a file path.

## CI and deployment

GitHub Actions uses **only fabricated source text and synthetic
Hebrew/Aramaic strings**. Regression cases cover:

- exact revalidation of the same locked English ambiguity and source
  version;
- available vs missing original-language research candidate;
- source morphology tag counts without false original-language signoff;
- no output files for default audit-only mode;
- HTML escape and CSP/XSS protection;
- immutable write-once `0600` output and no overwrite of owner's
  modified HTML;
- rejecting changed source English, changed original token fields,
  altered queue JSON, inappropriate permissions, unsafe locations;
- sanitized terminal JSON without private text.

## Actual owner-run acceptance (DANMEK-023, 2026-11-01)

The owner executed the real DANMEK-022 Parrot CLI with
`--require-311 --write-private-html` after updating to the merged
implementation on `main`. It reported **311 ambiguous cases
revalidated**, **311 provisional original-language verse references
present**, **0 missing**, **701 unreviewed original `HV`/`AV`
morphology code-prefix occurrences**, **0 verified grammatical
subjects**, **0 English changes**, and
`private_review_html_status=NEW_PRIVATE_QUEUE`. The private HTML was
created offline, not uploaded to GitHub. This is a **technical
source-integrity triage PASS**, not a completed word-level linguistic
review. See [owner-run evidence](DANMEK_023_REAL_PRIVATE_AUTOMATED_TRIAGE_PASS.md).

The owner-verified DANMEK-013/014 English reader remains **LOCKED**.
Full 66-book translation **NOT DONE**. Copyright/publication
rights **NOT VERIFIED**. Publication **BLOCKED**.
