# OLT-037B — Review queue for Greek numeric-reference ambiguity

Date: 2026-10-30. **Research case inventory, not a philological conclusion or released translation.**

## Context and scientific unit of analysis

OLT-037A compared the entire hash-pinned RP2018 Greek NT word-source corpus
with the separately hash-pinned STEPBible/TBESG dictionary. The source was
**11,035 distinct dStrong records**, of which some share a numeric
portion. The editor's 140,149 original Greek word positions had:

- **127,610** original word occurrences with one numeric STEPBible candidate;
- **12,539** occurrences with two or more numeric STEPBible candidates;
- **0** positions without a numeric TBESG candidate.

OLT-037B groups the **12,539 occurrences** into review cases keyed
by distinct original RP2018 **numeric Strong references**.
A *numeric-reference group* is NOT necessarily a Greek lexeme, homonym,
a dictionary root, a semantic sense, a named entity, a translation unit,
or a single philological review decision.

## Verified sources and licenses (unchanged)

- Source Greek text and editor morphology: official 27-book
  Robinson–Pierpont 2018 ByzTxt `v3.3.2`;
  commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`.
  Pinned local original `source/Strongs` files and original accented
  Unicode CSVs are independently verified by OLT-035D and OLT-036.
- Lexicon candidates: STEPBible/TBESG, commit
  `be4191f0082aeedddb0eff0c02c966292b2bd641`,
  original Git blob SHA-1 `efe271a1dbb73fa01f8fa6e0f164c6687757a9ae`.
  The source is 4,736,912 bytes, UTF-8. Original lexicon is
  **CC BY 4.0** with attribution:
  **STEP Bible (www.STEPBible.org), originally based on work at Tyndale
  House Cambridge**. License: https://creativecommons.org/licenses/by/4.0/.
- The 4.7 MB original lexicon is downloaded in CI from the exact
  upstream commit, verified byte-for-byte against its Git blob before
  parsing, and not vendored into the OLT repository.

## Reproducible queue contract

`olt_core/greek_lemma_triage.py` walks all 27 preverified RP2018 NT
books, preserving the exact OLT-derived source word locator and Unicode
spelling. For each unresolved numeric reference, the generated case
preserves:

1. Native STEPBible **dStrong**, **eStrong** and **uStrong** fields,
   source row number, literal Greek candidate headword, source
   morphology category and the original brief gloss marked clearly
   **SOURCE ONLY — NOT AN OLT TRANSLATION**.
2. Count of RP2018 word occurrences, per-book original-source counts,
   raw editor morphology-code distribution, number of distinct Unicode
   inflected surfaces and up to four actual source word occurrences
   including verse, derived locator, original Unicode and Beta Code.
3. Whether candidate headword spellings are *literally different*
   (an orthographic observation only, never a claim of homonymy or
   correctness).
4. The explicit unresolved state and empty approval fields:
   `scientific_classification=NOT_YET_DETERMINED`;
   `homonym_vs_polysemy_vs_entity_distinction=NOT_REVIEWED`;
   `selected_dstrong=null`, `selected_greek_lemma=null`,
   `selected_lexical_sense=null`,
   `approved_english_master_entry=null`,
   `independent_philological_signoff=false`;
   `publication_status=BLOCKED`.

The queue prioritizes the most frequent *source occurrences* first,
then ascending numeric source reference. This is a **research workload
ordering**, not a significance, orthodoxy or certainty ranking.

A **separate** collection preserves all **28 official alternative
Strong/morphology source analyses**, with independent candidate dStrong
sets; they remain annotations on existing Greek words, not extra words.
The four BP5-only empty source verse placeholders are unchanged. No
manuscript variant is inserted or merged.

## Scientific limitations and next review procedure

The numerical Strong crosswalk may group together source dictionary rows
with the same written headword, different written headwords, multiple
semantic senses, names or grammatical categories. **The program must
not choose between them.** Raw morphology-frequency distributions are
the RP2018 editor's labels, **not newly certified linguistic analyses**.
The first four example words illustrate source provenance but do not
replace exhaustive philological evidence.

For each eventual linguistic decision, require: independently cited
reference lexica, original Greek contextual examples, explicit
lexeme/headword identity reasoning, separate sense selection and
documented reviewer and owner approval. Keep any future decisions
separate from this immutable source-evidence queue. Do **not** use
English dictionary glosses as an automatic translation pivot.

## Reproduction and fail-closed gates

```sh
python scripts/fetch_olt_037_tbesg.py --output /tmp/OLT037-TBESG.txt
python -m olt_core.greek_lemma_triage --source /tmp/OLT037-TBESG.txt --summary
python -m olt_core.greek_lemma_triage --source /tmp/OLT037-TBESG.txt --case 26
python -m olt_core.greek_lemma_triage --source /tmp/OLT037-TBESG.txt --verify-checkpoint
OLT037_TBESG_PATH=/tmp/OLT037-TBESG.txt python -m unittest discover -s tests -p 'test_olt_037b_greek_lemma_triage.py' -v
```

The `--case` command works only for numbers that are actually present
in the ambiguous-reference review queue, not necessarily all Strong
numbers. The `--verify-checkpoint` command requires a committed
identical JSON snapshot under
`data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json`.
All unverified source mutations, reordered or changed word positions,
missing source evidence, or independently approved translations must
fail rather than pass automatically.

The independent `.github/workflows/olt-037b.yml` enforces the
pinned-source fetch, negative controls and a full 27-book reviewer queue
audit on Ubuntu. Required `foundation` remains unfiltered and always
runs on pull requests.

**Acceptance means reproducible source-based *review backlog*,
not published Greek scholarship, canonical lemma assignments,
master English translations or locale Bible chapters.**
