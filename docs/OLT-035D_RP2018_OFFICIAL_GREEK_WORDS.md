# OLT-035D — Official RP2018 Greek words, Strong references and morphology

Date: 30 October 2026. **Engineering research only, never automatic Bible publication.**

## Actual original-source breakthrough

The earlier OLT-035B imported all **27 Greek NT canonical books** as genuine accented Unicode source VERSES, **7,953 rows**, from the official pinned Robinson–Pierpont 2018 v3.3.2 release. This did **not** supply authentic Greek word-level morphological annotation.

OLT-035D now additionally imports all **27 official EDITOR SOURCE files from `source/Strongs/*.BP5`**, not reconstructed from English, nor guessed by splitting accented Greek verses. These are the files the upstream explicitly identifies as its primary (unedited, Beta Code) source of Strong number references and Robinson morphological analysis. Every file is byte-identical to a pinned upstream Git blob (ByzTxt `v3.3.2` / commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`); source and code are published under public-domain licensing. Source editorial documentation: https://github.com/byztxt/byzantine-majority-text/blob/27a45ff1b7be6c17ccbfeac414f3f55732ae8e28/source/README.md .

**Measured original editor-source corpus (empty-slot distinction corrected after a genuine failing GitHub Actions test):**

| Scope | Original source count |
|---|---:|
| Official BP5 Greek NT books | **27** |
| Original BP5 verse positions | **7,957** (7,953 with Greek words + 4 empty placeholders) |
| Original Greek Beta Code word records with Strong numbers and morphology | **140,149** |
| Additional alternative Strong/morph pairs attached to an existing word | **28** |
| Previously imported canonical accented Greek Unicode verse rows | **7,953** |
| Empty BP5 verse positions absent from continuous Unicode source | **4** (zero Greek words in each) |

The **28 alternative parses are NOT 28 additional Bible words**. They are extra editor annotations attached to the relevant existing Greek word. Examples: Matthew 26:45 gives `kaqeudete` either `V-PAI-2P` or `V-PAM-2P`, and Revelation 3:17 supplies two case/gender readings for `oudenos`. Original annotations are preserved exactly, not arbitrarily collapsed into one 'verified' choice.

## Four source-text reference discrepancies — mandatory review

The original official BP5 files contain four **EMPTY verse-position lines**, with **no Greek word/Strong/morphology triples**, whose references are **NOT** contained as ordinary rows in the derived Unicode `no-variants` continuous main text:

- **Luke 17:36**
- **Acts 8:37**
- **Acts 15:34**
- **Acts 24:7**

These are **structural versification placeholders, not four additional passages of Greek text**. The source has 7,957 reference slots but 7,953 nonempty BP5 Greek verse lines, the same number as Unicode Greek verse rows. OLT records the four empty positions explicitly, and still requires editorial/text-critical review before changing verse numbering or text. Never invent Greek words in those positions or silently alter the canonical text. The separately preserved ancillary Acts 24:6–8 and John 7:53–8:11 source files from OLT-035B are another textual layer and are **not automatically overwritten or spliced** by the new source parsing.

## Source identity and word-alignment honesty

Original BP5 provides `book reference + source Beta Code word + Strong number + editor morphology code`, but it does **NOT provide a universal immutable native ID on each original Greek word**. Therefore the new module creates an expressly **OLT-DERIVED WORD POSITION LOCATOR**, for example:

```text
rp2018-v3.3.2:Matt.1.1:w0001
```

This means “first word of the official pinned BP5 representation of Matthew 1:1”. It is deterministic, reproducible, version-scoped and unique within the imported source. It is **not represented as a native identifier issued by Robinson, nor an independently verified Greek lexical lemma**.

A Strong number is **the source editor's lexical reference**, not a guarantee that the associated original Greek dictionary lemma form, exact semantic meaning, owner translation or homonym classification has been reviewed. The upstream editor states that Strong references have been consolidated/modified and even acknowledges remaining possibility of errors. Retain exact original number as **an annotated number**, do NOT assume a literal English gloss.

The Beta Code word forms in `source/Strongs` are **unaccented**. The accented Unicode verse text comes from source `source/CCAT`, processed into the previously pinned Unicode CSV files. There is currently a verified **VERSE REFERENCE join**, but **NO word-to-word identity crosswalk between Beta Code and accented Unicode originals**, because spelling, accents, punctuation, word separation and variant inclusion may differ. Word-level Unicode surface remains `null`. Nothing from the English master lexicon or target-language translations is used to derive Greek word identities.

The compiler records source review as `IMPORTED_OFFICIAL_EDITOR_TAGS_NOT_INDEPENDENTLY_VERIFIED`; grammatical and lexical certification remains explicitly **NOT DONE**. Every actual Greek translation, target-language underword, Hebrew/Greek homonym selection and Scripture publication remains **BLOCKED**.

## Repository deliverables and commands

- `data/imported/nt/rp2018/strongs/*.BP5` — 27 byte-identical, official source files.
- `data/engine/olt_035d_greek_word_source_manifest.json` — per-book original file SHA-1 and byte length, exact word and alternative counts, four textual discrepancies, status barriers.
- `olt_core/greek_words.py` — read-only import/parser and full 27-book audit.
- `tests/test_olt_035d_official_greek_words.py` — positive and negative editor-source, parse-choice and publication tests.
- `.github/workflows/olt-035d.yml` — read-only Ubuntu CI (in addition to unfiltered required `foundation`).

```sh
python -m olt_core.greek_words --audit
python -m olt_core.greek_words --verse MAT Matt.1.1
python -m olt_core.greek_words --verse MAT Matt.26.45
python -m olt_core.greek_words --verse REV Rev.3.17
python -m unittest discover -s tests -p 'test_olt_035d_official_greek_words.py' -v
```

The output is **research JSON**, retaining editor morphology alternatives and the absence of independently verified word-to-Unicode alignment. CI PASS proves what the tests assert, not theological or philological correctness.

## Next research checkpoints

1. Verify the official source editor's Beta Code conversion and textual alignment against the original `source/CCAT` accented-master files; preserve original verse differences and passages.
2. Build a **cautious, reproducible Beta Code → accented Greek source-word crosswalk**, with exact match/mismatch reports and no invented identity. Do not accept alignment solely because two verse counts agree; 4 known reference differences and inline variants need explicit scrutiny.
3. Develop reviewed Greek lemma-form/sense and phrase boundaries using authentic Greek scholarly lexica and original editor provenance; distinguish root/concordance numbers from independent linguistic lemmas.
4. Propagate only adequately verified Greek original-language senses and name/meaning associations to the **English master research lexicon** (future OLT-036), then independently reviewed Amharic/Japanese/Icelandic/Chinese and other locale repositories.
5. Keep independent Greek source criticism, lexical approval, render QA, footer/footnote provenance and release authorization separate.

All existing owner-locked English Genesis verses, unique In/with underword, binitarian interpretive profile and name-meaning requests (God/Elohim → Mighty Governance; Noah → Rest) remain unchanged.

**There is NO claimed final Greek lemma dictionary, no independently signed-off morphology, and no Bible translation ready for release.**
