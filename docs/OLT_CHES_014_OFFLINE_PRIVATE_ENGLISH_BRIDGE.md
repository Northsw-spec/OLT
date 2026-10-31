# CHES-014 — Offline private CHES JSON → unapproved OLT English working drafts

**Status:** Narrow engineering bridge for the currently **fourteen source-pinned** original OT chapter scopes (Genesis 1–8 and Exodus 1–6), not a 929-chapter English engine and not an approved Bible translation. The owner's private PDF importer, existing English source generators, Hebrew checks and original CHES data remain unchanged.

## Rationale

The private 929-chapter CHES importer writes one source-only JSON chapter at
`$HOME/.olt-private/ches/<source-prefix>.<chapter>.json`. Prior English
pilot scripts primarily started from the downloaded **PDF** instead. Re-fetching
a chapter's original PDF just to render a private English working gloss stream
would duplicate acquisition and obstruct direct use of the locally imported
private corpus.

CHES-014 reuses the existing CHES-004 (Genesis 1) and CHES-007 (additional
pinned chapters) generators **without** reimplementing translation, grammar,
lexical mapping or PDF parsing.

## Safe one-chapter operations

From an updated local OLT checkout, using its installed Python environment:

```bash
cd ~/OLT-CHES-tools
git pull --ff-only

# Offline count-only validation; leaves files unchanged.
~/.local/share/olt-ches-venv/bin/python \
  -m scripts.ches_014_offline_english_bridge \
  --book Gen --chapter 1 \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --audit-only

# Generate one separate private, UNAPPROVED English source-gloss draft.
~/.local/share/olt-ches-venv/bin/python \
  -m scripts.ches_014_offline_english_bridge \
  --book Gen --chapter 1 \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --write-private-draft
```

Output (when explicitly requested):

`$HOME/.olt-private/olt-english-drafts/gen.1.unapproved-english.json`

The original imported file `gen.1.json` is untouched. Source-prefix
identifiers such as `gen` / `exo` are converted to the pinned original
Bible scope `Gen` / `Exod` **in memory and only after matching the exact
public source registry**. Only the **fourteen** existing explicit source pins
are allowed; unknown or unpinned books and chapters are rejected.

The output directory is owner-private (0700); the draft file is owner-private
(0600). If the same draft bytes already exist, re-running is a no-op. If a
draft file differs (e.g. it contains manual unapproved editorial changes),
CHES-014 **refuses to overwrite it**. A symlinked input/output and permissive
files or directories are rejected.

## Validation and nonclaims

Before the English draft generator runs, the bridge:

1. Checks the correct `.olt-private/ches` input directory, private
   permissions, no symlinks, safe single-file size, strict JSON (no duplicate
   keys or non-finite numbers), original PDF metadata structure, explicit
   source prefix, per-verse locator sequence, source fragment count,
   unapproved/copyright restrictions, and the same source snapshot SHA
   recorded by the original importer.
2. Matches the stored **original PDF SHA-256, page count, byte length, exact
   original PDF URL, verse count and green typography span count** to a
   previously source-verified **public technical manifest pin**.
3. Reuses authentic OSHB/WLC Hebrew verse/token records and the existing
   minimal CHES-first English drafting functions to retain source-ID-specific
   tense and lexical review candidates without guessing word alignment.
4. Emits **only numeric counts and fixed status booleans** to stdout; private
   CHES English spans and unapproved draft text are in the locally written
   private draft only.

**Important distinction:** The bridge compares *stored PDF SHA-256 metadata*
against an earlier trusted source pin. It does **not** have the original PDF
bytes and therefore **cannot rehash or independently authenticate those
original bytes now**. It also does not independently re-fetch the original
929-chapter index, audit the complete local archive, certify any
CHES-English ↔ Hebrew/Aramaic word or morpheme alignment, apply all grammar
rules, approve the final OLT translation, or grant redistribution rights.

As with the original English pilot, a mechanical concatenation of green PDF
English fragments is *not* yet a finished English biblical verse. Owner
choices (e.g., strict wayyiqtol English simple past, shaped/made/firmament)
are retained as **evidence-backed pending candidates**, not silently
substituted for unverified source glosses. All English output remains
`UNREVIEWED_PRIVATE_ENGLISH_WORKING_DRAFT` and
`publication_status=BLOCKED`.

## Testing and follow-on work

GitHub Actions runs synthetic English-gloss fixtures for all fourteen pinned
source scopes while consulting the real pinned original-language word records.
The regression suite checks modified hashes, approval flags, source index
metadata, conflicting drafts, symlinks, broad permissions, malformed JSON,
prohibited network use and source-text-free CLI results.

The separate source-PDF integration workflows remain responsible for real
original PDF re-verification. This offline bridge makes **no network calls**
and must not upload the owner's private 929-chapter corpus to GitHub.

**NEXT:** incrementally use the existing English rule/override layer on
explicitly verified verse-level evidence and provide a safe private review
process for unresolved cases; do not automatically assume that all 929
source files are linguistically aligned or replace this lightweight motor
with the superseded large lexical engine.
