# DANMEK-005 — Source-valid Hebrew order vs owner-preferred OLT English order

**Binding owner clarification (2026-10-31).** The private CHES JSON corpus is **not erroneous** because its interlinear English sublinear mirrors Hebrew word order. The owner never asked to correct Hebrew word order or rewrite the CHES source. The owner intends a **deliberate OLT English presentation style** that differs from the source's valid Hebrew-style ordering.

## Two distinct presentation layers

1. **CHES source view (immutable, source-faithful):** preserve the original imported `.olt-private/ches/*.json` including PDF green fragments, punctuation, grammar labels, articles, word order and geometry as extracted. The existing `scripts.ches_015_direct_private_reader` is a source reader, not yet a reordered English OLT translation.
2. **OLT preferred English reading (future separate derived view):** for a *demonstrably matched* subject and its verb in an authentic original verse, put the **explicit subject before the verb phrase**, retain the owner-preferred explicit pronoun (e.g. subject followed by `·he-is-...` as stylistically appropriate), and keep original morphological evidence inspectable. This is **not** a universal claim that Biblical Hebrew or CHES word order is wrong.

**Artificial illustration only (not a CHES or Bible quotation):** source order `and·he-is-buildingLeader»the·house`; desired derived English order `and Leader ·he-is-building »the·house`. The illustration captures the owner's *English-order intention*, not a claim that any original Hebrew text or token alignment has been checked.

## DANMEK-007 — No special divine-referent pronoun capitalization

**Permanent owner reversal (2026-10-31):** Preserve the English pronoun's ordinary casing even when the referent is God/the LORD. Do not add title-case `He/Him/His/Himself` on religious grounds; `·he-is-making` stays lowercase regardless of who is its subject unless ordinary sentence casing independently applies. The previous DANMEK-006 directive has been revoked and removed. This does **not** affect the separate English subject-before-verb order rule. [Binding cancellation](DANMEK_007_NO_DIVINE_PRONOUN_CAPITALIZATION.md).

## Safety and implementation contract

- Never modify, replace, normalize or re-import the owner's 929 original private CHES chapter JSON files for this purpose.
- Never globally move a fragment named after a person/deity or swap neighboring spans merely because they look like `verb + subject`. Existing green PDF fragments do **not** prove word boundaries, Hebrew morphological roles, or subject identity. Source-based correspondence must be verifiable at the individual relevant verse; otherwise leave the source rendering unchanged and report the case as awaiting OLT English-order transformation.
- Never treat a Hebrew-correct source ordering as a defect, corruption, PDF extraction failure or wrong translation. **The requested difference is editorial English order.**
- Standalone `c` (including repeated appearances) might be an interlinear morphology marker whose superscript/subscript presentation was lost by text extraction; do not strip it without checking source typography and role. Similarly, a repeated `the` might represent distinct Hebrew definite articles rather than duplicated extraction; do not automatically delete it. Keep a faithful source representation and build verified editorial changes in a separate view.
- The historic YLT 1898 remains the English authority for **eligible tense and overmodern noun choices** under the already-agreed bounded rules. It does not by itself establish a token-by-token subject/verb alignment or authorize wholesale Hebrew-order rewriting.
- English-view changes must be isolated in the versioned, private, non-destructive presentation layer. Public Git may contain only implementation and synthetic tests. Do not commit private CHES source lines, screenshots, or rendered verses. No redistribution / owner approval is inferred; publication remains `BLOCKED`.

## Current status and next implementation

**Policy locked; full-corpus reordering NOT IMPLEMENTED or VALIDATED.** Next coding step is to provide a separately labeled OLT English view and an auditable, source-supported subject/verb reorder for confirmed cases, with negative tests for ambiguous cases and Hebrew-original unchanged assertions. Do not apply a global regex to every chapter or conflate a CI pass on synthetic cases with owner-approved English Bible verses.
