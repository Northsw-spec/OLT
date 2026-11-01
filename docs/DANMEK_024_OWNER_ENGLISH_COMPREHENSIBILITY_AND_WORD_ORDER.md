# DANMEK-024 — Owner's binding English-comprehensibility and word-order quality gate

**Decision date:** 2026-11-01.
**Scope:** The private CHES-derived **DANMEK English Old Testament reading**,
without changing the source material or switching to a wholesale new translation.

## DANMEK-026 — Latest owner decision: accept CHES, do not revalidate its Hebrew equivalents (2026-11-01)

**Binding engineering assumption (not an independently demonstrated philological
claim): CHES is accepted as authoritative for the English lexical choices and
the existing Hebrew/Aramaic correspondence in DANMEK's CHES-first reading.**
Do **not** spend engineering time comparing CHES words, lemmas, meanings or
their placement against the separately imported original-language corpus.
Do **not** require a verified CHES-to-OSHB/WLC crosswalk, original-language
word alignment, morphology inspection or Hebrew grammatical-subject
identification before evaluating **English grammar**.

The 311 historic ambiguity cases are English syntax-review candidates, **not**
311 suspicious Hebrew translations. Keep their existing private immutable
research records as historical evidence; stop the source-language alignment
investigation as an **active DANMEK-025 prerequisite**. English grammatical
review can use the actual CHES-derived English clause and English grammatical
evidence. Its default decision is NO_CHANGE; only proven defects may lead to
minimal, unapproved proposals. When evidence is insufficient, leave unchanged.

This does not claim that CHES has been externally proved infallible or that
the OT original-language scholarly editions should be deleted. Retain them for
distinct original-language research, narrowly authorized OLT lexical/tense
exceptions or future explicitly commissioned projects. Such work is **not**
a recurring certification of CHES's Hebrew fidelity, nor a prerequisite to
completing the DANMEK private English reader. All privacy, source-hash,
import-integrity, licensing and locked-snapshot safeguards remain mandatory.
The NT Greek work is independent of CHES OT.

## Latest owner clarification takes priority

The owner explained that they are **already pleased with DANMEK as an
English CHES-derived reading**, but after understanding what the 311-case
ambiguity work actually detects, **explicitly reaffirmed that the
English word order must still be checked and, when justified, corrected
until it is truly understandable**. Previous satisfaction is **NOT**
a command to stop grammar/reordering work, and is **NOT** a blanket
attestation that all clauses are currently grammatically correct.

**Working objective:** grammatically defensible and comprehensible English
that retains Hebrew-like word order, archaic cadence and the owner's very
literal, Early Modern English style, source-bound semantics, contextual CHES
sense choice and all established translation conventions. This is an
**editorial quality target**, not a new license to paraphrase or to
invent grammatical subjects.

## Latest owner correction — grammar defects, not stylistic polishing (2026-11-01)

**The default result is NO_CHANGE.** Preserve the order inherited from the Hebrew/
Aramaic source to the greatest defensible extent. Unusual English ordering,
marked fronting, repetition, dialect-like cadence, archaic constructions and
poetic prose are **intended features**, not automatically faults. Do not seek
modern, idiomatic, natural-sounding, fluent or stylistically smoother English.

**A correction proposal is permitted only when a specific English grammatical
error is supported by traceable evidence**, such as defective subject–verb
agreement, a genuinely missing grammatical constituent, a wrong subject/object
role or an unparseable construction that materially obscures meaning. Detection
of odd word order, a regex match or low readability score alone is insufficient.

When an error is suspected but cannot be demonstrated reliably, classify it
**GRAMMAR_UNRESOLVED_NO_REORDER**, preserve the wording and request targeted
linguistic review; do not declare a grammatical pass. A machine-proposed repair
is still unapproved until source-sensitive review and owner acceptance.
Preserve the existing owner-approved DANMEK-013/014 reader and snapshots;
this rule is prospective and does not silently revoke past approvals.

## What is and is not the target

- **YES:** Continue investigating the **311 ambiguous English typography
  cases** strictly as English-grammar candidates, **without** any routine
  comparison of CHES with pinned Hebrew/Aramaic sources.
- **YES:** Assess other English readability issues that the existing
  regex candidate patterns may miss; 311 is not the complete set of
  potentially awkward English clauses.
- **YES:** Generate *private, versioned, evidence-backed proposed
  English renderings* with clear "proposed / unverified" status and an
  exact source reference, not merely more count-only reports.
- **YES:** Default to **no change** when the current English is grammatically
  defensible and comprehensible even if unusual, Hebraic, archaic or poetic.
