# DANMEK-017 — Offline local source-index membership comparison for GT

**Goal:** Strengthen the already merged DANMEK-016 chapter/verse coverage
audit without modifying the **owner-verified, LOCKED DANMEK-014 English
HTML** or private CHES source records. An archive having 929 files across
39 filename prefixes by count does **not** establish that those are the
*correct* 929 chapter files.

## Method

The new command `scripts.danmek_017_private_source_index_membership`
accepts two separately existing, locally private inputs:

1. The previously validated `~/.olt-private/ches` CHES JSON chapter
   archive, which already stores a source-index SHA-256 in every chapter.
2. An **actual local copy of the source's OT PDF index HTML**, given
   explicitly with `--source-index`. The supplied file must be inside
   the user's `.olt-private` tree **outside the `ches/` source
   archive**, non-symlinked, permission 0600 or stricter and within
   the strict size limit. No index is downloaded automatically.

The tool reuses the strict offline original-index parser, requiring **929
individual PDF chapter links across 39 source filename prefixes**.
For each local CHES chapter, it validates the source JSON's existing
structure, requires the chapter's (filename prefix, chapter number)
to **exist in that supplied index**, and requires that its recorded
`source_original_index_sha256` exactly matches the supplied HTML bytes.
It then computes how many expected source-index chapters are absent,
broken down by source filename prefix. If a locally present chapter is
**not** in the supplied index, or its indexed SHA differs, the audit
**fails closed**. A second source-archive validation and a second read
of the index prevent silent reuse after inputs change.

The optional `--require-index-complete` gate fails when any indexed
chapter is not present locally.

## Strict evidence boundaries

- **YES:** The files observed in the private archive are consistent
  with the **supplied local index HTML** by chapter identity and SHA.
- **NO:** This is not independent authentication of the HTML file as
  the upstream site's current or historical authoritative index.
  Because the file itself is user-supplied, both a malicious/changing
  index and a forged chapter archive could be internally consistent.
- **NO:** This does not download/re-hash the original source PDFs,
  prove CHES words line up with Hebrew/Aramaic originals, independently
  certify book mappings, certify that an English translation is complete,
  or grant reproduction/publication permission.
- **NO:** A local file count, index count, or GitHub Actions passing
  does not constitute personal approval of all 66 books.

The output contains **only SHA-256 identity, numbers, boolean evidence
flags, and filename-prefix-level counts**. Never reveal the HTML itself,
licensed source text, private paths, Hebrew/English lines, or verse
references. The audit writes **zero** source or output files and makes
**zero** network calls. All public CI tests use a wholly invented
929-link/39-prefix index, not any original third-party HTML or CHES.

## Parrot operation

This command is relevant only **if the authentic index HTML is already
available privately**. The example index path is illustrative, not a
claim that a file currently exists there.

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" \
  -m scripts.danmek_017_private_source_index_membership \
  --private-root "$HOME/.olt-private/ches" \
  --source-index "$HOME/.olt-private/source-index.html" \
  --confirm-machine-readable-use-permission
```

When every indexed chapter is expected locally, add
`--require-index-complete`. With missing chapters, omit that flag so
the audit can still report the exact **aggregate** missing counts.

If no authentic, matching private index HTML is present, **do not
fabricate one or guess a filename**. The DANMEK-016 count-only audit
remains available until separately preserved source-index bytes can
be identified and verified. This step does not require user visual
feedback because it changes no accepted text presentation.

**Publication: BLOCKED.** **Original files: unchanged.**
**Independent source-index provenance: NOT VERIFIED.**
