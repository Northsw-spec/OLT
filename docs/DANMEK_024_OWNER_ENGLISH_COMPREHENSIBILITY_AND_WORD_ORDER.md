# DANMEK-024 — Owner's binding English-comprehensibility and word-order quality gate

**Decision date:** 2026-11-01.
**Scope:** The private CHES-derived **DANMEK English Old Testament reading**,
without changing the source material or switching to a wholesale new translation.

## Latest owner clarification takes priority

The owner explained that they are **already pleased with DANMEK as an
English CHES-derived reading**, but after understanding what the 311-case
ambiguity work actually detects, **explicitly reaffirmed that the
English word order must still be checked and, when justified, corrected
until it is truly understandable**. Previous satisfaction is **NOT**
a command to stop grammar/reordering work, and is **NOT** a blanket
attestation that all clauses are currently grammatically correct.

**Working objective:** intelligible, grammatically defensible English
sentence order while preserving the owner's very literal, Early Modern
English style, source-bound semantics, contextual CHES sense choice and
all already established translation conventions. This is an
**editorial quality target**, not a new license to paraphrase or to
invent grammatical subjects.

## What is and is not the target

- **YES:** Continue investigating the **311 ambiguous English typography
  cases** with the available pinned Hebrew/Aramaic research evidence.
- **YES:** Assess other English readability issues that the existing
  regex candidate patterns may miss; 311 is not the complete set of
  potentially awkward English clauses.
- **YES:** Generate *private, versioned, evidence-backed proposed
  English renderings* with clear "proposed / unverified" status and an
  exact source reference, not merely more count-only reports.
- **YES:** Suggest **no change** where the existing English already
  satisfies the owner's readability and source-fidelity goal.
- **NO:** Equate the presence of two English regex patterns with a
  proven Hebrew grammatical error or a required English correction.
- **NO:** Equate a same-number OSHB verse or raw `HV`/`AV`
  morphology code with a verified CHES-to-original-word/subject
  alignment. The original-source candidate crosswalk still needs
  evidence.
- **NO:** Change `scripts/ches_015_direct_private_reader.py`,
  `scripts/danmek_011_owner_order.py`, or the **owner-verified
  DANMEK-013/014 English HTML snapshots** during research. Do not
  overwrite, mutate, retroactively regenerate, or claim the owner
  approved a new reading.
- **NO:** Treat all 311 cases as mistranslations or claim that the
  desired word order can always be inferred from morphology alone.

## Quality criteria for proposals

A proposed change must address a concrete comprehensibility issue;
preserve the original meaning and adjacent source-bound words; avoid
moving an object as if it were a subject; and show both its **actual
evidence** and its **remaining uncertainties**.

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

Build an independent **offline private readability-proposal pipeline**.
The next stage should:

1. Use the already owner-generated **DANMEK-020** 311-item queue and
   **DANMEK-022** private triage snapshot, *without modifying them*.
2. Discover specific English word-order alternatives only where the
   source English fragment structure supports a bounded proposal.
   Original-language morphology may be used as a *non-authoritative
   research hint*; do not invent one-to-one CHES↔OSHB pairings.
3. Emit a private, hashed, immutable side-by-side before/proposed
   comparison with **reason codes**, evidence status and an explicit
   "no change" path. Keep English word-order improvement and
   Hebrew-source grammatical certification as separate fields.
4. Include an **additional full-corpus readability diagnostic**:
   the 311 count comes from a narrow ambiguity detector and does not
   prove all other 22,833 CHES verse readings are readable.
5. Summarize only safe aggregate counts in CLI and GitHub; keep
   licensed CHES English, original-language tokens and any
   candidate lines strictly in `.olt-private/`.
6. Add synthetic regression tests for unsafe object movement,
   incomplete evidence, idempotence, source-chapter drift, strong
   no-overwrite controls and no false grammatical/editorial PASS.
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
