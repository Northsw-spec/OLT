# OLT-037 — Greek lemma source-evidence layer, phase A

Date: 30 October 2026. **Research candidates only. Translation and Scripture publication remain BLOCKED.**

## Decision and source

OLT-036 verified positions and explicitly lossy source-orthographic
correspondence for **140,149 original Greek RP2018 word records** across
27 NT books and 7,953 nonempty verses. This verifies the *source-position
join*, **NOT the original author's lemma form or its meaning**.

This next checkpoint introduces **independent lexicographic reference
evidence**, the `TBESG` (Translators Brief lexicon of Extended Strongs
for Greek) dataset provided by
[STEP Bible](https://github.com/STEPBible/STEPBible-Data), originally
based on work at Tyndale House Cambridge. The source is licensed
**Creative Commons Attribution 4.0 (CC BY 4.0)**, unlike the public-domain
Robinson–Pierpont text source. Exact credit:

> Greek lexicon data: STEP Bible (www.STEPBible.org), originally based on
> work at Tyndale House Cambridge; CC BY 4.0.

License: https://creativecommons.org/licenses/by/4.0/
The separate upstream TBESG dataset is continually maintained; OLT pins
**one exact revision** and records original source-byte provenance:

| Source invariant | Pinned value |
|---|---|
| Upstream repository | STEPBible/STEPBible-Data |
| Git commit | `be4191f0082aeedddb0eff0c02c966292b2bd641` |
| Source | `Lexicons/TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt` |
| Original Git blob SHA-1 | `efe271a1dbb73fa01f8fa6e0f164c6687757a9ae` |
| Source length | 4,736,912 bytes |
| Encoding | UTF-8 |
| License | CC BY 4.0 |

These values were obtained from the original upstream Git tree and
verified by `scripts/fetch_olt_037_tbesg.py` before parsing.
The original license-bearing file is intentionally **NOT copied into
the OLT Git repository**; CI fetches that exact immutable upstream
commit, validates its original Git blob, then discards its local copy
with the runner. The transformation and its limitations are documented
here; original source credits are included in API/CLI output.

## Important: different dictionaries can disambiguate differently

The RP2018 source `source/Strongs` supplies an **editor Strong number**,
not a STEPBible **dStrong** (disambiguated Strong) identifier.
The TBESG records have distinct native identifier fields:

- `eStrong` (extended Strong reference);
- `dStrong` (distinct source-key for split senses and entities);
- `uStrong` (unified Strong reference);
- original Greek lexicon form, transliteration, morphological category,
  English gloss and a definition.

OLT preserves each row under **its actual source dStrong**. Only the
**shared numeric part** of the original RP2018 Strong and STEPBible
dStrong is used to find *candidate reference records*. It is **not a
scholarly proof** that the candidate's lemma is the word's correct
dictionary form, that its morphology matches, or that its sense belongs
to this context.

When the shared number corresponds to:

- **Zero** TBESG records: `NO_NUMERIC_SOURCE_CANDIDATE`.
- **Exactly one**: `ONE_NUMERIC_SOURCE_CANDIDATE_NOT_REVIEWED`.
- **More than one**: `MULTIPLE_NUMERIC_SOURCE_CANDIDATES_UNRESOLVED`.

Even an apparently unique numeric candidate is **NOT automatically
approved**. Under all three cases, `selected_lemma=null`,
`selected_sense=null`, `approved_english_translation=null`,
`independent_review=NOT_DONE`, and
`publication_status=BLOCKED`.

The output retains literal TBESG lemma and gloss fields under names
explicitly ending in `_candidate` or `_EVIDENCE_ONLY`.
Never emit one of those glosses as a final OLT translation without
a separate source-based lexical review. Multiple dictionary meanings,
namesakes and homonyms must NOT be collapsed to the first row.

## Evidence fields and reproducibility

`olt_core/greek_lexicon.py` reads original TBESG TSV,
preserves every original source line number, all columns, every
disambiguated dStrong, and reports collisions. It refuses unknown/
malformed source identifier rows and duplicate dStrong IDs. The
full-corpus audit walks the already validated OLT-036 Greek word
positions, including RP2018 alternate analyses, without changing
the original BP5/Unicode words or inventing new verse positions.
Each alternative Strong/morphology pair retains **its own, separately
unapproved numeric-reference candidate set**, without generating an extra
Greek token or silently replacing the primary Strong annotation.

Run in a GitHub Actions Ubuntu runner or other environment with access
to GitHub raw source:

```sh
python scripts/fetch_olt_037_tbesg.py --output /tmp/OLT037-TBESG.txt
python -m olt_core.greek_lexicon --source /tmp/OLT037-TBESG.txt --audit
python -m olt_core.greek_lexicon --source /tmp/OLT037-TBESG.txt --verse 3JO 3John.1.1
python -m olt_core.greek_lexicon --source /tmp/OLT037-TBESG.txt --strong 26
OLT037_TBESG_PATH=/tmp/OLT037-TBESG.txt python -m unittest discover -s tests -p 'test_olt_037_greek_lexicon_evidence.py' -v
```

The dedicated `.github/workflows/olt-037.yml` verifies the source
hash, spelling provenance, lexical candidate enumeration and negative
cases, and additionally the normal required OLT `foundation`
regression suite. **GitHub Actions passing proves only the source
identity and the assertions actually tested**, never any publication
or language-science approval.

## Not done / next decisions

1. The initial `numeric reference -> candidate set` is a research
   crosswalk, not a philological lemma assignment.
2. Independently inspect dictionary lemmas, especially homonyms,
   exceptional derived root references, and different STEPBible vs
   RP2018 editorial assumptions; record decisions against specific
   original word-position IDs.
3. Independently research source morphology and contextual senses.
   Keep research suggestions separate from owner-reviewed English
   master lexicon words and all target-language translations.
4. Preserve the four known **empty** Greek BP5 verse placeholders
   and the separately retained ancillary source variants unchanged.
5. No Greek lemma, translated Scripture, or target-language release is
   licensed by this engineering checkpoint.

The full OLT multilingual rule remains **original-language first**;
an English master lexical reference is never a mandatory translation
pivot for future target languages.