- **NO:** Equate the presence of two English regex patterns with a
  proven Hebrew grammatical error or a required English correction.
- **NO:** Equate a same-number OSHB verse or raw `HV`/`AV`
  morphology code with a verified CHES-to-original-word/subject
  alignment. Such an alignment is **not needed or to be pursued** in
  DANMEK's English grammar-review workflow.
- **NO:** Change `scripts/ches_015_direct_private_reader.py`,
  `scripts/danmek_011_owner_order.py`, or the **owner-verified
  DANMEK-013/014 English HTML snapshots** during research. Do not
  overwrite, mutate, retroactively regenerate, or claim the owner
  approved a new reading.
- **NO:** Treat all 311 cases as mistranslations or claim that the
  desired word order can always be inferred from morphology alone.
- **NO:** Reorder solely because English sounds unusual, lacks modern fluency,
  or a readability heuristic favors a more idiomatic alternative.

## Quality criteria for proposals

A proposed change must target an **evidenced English grammatical defect**;
preserve original meaning and adjacent source-bound words; avoid moving an
object as if it were a subject; and show both its **actual evidence** and its
**remaining uncertainties**. Mere stylistic awkwardness never suffices.

The unchanged current reading stays the approved reference baseline.
The proposal can be mechanically suggested, but it cannot be promoted
to a verified grammatical repair or added to the approved reader
without a separately tracked linguistic check and the owner's
explicit editorial approval. No guessed subject mapping, tense change
or word-order movement qualifies as a proven source-aligned fix.

The English must preserve:
- literal/source-faithful wording where reasonably intelligible;
- the existing Early Modern English / KJV-like register;
- the owner-constrained subject-verb clarity and explicit English
  subject rendering, where original-language evidence permits;
- the globally defined tense/wayyiqtol policy and owner lexical
  choices;
- ordinary English pronoun capitalization only, **not** special
  capitalization for a divine referent;
- the original CHES English semantic choice as default, unless
  an individually supported, owner-authorized exception exists.

## Next development: DANMEK-025

Build an independent **offline private grammar-defect detection and triage
pipeline**. **NO_CHANGE is the default**, not a fallback after automatic
stylistic rewriting.
The next stage should:

1. Use the already owner-generated **DANMEK-020** 311-item queue and
   **DANMEK-022** private triage snapshot, *without modifying them*.
2. Flag specific, evidenced English grammar defects first (subject, verb,
   agreement and syntactic roles). Generate a narrowly bounded word-order
   proposal **only after** that grammar threshold is satisfied. Preserve
   original order in cases that are unusual but grammatical.
   Use English syntactic evidence only for this grammar workflow; do not
   pursue original-language morphology or CHES↔OSHB word pairings as a
   validation step.
3. Emit a private, hashed, immutable side-by-side before/proposed
   comparison with **reason codes**, evidence status and an explicit
   "no change" path. Do **not** make Hebrew-source grammatical
   certification part of DANMEK-025.
4. Include an **additional full-corpus grammatical-defect diagnostic**:
   the 311 count comes from a narrow ambiguity detector and does not
   prove all other 22,833 CHES verse readings are grammatically sound.
   A heuristic suspicion is not an error finding or permission to edit.
5. Summarize only safe aggregate counts in CLI and GitHub; keep
   licensed CHES English, original-language tokens and any
   candidate lines strictly in `.olt-private/`.
6. Add synthetic regression tests for **unusual but acceptable Hebraic
   syntax producing NO_CHANGE**, unsafe object movement, incomplete evidence,
   idempotence, source-chapter drift, no-overwrite controls and no false
   grammatical/editorial PASS.
7. Require explicit separate review before applying **any** proposed
   change to the approved DANMEK reading.

Automated quality triage is meant to reduce repetitive manual review,
not to claim language understanding or evidence it does not have.
GitHub Actions on Ubuntu is sufficient for **engineering tests**,
but cannot independently read the private CHES material or certify
the true linguistic quality of all 311 cases.

## Release/approval state

- Existing owner-approved English **presentation baseline**: **LOCKED**.
- English grammar/readability quality review: **ACTIVE, NOT COMPLETE**.
- 311 English ambiguity cases: **triaged technically, NOT all
  linguistically resolved**.
- Every complete English Bible translation approved: **NOT DONE**.
- Copyright/derived-publication rights: **NOT ESTABLISHED**.
- Public publication: **BLOCKED**.

The binding machine-readable mirror is
[`data/policy/danmek_024_english_comprehensibility_owner_priority.json`](../data/policy/danmek_024_english_comprehensibility_owner_priority.json).
