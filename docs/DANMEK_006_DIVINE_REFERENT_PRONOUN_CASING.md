# DANMEK-006 — Reverential capital letters for verified divine pronouns

**Owner style decision (2026-10-31):** In the *derived OLT English reading*, capitalize the **first letter** of pronouns that **refer to God/the LORD**. Examples: `·he-is-making` → `·He-is-making` if and only if that `he` refers to God; `him` → `Him`, `his` → `His`, and `himself` → `Himself` when their referent is the LORD/God. A human `he/him/his` remains lowercase except for independent ordinary English sentence capitalization. The referent matters, not whether God is also the grammatical subject of the clause: **`Him` may refer to God as object**.

## Scope and source of certainty

- CHES Hebrew-order JSON and the existing source-faithful offline reader stay **unchanged**. This is *editorial English presentation*, not a spelling, Hebrew grammar or source-data correction.
- Do not infer reference by a generic nearby `God`, `Elohim`, `LORD`, etc. A verse may contain human and divine pronouns, different antecedents, quotations and ambiguous references. Never globally title-case `he`/`him`.
- **Every changed occurrence requires an explicitly reviewed original-language/semantic referent annotation linked to that particular English verse and offset**. Without sufficient evidence, do not capitalize automatically and mark the passage for further review in the future OLT reading layer. The presence of a user-supplied annotation is *not independent original-language certification*.
- Only the **first** letter is uppercase, not entire words or an attached phrase. A verified `·he-is-making` becomes `·He-is-making`, without modifying `is-making`. The same principle applies to `Him/His/Himself`.
- Preserve deliberate English-order subject-first style, CHES contextual choices and the separate bounded YLT-1898 noun/tense decision policy.
- `c` grammatical markers and distinct `the` articles are unrelated and never automatically deleted by this change.

## Current engineering state

The small pure helper `scripts.danmek_006_divine_pronouns.capitalize_verified_divine_pronouns` supports explicit per-occurrence offsets via `VerifiedDivinePronoun`, with fixed validation errors, no I/O, synthetic-only negative tests, and preservation of all other letters. It is **NOT YET connected to 929 source chapters**, because their imported CHES green PDF fragments do not contain verified pronoun→divine antecedent links. Therefore **do not claim the full English text was capitalized**.

The helper is for a **future separately versioned private derived OLT English view**, never an implicit mutation of the CHES source reader. Source English text remains private and publication `BLOCKED` pending the same rights/review gates.
