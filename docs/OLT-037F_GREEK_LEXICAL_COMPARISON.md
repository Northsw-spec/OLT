# OLT-037F — Source-cited original Greek contextual lexical comparison

**Scope:** engineering-verified, source-cited evidence for Greek lexical research.
**Not:** completed philological analysis, a contextual word-sense decision,
an approved English lexical choice, or a published Bible translation.

## Scientific question

Previous checkpoints pinned these original sources:

1. **Original NT Greek text and context**: Robinson–Pierpont 2018
   ByzTxt v3.3.2, 27 Greek NT books, 140,149 original source word positions,
   with original accented Greek and raw editor morphology, a fixed
   unicode-word/verse span, and OLT-derived locators. OLT-037C's
   source-context checkpoint contains 2,315 occurrences of numeric
   G3004 and 1,287 of G3754 (and 136/53 selected source examples).
2. **STEPBible TBESG**, CC BY 4.0, with separate editor dStrong
   subidentifiers; no numeric source join is a verified lexeme or
   synonym/homonym relation.
3. **Abbott-Smith**, *A Manual Greek Lexicon of the New Testament*
   (1922). Its original Greek NT dictionary's digital TEI and markup
   are described as **public domain** by the separately Git-pinned
   upstream README. The original TEI source is NOT the RP2018 edition
   and its dictionary Strong labels are NOT native RP2018 word IDs.
4. **Perseus Liddell–Scott–Jones (LSJ)**, *A Greek-English Lexicon*,
   original TEI-XML data **CC BY-SA 4.0**, via pinned original Git
   commit and Git-blob SHA values, and explicit attribution to
   Liddell, Scott and Jones and Perseus Digital Library, Tufts
   University. LSJ primarily serves classical Greek lexicography;
   it does not independently establish meaning in the Koine Greek NT.

Abbott-Smith and LSJ are NOT independent statistical votes about a
meaning, since historical lexicographical sources often depend on
their predecessors.

## Specific original LSJ entries subject to research

The original upstream Perseus XML shards are downloaded in ephemeral
GitHub Actions and verified against their original byte lengths and
immutable Git blob checksums. OLT-037F examines **only** these
unapproved candidate source entries:

| RP2018 research number | LSJ original source ID | Native original TEI key | Status |
|---|---|---|---|
| G3004 | `n62204` | `le/gw1` | Source entry only, unreviewed |
| G3004 | `n62205` | `le/gw2` | Source entry only, unreviewed |
| G3754 | `n75695` | `o(/ti^` | Source entry only, unreviewed |

These are exactly the source native entry IDs and original TEI
dictionary key strings found in OLT-037D/E. The `^` source
notation on `o(/ti^` is why the previous literal `o(/ti` search
failed. The original exact search failure remains present in
the earlier frozen evidence; do **not** rewrite historical source
evidence just because a new, lossy diagnostic found a candidate.

The source scanner isolates the *original TEI entry body* between
the literal source opening `<entryFree>` tag and its own closing
`</entryFree>` tag. It rejects duplicates, missing keys and
inconsistent source boundaries. It records:

- original entry ID and original Beta Code-like source key;
- SHA-256 hash and Unicode length of the entry's complete original
  XML body, allowing later reviewers to detect unexpected edits;
- original `<sense>` tag count and a short sample of native `n`
  hierarchy labels — these are **source markup labels**, not
  independently approved Greek meaning categories;
- counts of source `<tr>`, `<bibl>`, `<ref>` and `<orth>` tags;
- **at most one very short original `tr` source excerpt per LSJ
  entry**, separately attributed as CC BY-SA 4.0
  **SOURCE ONLY — NOT AN OLT TRANSLATION**.

There is no untrusted DTD expansion, XML network entity resolution,
arbitrary LSJ definition copying, automatic semantic classification or
comparison score. The full original LSJ entries stay in the
unchanged licensed external files; researchers can consult their
exact original entries by source commit and entry IDs.

## Actual biblical Greek context

The script reads the *exact same* immutable OLT-037C Greek contextual
source dossier rather than synthesizing Bible verses from a dictionary.
It selects five original word/verse occurrences for G3004 and five
for G3754 from the existing independently pinned source sample,
based on deterministic original-source order, book variation, morphology
variation and observed Greek surface variation. It preserves:

- original source book, Greek verse reference and **full original
  accented Greek source verse text**;
- exact original accented word form, Unicode verse-string offset,
  raw source editor morphology annotation and source ordinal;
- explicit OLT-derived word locator (NOT a publisher-native word ID);
- original 037C selection reasons and null unapproved fields.

Each Greek original verse/word substring is checked at its original
Unicode character span. Neither the lexicon source's words nor an
English translation is used to reconstruct the actual Greek verse.

## What OLT-037F proves — and what it cannot prove

Engineering can prove that the pinned source files exist, the relevant
source dictionary entries and primary Greek source excerpts are
correctly retained, and the same evidence packet can be rebuilt
byte for byte. It cannot prove that `G3004G` and `le/gw1` name
the same lexical sense, that one English short gloss is correct
in a cited verse, that an original editor morphology code is
independently scholarly certified, or that any biblical translation
is acceptable.

The resulting report
[`data/quality/olt_037f_source_cited_greek_lexical_comparison.json`](../data/quality/olt_037f_source_cited_greek_lexical_comparison.json)
has exactly **two** unapproved source comparison dossiers and **ten**
unaltered source Greek verse/word examples, covering the same 2,315
and 1,287 original word occurrences. All human sense decisions,
human reviewer identity, dates, owner editorial approval and target
English lexical entries remain empty or explicitly false.

Any future **qualitative lexical judgment** must separately cite
specific independently inspected source entry locators, original
Greek syntax and literary context, text-critical alternatives,
opposing interpretations and appropriate Koine scholarly studies.
It must bear a genuine human reviewer identity/date and owner
translation decision, **not simulated certification or an inferred
CI PASS**.

## Reproduction and safety gates

```sh
mkdir -p /tmp/olt037f-lsj-source
python scripts/fetch_olt_037d_lsj.py --output-dir /tmp/olt037f-lsj-source
OLT037F_LSJ_DIR=/tmp/olt037f-lsj-source \
  python -m unittest discover -s tests -p 'test_olt_037f_lexical_comparison.py' -v
python -m olt_core.greek_lexical_comparison \
  --lsj-dir /tmp/olt037f-lsj-source --audit
python -m olt_core.greek_lexical_comparison \
  --lsj-dir /tmp/olt037f-lsj-source --verify-checkpoint
```

`.github/workflows/olt-037f.yml` uses read-only permissions and a
pinned external source fetch. Dedicated negative-source tests and
source-integration checks must pass. Once the CI-generated report
is first frozen and committed, the final PR and merged `main` must
regenerate it **byte for byte**. Unfiltered `foundation` regression
is also required.

**Release gate: BLOCKED. Contextual Greek lemma, sense, English master
lexical equivalent and target-language Bible verses are NOT approved.**
