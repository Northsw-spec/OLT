# OLT-037C — Original Greek contextual evidence dossiers

Date: 2026-10-30. **No source language form, lexical sense or English verse has been independently certified. Publication remains BLOCKED.**

## Research question and two explicitly named cases

In OLT-037B, 12,539 Greek original-source word occurrences were grouped
into 107 **numeric Strong reference** source cases. Those 107 numeric
groups were never scientifically established as 107 distinct lexical
identities or 107 Greek homonyms.

OLT-037C begins a more exact, reproducible *human review dossier*
for two of those cases:

| Source numeric reference | Original RP2018 word occurrences | Exact observed Unicode word surfaces | STEPBible dictionary records |
|---|---:|---:|---|
| RP2018 editor Strong **3004** | **2,315** | **83** | **G3004G**, **G3004H** |
| RP2018 editor Strong **3754** | **1,287** | **2** | **G3754G**, **G3754H** |

G3004 is the primary research subject. G3754 is a contrasting
grammatical case to exercise the same methodological safeguards;
it is **not** an independent external lexicon or an approved translation.
All numeric counts are from the original OLT-037B source audit. This
checkpoint adds original verse-based contextual dossier construction.

For the publisher's TBESG source rows:

- G3004G: Greek headword **λέγω**, source English gloss **“to say”**.
- G3004H: **same written Greek headword λέγω**, gloss
  **“to say: call”**. Its source relationship is tagged **“a Meaning of”**.
- G3754G: Greek headword **ὅτι**, gloss **“that/since: that”**.
- G3754H: **same written Greek headword ὅτι**, gloss
  **“that/since: since”**, also tagged **“a Meaning of”**.

**These are STEPBible's literal dictionary-source glosses and source
classification metadata, not approved OLT translations or independent
historical Greek lexical conclusions.** That both candidate rows have
the same written headword within each case means that a simplistic
"two dictionary rows = two Greek homonyms" assumption is invalid.
It also does not certify that both meanings, or either meaning, fits
any particular original verse.

## Source provenance, reproducibility and license

**Greek text and original editor morphology:** Robinson–Pierpont 2018,
official ByzTxt v3.3.2, pinned upstream commit
`27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`.
All 27 source books are checked against the existing immutable
OLT-035D/OLT-036 imported original files. OLT-036's word join checks
source position + explicitly **lossy** normalized spelling. The
original exact accented Greek Unicode word and full verse text remain
unchanged, including punctuation. The 28 publisher alternate
Strong/morphology analyses remain attached to the original word;
they are NOT additional words.

**Lexicon reference evidence:** STEPBible/TBESG, source commit
`be4191f0082aeedddb0eff0c02c966292b2bd641`, pinned original
Git blob `efe271a1dbb73fa01f8fa6e0f164c6687757a9ae`
and exact file size **4,736,912 bytes**.
The original source is **CC BY 4.0**, with attribution:

> Greek lexicon data: STEP Bible (www.STEPBible.org), originally based on
> work at Tyndale House Cambridge; CC BY 4.0.

Source: https://github.com/STEPBible/STEPBible-Data
License: https://creativecommons.org/licenses/by/4.0/

The source file is fetched into an ephemeral GitHub Actions runner
at its exact immutable Git revision and its Git object hash is verified.
Neither moving upstream `master` nor unverified arbitrary TSV input
is accepted by the actual CI workflow.

**Prior audit dependency:** OLT-037B canonical JSON SHA-256
`a0291d66b506f7070263e8afc8c78ac160d2f9081720993b487e0cee3bc6db5b`
must match before any new dossier can be built; original candidate
dStrong rows and aggregate per-book and per-morph frequencies are
cross-checked exactly against that previous immutable checkpoint.
Nothing is quietly recounted to "fix" a source discrepancy.

## What the source dossier actually contains

