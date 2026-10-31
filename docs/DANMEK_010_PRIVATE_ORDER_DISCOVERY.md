# DANMEK-010 — Private candidate discovery for English subject-first order

**Status:** Small offline review pipeline implemented. Its proposal scanner is a
**heuristic over English text typography**, NOT a Hebrew/Aramaic syntax parser,
not original-language verification, and **NOT an automatic conversion of the OT**.
The original CHES data are neither corrected nor changed.

## What it does

- Reads each existing validated private `~/.olt-private/ches/*.json`
  source file; no internet, PDF re-download or copying source into GitHub.
- Detects a limited candidate shape: English pronoun/verb gloss
  (e.g. synthetic `and·he-shaped`) followed by a capitalized potential
  subject, either across exactly two consecutive whole fragments or within
  exactly one fragment. It is a **candidate only**, not proof of a subject.
- If one verse has multiple candidate pairs, it is marked ambiguous and left
  outside the actionable queue. Nonmatching passages are not guessed.
- Creates a **private**, immutable `review-<hash>/candidates.json` and
  `review-<hash>/review.html` with original and suggested English order,
  so the operator can check candidate phrases against the original Hebrew
  and CHES PDF layout without making a public upload.
- By default keeps up to 2,000 candidates in one snapshot; reports the
  true detected count and whether the queue was truncated.
- The private review entries are intentionally marked
  `source_syntax_reviewed=false`, `review_note=NOT_REVIEWED`. They are
  **not accepted by DANMEK-009's reader as approved rules**.

This is **not** linguistic evidence that `Leader` (or another candidate)
is the grammatical subject; even a candidate whose English phrasing looks
plausible can be a false positive.

## Scan and preview on Parrot

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main

PY="$HOME/.local/share/olt-ches-venv/bin/python"

# No files created; output is sanitized counters only.
"$PY" -m scripts.danmek_010_order_review \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --audit-only

# Save a separate private HTML review and candidate JSON.
"$PY" -m scripts.danmek_010_order_review \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-review
```

For a focused chapter (for instance, local source prefix `gen`, chapter
`1`), append `--book-prefix gen --chapter 1` to the build command. The
command returns a generated `review_id` such as `review-<hash>`. The actual
private review files are in
`~/.olt-private/olt-english-order/<review_id>/`.
**No passages, local file paths or original CHES text are printed to stdout.**

Do not paste a private review HTML, source JSON or passages into a public PR.

## Promote ONE reviewed candidate

Check the proposed subject/verb relation and placement against the genuine
original-language syntax and CHES original text/geometry locally. Only after
that check, explicitly attest one candidate. Example CLI syntax, with
placeholders (never use this as an unexamined bulk approval):

```bash
"$PY" -m scripts.danmek_010_order_review \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --approve-reference gen.1.1 \
  --review-id 'review-REPLACE_WITH_ACTUAL_ID' \
  --review-note 'Hebrew subject/verb relation verified; record source evidence here' \
  --attest-original-language-syntax-reviewed
```

The command verifies the proposal against the **current unchanged SHA-256
of the original source chapter JSON and exact current fragment strings**.
It creates or extends `~/.olt-private/olt-english-order/approved.json`,
which DANMEK-009 already consumes via `--olt-subject-first`. Before
extending a prior `approved.json`, it makes an immutable, source-private
SHA-addressed backup. A previously approved reference cannot be replaced
silently. This tool records an **operator attestation**, not independent
machine proof that the original Hebrew relation was correct.

To build the separate private OLT HTML after real approvals:

```bash
"$PY" -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader \
  --use-ylt-authority \
  --olt-display-faces \
  --olt-subject-first
```

YLT 1898 must already be installed in its verified private location for
the optional `--use-ylt-authority` argument. Otherwise omit that flag.

## Verification and next task

GitHub Actions uses only **fabricated synthetic English phrases**. It tests
read-only audit mode, case preservation, candidate ambiguity, immutable
review HTML and manifest, explicit approval, outdated-source rejection,
source byte immutability, safe private permissions, HTML escaping, review
backup, and the existing DANMEK-009 reader integration.

**Actual deployment still requires local source checks and verified syntax
review.** The scanner has not been run against the owner's private 929 JSON
files, and cannot claim real candidate counts, English-order accuracy or
coverage in any chapter. The next evidence-bearing step is the **private
count-only audit/scan**. Based on those counts, refine candidate patterns
only with privately evaluated cases; do not guess original Hebrew syntax.

Permanent rules: no divine-referent capitalization (DANMEK-007); CHES original
data untouched; publication remains **BLOCKED**.
