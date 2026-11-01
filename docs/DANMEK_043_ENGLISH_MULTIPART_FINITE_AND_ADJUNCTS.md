# DANMEK-043 — English multi-fragment predicates and complete intervening adjunct chains

**2026-11-02.** This stage only analyzes the owner's PRIVATE CHES English source ZIP. The corpus consists of **929 chapter JSON files and 23,144 English verse records**. It performs **no Hebrew, Aramaic, Greek, morphology, source-language verification, or CHES↔OSHB/WLC comparison**. No licensed CHES verse is committed to GitHub or GitHub Actions.

## Real corpus defect: a finite English verb can have three PDF fragments

A direct source-English census found **1,641** finite pronoun-verb tokens ending with a hyphen immediately followed by **one lowercase English lexical stem** and a separate **`ing` continuation fragment**. Example, with invented nouns:

`and·he-is- go ing-up ... Rowan`

The active parser in DANMEK-042 accidentally tested the single-lowercase-fragment branch *before* the two-part lexical continuation. Thus it recognized only `and·he-is- go`, leaving `ing-up` outside that predicate; `_predicate_lemma` could then return `go` instead of the combined English `going-up`.

The audit found **378 distinct lexical stem/continuation pair shapes** in this 1,641-instance English source class. These are **mis-segmented verb-group occurrences**, NOT 1,641 proven errors in the final English reading or 1,641 automatically corrected subjects. The new grammar parser prioritizes complete two-fragment continuations, composes an **internal role-classification-only** English lemma (e.g. `go` + `ing-up` → `going-up`), and preserves the exact original source pieces in private output.

This fix applies both to source forms beginning with a complete English finite pronoun token (`and·he-is-`) and to separately split pronoun prefixes where applicable. Independent finite clauses keep their own subject positions; no historical DANMEK reader is imported.

## Real CHES English subjects past locative and temporal phrases

Another complete source-English scan found **25 initial structures** consisting of a recognized finite predicate, a short English location/time adjunct (`there`, `here`, or the distinct two-fragment `in·` + `·first`), and a following name-shaped English nominal. The source sample includes:

- **Possible postverbal subjects** after an intransitive motion/state predicate (e.g. a person who dwelt or died *there*) or a fully separated progressive English verb + `in· ·first`.
- **Possible postverbal transitive agents** after `there`, but **only if an entirely separate explicit `»` object follows the complete named nominal**.
- **Counterexamples**: `serve there N other-ones` may contain a **direct object N**, not an agent; `building there N altar` lacks the separate object marker necessary for this rule; `called there N ...` can have a predicate/name complement; `N and ...` can be a coordinated nominal. These **must not be mass moved**.

Accordingly **25 is a pre-filtered source-shape count, not 25 grammatical corrections or verified errors**. The exact number of changed verses from v5 needs the current private CHES reader run and an output-diff audit; this document makes no unsupported applied-edit claim.

## DANMEK-043 implementation: no token-distance limit, strict English grammatical closures

1. Update only the **single active** `scripts/danmek_039_english_only.py` from revision v4 to v5. `_predicates` now returns a complete English finite verb span before any semantic-role recognition.
2. `_predicate_lemma` combines stem + `ing` continuation *only for classifying the English predicate*. It does **not** rewrite CHES words, replace lexical choices or edit the source JSON.
3. `_complete_english_adjunct_end` walks *one or more* already-complete English adverbial/prepositional units (e.g. `from·there`, `after·him`, `to·them`, `here`) without a fixed maximum number of intervening units. It accepts the two-source-fragment adverbial `in· ·first` only in the relevant upward-motion clause frame.
4. The next complete named noun phrase is considered a possible agent only if the English **intransitive role** permits it. Explicitly unclosed prepositions (`from`, `in·`, `to`) and embedded `NAME - finite` clauses prohibit the move.
5. Transitive verbs with location `there/here` can use `LOCATIVE_AGENT_BEFORE_SEPARATE_MARKED_OBJECT` only where a **second standalone object `»`** follows the entire nominal phrase. Naming/identification predicates and unmarked object contexts remain excluded.
6. Reuse DANMEK-039–042 protections for multiple independent clauses, direct objects, quotations, vocatives, title/kinship fragments, coordinated names, and full original `»` marker preservation. Historical readers are not imported. Regenerate **one private current English output**, not another versioned reader.

## Verification, honesty, and future work

The dedicated Ubuntu workflow must run `tests/test_danmek_043_multipart_english_verbs.py` together with all prior DANMEK and foundation regressions. Tests use **invented English tokens** only and check tri-fragment predicate recognition, compound motion roles, multiple closed adjuncts, transitive counterexamples, preserved source files, and correct current HTML output.

The 1,641 source predicate structures and 25 adjunct/name candidates provide **actual full-corpus evidence for this specific grammar change**. They are not a full parse of all English syntax in all OT verses, proof of correctness of every subject, or permission to publicly publish the licensed CHES-derived text. **Publication remains BLOCKED.**
