# DANMEK-040 — Direct CHES English finite-clause and delayed-subject audit

**2026-11-01.** This research used the private CHES English ZIP supplied by the owner, with **929** JSON chapters and **23,144** English verse records. No Hebrew, Aramaic, Greek, morphology, lemma, OSHB/WLC or original-language comparison was performed. No licensed verse text is stored in this public report.

## High-severity correctness defect in DANMEK-039 v1

The old `DISTANT_RELATIVE_CLAUSE_SUBJECT` heuristic searched forward from an outer finite predicate after an `as·which` marker and treated a name near another finite verb as the **outer** predicate's subject. That was a **grammatical role misattachment**: the post-relative name may belong to the embedded predicate. This is not repaired by allowing longer searches or adding more names.

A direct English-only source-fragment scan identified **71** outer-finite/relative-anchor positions. **Zero** matched the particular synthetic `relative + name + '-' + another finite` rule. The old rule provided no demonstrated real-corpus coverage and had a demonstrable false-attachment risk. **Removed.**

The replacement parses the embedded English finite predicate itself. It can then attach a syntactically supported name to **that** verb, without lifting that name into the matrix clause. Tests include a 150-fragment intervening relative context to ensure a long distance alone never licenses an incorrect move.

## Actual split-predicate counts from private CHES

The English fragment stream contains:

| English-only observation | Source-fragment count |
|---|---:|
| Explicit separate pronoun-prefix fragments (`he-`, `she-`, `they-`, `and·he-`, etc.) | 5,019 |
| Pronoun-prefix fragments immediately followed by a complete lowercase lexical continuation | 4,322 |
| Further accepted two-lexical-fragment split predicates | 264 |
| **New split-finite verb groups identifiable by the new source fragment parser** | **4,586** |

Combined with **37,577** previously recognized complete English finite groups, the independent source-only classifier recognizes **42,163** groups of the supported shapes. These numbers are **English predicate structure counts**, not grammatical error counts, distinct subject counts or actual text edits.

In the narrower `he-`/`she-`/`they-` subset (excluding `and·` forms), the source exhibited **91** split verb + single named nominal + standalone object marker cases, **30** speech verb + named nominal + recipient cases and **10** split verb + attached marked pronominal object + following named nominal cases. The last class requires stronger whole-phrase guards before an actual reorder; the generic parser accepts only complete, non-coordinated subject groups.

## Grammar and corruption prevention

- `scripts/danmek_039_english_only.py` remains the **only active** DANMEK engine. It is entirely Python-standard-library code and imports no previous readers or original-language source modules.
- Add direct support for English `he-` + `instructed`, `and·he-` + `spoke` and syntactically supported two-piece lexical predicates. These are original English CHES source fragments, not extracted or retranslated Hebrew words.
- A named subject follows **its own** finite predicate, not an unrelated head in an outer clause.
- Marked `»` objects and speech-recipient `to` roles support restricted English subject-position analysis. A marked object pronoun may precede a **complete** postposed agent phrase; the object marker remains after the predicate in the derived reading.
- **Reject incomplete subject groups:** a single name followed by `and·` plus a coordinated name/relative, a title, kinship or `-of` noun phrase may not be truncated into a one-token subject. This applies even when an object marker is present.
- A capitalized noun after a transitive verb is still *not* evidence of grammatical subjecthood on its own. Uncertain cases remain unchanged and counted.
- Update aggregate CLI diagnostics: `english_finite_predicates_seen` and `english_split_finite_predicates_seen` are separate from `subject_moves_applied` and `unresolved_subject_roles`.
- Synthetic tests cover multiple embedded clauses, delayed object-marked subjects, 150-token context, and negative transitive, infinitival and coordinated cases. No actual CHES verses appear in public tests or logs.

## Limits

This is a real generalization of the single English grammar engine, **not a complete dependency parser** for every CHES sentence. Correct subject/verb association for unmarked distant complements, nested participles and coordinated nominal clauses can remain unresolved. The independent local source scanner supports the pattern census, but actual runtime applied/edit counts should come from the `DANMEK-039` command against the private ZIP or original local chapter directory.

Original CHES and current publishing permissions remain unchanged; only a private derived reader is built on explicit request. Public publication remains **BLOCKED**.
