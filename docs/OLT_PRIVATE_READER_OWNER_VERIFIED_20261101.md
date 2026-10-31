# OLT private English reading — owner-verified baseline lock (2026-11-01)

**Status: OWNER VISUALLY VERIFIED — LOCKED BASELINE (DANMEK-013).**

## Owner acceptance

On **2026-11-01**, the owner inspected the locally generated **private Parrot OLT English HTML reading** based on the implemented DANMEK-008/011/012/013 display pipeline and expressly reported:

- The reading view is **correct and approved** in its present form.
- The displayed sentence and word spacing are correct. Apparent loss of spaces in text copied into a chat was a **copy/paste artifact**, **not an HTML-rendering defect**.
- No further reordering, extra word separators, normalization, or code change is needed in the accepted version.
- Owner expressly requested that this acceptance be **locked as verified** in the canonical GitHub project.

The protected repository **baseline commit at the time of acceptance** is
`8e10a1b97f8dd98ed9a59deba31e9683b236ac5c` (PR #93,
DANMEK-013). The preexisting GitHub Actions foundation suite passed on
that main commit: run
https://github.com/Northsw-spec/OLT/actions/runs/41251067681.
GitHub Actions validated engineering behavior using synthetic test data;
the **owner** supplied the separate visual acceptance of the real local
English reading.

The private HTML's exact local `snapshot-...` identifier, which source
chapter files were installed, and a complete corpus coverage audit have
**not been provided to public GitHub** and are **not claimed** here.
Only the owner could inspect their private source and local reader.
The source-private snapshots remain offline; no CHES source text, HTML,
original verses or other restricted material is committed.

## Locked behavior

The accepted English reading uses opt-in
`--olt-owner-approved-candidates` with the available optional
`--olt-display-faces` transformation and existing DANMEK-012 isolated
lowercase `c` fragment suppression. Earlier individually attested
DANMEK-009 source-syntax-reviewed mode remains a separate option.

**Do not retroactively alter this owner-accepted baseline.** Subsequent
formatting/syntax proposals must be independently versioned in new private
snapshots, implemented through protected PRs and GitHub Actions, and must
not silently mutate the accepted source-faithful or current private OLT
reading. Do **not** reopen the alleged missing-space issue based solely on
the pasted chat text. Keep original CHES JSON bytes unchanged.

## Later independently verified presentation (DANMEK-014)

The owner subsequently personally verified the separate DANMEK-014 view,
which only expands removal of standalone lowercase c markers. This does
**not** change or supersede the validity of this earlier DANMEK-013
checkpoint. Both accepted source-code baselines remain separately locked.
See [DANMEK-014 owner-verification lock](OLT_PRIVATE_READER_OWNER_VERIFIED_DANMEK014_20261101.md).

## Scope of acceptance — do not overstate

- **YES:** The owner visually inspected and explicitly approved the current
  locally rendered private English **reader presentation**.
- **YES:** The exact implemented display baseline at the above code commit
  is frozen as a stable checkpoint.
- **NO:** This does not amount to grammatical certification of every
  Hebrew/Aramaic subject, word-to-source alignment, verification of
  all 929 OT chapters, or a completed original-language translation.
- **NO:** This does not constitute personal approval of the complete
  66-book English Bible or permission to publish source-derived text.

The binding OLT-ENGLISH-FIRST-001 release gate remains:
**English translation complete: NOT DONE. Complete 66-book English
translation: NOT DONE. Final full-text owner approval: NOT DONE.
Publication: BLOCKED.**

This file records the owner's real acceptance without claiming any
unperformed local or linguistic verification.
