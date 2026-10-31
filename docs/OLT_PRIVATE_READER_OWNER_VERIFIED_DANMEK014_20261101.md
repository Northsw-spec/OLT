# OLT — DANMEK-014 owner-verified private reader baseline (2026-11-01)

**Status: OWNER VISUALLY VERIFIED — LOCKED.**

## Specific owner approval

On **2026-11-01**, after building and opening the updated private
Parrot OLT reading, the owner expressly replied: **“godkänt. verifierat.”**
That is a direct **human visual acceptance** of the **DANMEK-014** English
reading, including the display-only removal of isolated lowercase
`c` markers (`c`, `c c`, `cc`), while keeping the previously
accepted DANMEK-013 subject-before-verb English display.

**Source-code reference:** protected `main` commit
`2e56f446b707226c584269c88c50efab37e0ffc2`, introduced by
[PR #95](https://github.com/Northsw-spec/OLT/pull/95).
GitHub Actions [run 41252311520](https://github.com/Northsw-spec/OLT/actions/runs/41252311520)
passed on that exact protected main commit.

The owner's local HTML content, CHES originals, exact private snapshot ID,
paths and real-corpus per-verse evidence were **not** shared to this public
repository. We therefore record **personal owner inspection and sign-off**,
not a fabricated verification of all source chapters or a reproducible
public hash of the owner's private HTML.

## Locked presentation guarantees

- Preserve the owner-approved English order corrections from the DANMEK-013
  pipeline, with the permanent rule **no special divine-pronoun capitalization**.
- Keep the owner-requested `sur faces` → `faces` simplification in the
  separate OLT English view when `--olt-display-faces` is enabled.
- In the opt-in `--olt-owner-approved-candidates` view, hide only separate,
  whitespace-delimited lowercase `c` markers and their duplicates,
  including those in mixed source fragments. Do not remove `c` inside words,
  upper-case `C`, or punctuation-attached `c.`, `c·`, etc.
- Preserve whitespace, English words, original CHES JSON and source-faithful
  readings. The earlier [DANMEK-013 accepted baseline](OLT_PRIVATE_READER_OWNER_VERIFIED_20261101.md)
  remains separately locked and intact.
- Do not silently change this accepted display. Any future presentation
  change requires a distinct source-revision-derived immutable private
  snapshot, protected PR, GitHub Actions, and **separate owner inspection**
  before describing that new version as owner-verified.

The **DANMEK-015 synthetic regression tests** encode these accepted
presentation invariants so future coding errors cannot silently change
them without failing CI. They use invented example text; the real private
snapshot is not uploaded to GitHub or asserted to have been re-run in CI.

## Scope boundary

**Owner approved: the local English reading's presentation.**

**Still NOT established:** 929-chapter completeness, Hebrew/Aramaic
subject syntax correctness, word-level morphology alignment, Greek NT
translation, completeness of the 66-book English Bible, final owner
approval of its translation, or rights for public distribution.

**OLT-ENGLISH-FIRST-001 remains binding: complete English Bible NOT
DONE; final full-text owner approval NOT DONE; publication BLOCKED.**

This is a checkpoint to **protect functioning work**, not permission
to freeze all future original-language or English-engine development.