`olt_core/greek_sense_dossier.py` scans all **140,149** original
Greek RP2018 word positions and extracts actual source occurrences for
numeric editor Strong 3004 and 3754. It verifies exact source word
ordinals, OLT-derived locators and character offsets against original
accented Greek verse strings, never reconstructing Greek original text
from an English translation or from lexicon headwords.

For each case, the dossier records **full-source frequency tables**
for every observed exact original Unicode surface, each original editor
morphology string and each NT book. It retains publisher eStrong,
dStrong, uStrong and editor relationship notes without conflating them.

An inspectable set of samples is chosen using an explicit fixed rule:

1. The **first and last** original occurrence in each book where the
   source case occurs.
2. The **first** original occurrence of every *raw RP2018 morphology
   annotation code* observed for the reference.
3. The **first** occurrence of every *exact Unicode original Greek
   surface spelling* observed for the reference.

The resulting union (duplicates merged by original OLT word locator)
includes full accented Greek original verse strings, the source Greek
word, its exact Unicode character span, up to three original Greek
word tokens on either side, original editor morphology, any alternative
original-source editor analyses, and **explicit sample-selection reasons**.
These samples document **where** original Greek can be examined, not
**what any word must mean**.

This is intentionally not an automatic word-sense-disambiguation
algorithm; samples are not classified as "say" versus "call", or
"that" versus "since". Source morphology is still the official
editor's analysis, **not independently reviewed grammar**.

## Human research and editorial gates

Before assigning a Greek sense to any original RP2018 word position,
a qualified reviewer must:

- Verify original Greek text and relevant variants independently.
- Establish Greek lemma identity with correctly cited independent
  lexicographical sources; do not treat dStrong suffixes as proof.
- Distinguish the dictionary publisher's "a Meaning of" notes from
  scholarly conclusions about homonymy, polysemy and usage.
- Examine the actual Greek syntax and wider passage context, rather
  than accepting an English lexicon gloss as an OLT verse translation.
- Independently check RP2018's morphology and alternative parse tags.
- Record contextual evidence, bibliography, reviewer, rationale,
  counterexamples and any unresolved disputes.
- Keep the owner English master lexicon and each separately versioned
  target-language output behind their independent approval gates.

All these gates remain **NOT DONE**. The committed generated dossier
explicitly sets `philological_reviewer_identity=null`,
`independent_lexicon_bibliography=[]`,
`contextual_sense_assignments=[]`,
`selected_stepbible_dstrong=null`,
`approved_greek_lemma=null`,
`approved_english_translation=null`,
`independent_philological_signoff=false`,
`owner_editorial_approval=false` and
`publication_status=BLOCKED`.

## How to inspect and verify

```sh
python scripts/fetch_olt_037_tbesg.py --output /tmp/OLT037-TBESG.txt
python -m olt_core.greek_sense_dossier --source /tmp/OLT037-TBESG.txt --summary
python -m olt_core.greek_sense_dossier --source /tmp/OLT037-TBESG.txt --case 3004
python -m olt_core.greek_sense_dossier --source /tmp/OLT037-TBESG.txt --case 3754
python -m olt_core.greek_sense_dossier --source /tmp/OLT037-TBESG.txt --verify-checkpoint
OLT037_TBESG_PATH=/tmp/OLT037-TBESG.txt python -m unittest discover -s tests -p 'test_olt_037c_greek_sense_dossier.py' -v
```

The committed JSON target is
`data/quality/olt_037c_greek_contextual_research_dossiers.json`.
Its exact contents must regenerate byte for byte in the dedicated
read-only `.github/workflows/olt-037c.yml`. All negative tests must
pass and required `foundation` regression remains mandatory.

This is an engineering-based **source-evidence dossier and review
protocol**, not a completed scholarly investigation or a Greek
lexicon approval. Future OLT-037D decisions, if any, must be created
as separate human-reviewed editorial records rather than modifying
this frozen unapproved source evidence.
