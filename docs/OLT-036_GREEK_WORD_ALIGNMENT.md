# OLT-036 — RP2018 Greek BP5 / accented Unicode position crosswalk

Date: 2026-10-30. **Source-bound engineering comparison; NOT independent philological approval or permission to publish Scripture.**

## Scope and underlying evidence

This checkpoint joins two already imported and independently Git-hash-validated
representations from the **same** upstream Robinson–Pierpont 2018 revision
(ByzTxt `v3.3.2`, commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`):

1. The editor's 27 `source/Strongs/*.BP5` original **unaccented** Beta Code
   source files containing a source-verse word order, a Strong reference
   and one or more editor morphology analyses.
2. The 27 pinned accented Unicode `csv-unicode/ccat/no-variants/*.csv`
   continuous verse-text files, derived upstream from the CCAT layer.

The source publisher describes the BP5 and CCAT layers and their conversion
differences in its [official source README](https://github.com/byztxt/byzantine-majority-text/blob/27a45ff1b7be6c17ccbfeac414f3f55732ae8e28/source/README.md).
Both layers ultimately belong to the same source edition: matching them is
**not** independent manuscript collation or verification of the editor's
morphology.

The OLT-derived locator `rp2018-v3.3.2:Matt.1.1:w0001` remains an OLT
word-position key, **not** a native publisher token ID.

## Alignment algorithm — deliberately strict

For each of the 27 books:

- Verify both files against the pinned upstream Git blob SHA and source manifest.
- Compare **the identical source verse reference**, never guess which
  numbered verse it refers to.
- Tokenize the original accented Unicode text by contiguous Greek-script
  letters, treating spaces, typographical apostrophes, paragraph markers and
  punctuation as boundaries. Preserve **exact source Unicode surface and
  character offsets**. Do not rewrite the imported Unicode verse itself.
- Transliterate the documented unaccented source Beta Code:
  `a α, b β, g γ, d δ, e ε, z ζ, h η, q θ, i ι, k κ, l λ,
  m μ, n ν, c ξ, o ο, p π, r ρ, s σ, t τ, u υ, f φ, x χ,
  y ψ, w ω`. Unknown notation is an error, not an approximation.
- Compare positions only when the two verses have **the same number of words**.
  Then require **every positional word pair** to have identical values under
  the finite normalization described below. Reject the entire verse if
  the count, spelling, reference or order differs: no fuzzy/partial join.
- Keep all Strong references and editor morphology codes **exactly as imported**.
  The 28 extra analyses still belong to their existing 28 annotations on
  source words, not to 28 additional word positions.

### Crucial limitation: orthographic comparison is lossy

The source `source/Strongs` representation lacks the Greek accent,
breathing, diaeresis and **iota subscript** information present in the
accented Unicode representation. OLT's explicit `OLT-036-RP2018-BP5-UNICODE-V1`
comparison therefore ignores **only** these Unicode combining marks
after NFD normalization:

| Unicode mark | Effect in comparison |
|---|---|
| U+0300, U+0301 | grave, acute |
| U+0313, U+0314 | smooth, rough breathing |
| U+0342 | Greek circumflex |
| U+0308 | diaeresis |
| U+0345 | Greek iota subscript (**lexically/orthographically significant**) |

Final sigma `ς` is compared as `σ`; all other consonants and vowel
bases remain required. Other combining marks fail closed. **Discarding
U+0345 in the comparison is not equivalent to proving the original
accented spelling.** It merely acknowledges an orthographic feature
that the unaccented BP5 representation cannot encode. OLT records the
exact accented Unicode word, a boolean marking subscript presence, and
the original word span; it never treats the lossy form as a scholarly lemma.

For example, source `gaiw` and Unicode `Γαΐῳ` compare as `γαιω`.
The actual Unicode `Γαΐῳ` is still preserved, and the subscript is
flagged. **No English definition is generated or certified** by this join.

## Corpus constraints

| Invariant | Required count |
|---|---:|
| NT source books | 27 |
| BP5 original verse slots | 7,957 |
| Unicode continuous verse rows | 7,953 |
| Source word-position records expected to align | 140,149 |
| Extra morphological alternative pairs preserved | 28 |
| Original source-only empty positions | 4 |

The four empty BP5 source positions remain **Luke 17:36; Acts 8:37,
15:34 and 24:7**. They have **zero** source Greek words and no
corresponding Unicode continuous verse. This checkpoint does not fill them
or splice the separately imported `PA` / `ACT24` ancillary sources.

### Output safety model

Aligned records contain both source-form fields:
`beta_code_word_form` and `accented_unicode_word_form`; the old editor
Strong/morphology annotations, exact Unicode character spans and OLT
source-derived ordinal; and `unicode_word_form_alignment =
MATCHED_POSITION_AND_LOSSY_NORMALIZED_ORTHOGRAPHY`.

Every report also records `publisher_native_word_ids_available=false`,
independent lexical/morphological review `NOT_DONE`, owner translation
`null` and publication `BLOCKED`. All future Greek lemma and English
lexical-sense work must carry out its own critical review. No Strong
number, normalization key or programmatic position match can by itself
become an approved dictionary entry, homonym, translation, or doctrine.

## Reproduction

```sh
python -m olt_core.greek_alignment --audit
python -m olt_core.greek_alignment --verse 3JO 3John.1.1
python -m olt_core.greek_alignment --verse MAT Matt.26.45
python -m unittest discover -s tests -p 'test_olt_036_greek_word_alignment.py' -v
```

The dedicated read-only GitHub Actions workflow `.github/workflows/olt-036.yml`
runs these tests and a full 27-book audit, in addition to the unfiltered
required `foundation` workflow. Negative tests intentionally change one
word, reverse order, change counts, use unsupported notation, or move source
references; the pipeline must reject such fabricated joins.

**Acceptance:** complete coverage of the pinned original sources and
failure on every introduced source-identity mismatch. Engineering PASS is
a source-position/orthography claim only; independent linguistic and
publication gates remain closed.

## Next checkpoint

Build a **separate, reviewed lemma-source inventory**, with provenanced
source-lemma form candidates and dictionary evidence linked to the now
verified OLT word positions. Avoid pivoting original-language data through
an unapproved English gloss when creating future language repositories.
