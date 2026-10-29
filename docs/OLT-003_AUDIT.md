# OLT-003 — Corpus audit and exact lexical identities

This phase does not make a full OLT English lexicon automatically; it establishes
**an auditable identity for every distinct OSHB lexical component actually used in the MT**.

## Why this phase matters
In OSHB `lemma="1254 a"` and `lemma="1254 b"` are not guaranteed to mean
the same lemma, even when they share Strong's base number `1254`.
The initial import's numeric summary grouped both under `1254`.
This source-derived audit preserves the **entire exact lemma identifier** in a
distinct registry (the original raw `lemma` is always preserved in book data).
No dictionary sense is invented based only on consonantal spelling.

Prefix-only components such as `b`, `c`, `l`, `m` are stored separately,
not fabricated into Strong-number lemmas. A word may carry multiple slash-separated
morphemes: the report therefore distinguishes *word tokens* and *lexical components*.

## Source morphological tags
Actual OSHB morphological codes include `HC/Vqw3ms`:
- `H`: Hebrew.
- `C`: conjunction segment.
- `V`: verb segment.
- `q`: Qal stem in this example.
- `w`: sequential-imperfect / wayyiqtol **source annotation**.
- `3ms`: third-person masculine singular.
Compare qatal `HVqp3ms` and sequential perfect `HC/Vqq3cp`.
The OLT-TENSE-001 English **Simple Past** rule applies to independently checked
source tags; a tag alone is not a certification of ancient discourse context.

The OSHB source includes **Aramaic** occurrences, which are separately counted from
Hebrew where its morphology codes indicate `A`. This does not replace language
verification where ambiguous.

## Created datasets
- `data/quality/observed_exact_lemmas.json`: all observed, fully qualified
  lemma identifiers + occurrence counts + English approval still empty.
- `data/quality/corpus_audit.json`: exact coverage, prefix-only cases,
  source-tag verb form counts, and unresolved ambiguity.
- `data/quality/genesis_01_morphology.json`: all 31 verses and each actual
  source word with raw and parsed morphology, preliminary wayyiqtol flags
  and explicit `NOT_YET_ALIGNED` placeholders for English.

## Limits
The data is derived directly from the pinned OSHB word tokens, but the
underlying OSHB editorial morphology is imported, not independently checked
against another academic source. No English verb or noun is validated by this
ledger until actual token alignment and philological review happen.
