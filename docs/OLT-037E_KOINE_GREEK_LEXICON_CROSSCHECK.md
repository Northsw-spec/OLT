# OLT-037E — Abbott-Smith New Testament Greek lexicon and LSJ source-key investigation

**Status:** Source-bound research, **NOT** Greek lemma/sense approval, not a
translation and not a released Bible. Date: 2026-10-31.

## Purpose and why an additional source is necessary

OLT-037C preserved all source Greek original RP2018 word occurrences for
the research labels G3004 (2,315 occurrences) and G3754 (1,287), plus
189 provenance-preserving original Greek verse-context samples.
OLT-037D imported a **separate** original Perseus LSJ dictionary-key
research inventory. LSJ is classical Greek; its key IDs alone cannot
establish Koine usage or individual NT word-sense assignments.

**OLT-037E adds an original lexicon specifically about NT Greek**:
George Abbott-Smith, *A Manual Greek Lexicon of the New Testament* (1922).
The digitized TEI is provided by the
[translatable-exegetical-tools Abbott-Smith project](https://github.com/translatable-exegetical-tools/Abbott-Smith)
and that project's original README explicitly states that
`abbott-smith.tei.xml` **including its markup is public domain**.

The original printed lexicon specifically says its textual background
follows the text associated with Moulton and Geden/Westcott-Hort, **not
the current OLT RP2018 textual edition**. Consequently a matching native
Strong number in this dictionary is **source-referenced lexical research
only**, not the publisher's original RP2018 word-position ID or proof of
a precise Greek morphological or lexical identity.

Importantly, Abbott-Smith's own introduction credits earlier LSJ,
Thayer and related lexicographical scholarship. Therefore apparent
agreement between Abbott-Smith and LSJ is **not** statistical evidence
from two fully independent authorities. No automatic multiple-source
confidence score, vote, semantic promotion, or approval is implemented.

## Provenance and licensing

**Abbott-Smith original native source** from
`translatable-exegetical-tools/Abbott-Smith`:

| Property | Source locked in repository |
|---|---|
| Repository commit | `8c00cb244761aa23659421a8cbbbf7a3b27b7d59` |
| Full original filename | `abbott-smith.tei.xml` |
| Original Git blob SHA-1 | `e10dcfa534dbc71168ca6ac273e991348bab2bb2` |
| Exact XML byte length | **5,698,817** |
| Original project README blob SHA-1 | `64eda828221708e54d3b23d2d8a1c17b1e76a1ef` |
| Original project README length | **4,416 bytes** |
| Source license statement | **Public domain**, including digitized markup; verified against the pinned README itself |

Full source manifest:
[`data/engine/olt_037e_abbott_smith_source_manifest.json`](../data/engine/olt_037e_abbott_smith_source_manifest.json).

Original LSJ source is separately pinned at Perseus upstream commit
`1c34cdf756c63cf37db61bd366d733431dbd7aa0`,
with exactly validated 6,753,569-byte and 12,280,021-byte XML files.
**Perseus LSJ is CC BY-SA 4.0** with attribution to Liddell,
Scott and Jones and the Perseus Digital Library at Tufts University.
STEPBible's TBESG remains **CC BY 4.0** with source attribution.
The newer Koine dictionary's public-domain status **does not**
change the conditions on the distinct STEPBible and Perseus sources.

Source XML data is fetched only into temporary GitHub Actions storage
and never committed. The OLT research outputs contain original
Abbott-Smith lexical source **metadata and selected short, explicitly
SOURCE-ONLY definition text**, which is not transferred into an
approved English master lexicon or published Bible verse.

## How results are derived, and what they do NOT mean

After validating the independent exact Git objects, the script
`olt_core/greek_koine_crosscheck.py` inspects the original
TEI/XML `entry` elements and preserves their source `n` attributes.
Only original G3004 and G3754 numerical labels are extracted,
preserving any multiple dictionary entries and their exact original
first written `orth` forms, all native Strong-number references and
up to 12 original short `def`/`gloss` source records as evidence.
All such definitions are marked **NOT OLT translations** and no
meaning, sense or grammatical label is selected. A source editor's
word form is not assumed to match RP2018's accentuation or parsing
without independent linguistic review.

The source-critical LSJ diagnostic scans the **same immutable Perseus
XML shards as OLT-037D**, with full byte-hash verification. It retains
the strictly matched records for G3004 (`le/gw1`, `le/gw2`) and
the exact G3754 test for `o(/ti` (previously no match). Separately,
it computes two **strictly diagnostic, lossy ASCII signatures** on raw
source dictionary `key` strings (for example, stripping original
accent notation and numeric suffixes). The output always records the
original native source entry key/ID and marks the lossy diagnostic
**NOT VALID FOR A CROSSWALK**.

This can expose possible alternative source-key notation, **but must
never auto-fill a missing exact entry**, invent a Greek headword,
decide whether entries are homonyms/polysemes, or assign "since",
"that", "say" or "call" to a verse.

Original downstream Greek text, word positions, editor alternative
morphologies, the 107 numeric research groups, and the OLT-037C
original Greek evidence remain immutable. All current linguistic
claims and owner-edited translations remain **unapproved**.

## Measured original-source results and recovered LSJ key notation

The first dedicated GitHub Actions source run
([OLT-037E #41144904136](https://github.com/Northsw-spec/OLT/actions/runs/41144904136))
verified the original public-domain statement in Abbott-Smith's exact
upstream README and the byte-identical original TEI corpus, as well
as both unchanged Perseus LSJ XML Git objects. Subsequent source run
([OLT-037E #41144904136](https://github.com/Northsw-spec/OLT/actions/runs/41144904136))
confirmed 7/7 tests for the original source and spelling-key research
method. The complete pinned corpus contains **6,153** native
`entry` XML elements, of which **5,896** have original `n`
source entry metadata. This is original dictionary entry metadata,
**not** the 140,149 source Greek Bible word positions.

| Source investigation | RP2018 G3004 | RP2018 G3754 |
|---|---|---|
| Original Abbott-Smith TEI entry `n` | `λέγω\|G2036\|G2046\|G3004\|G4483` | `ὅτι\|G3754` |
| Original indexed Abbott-Smith entries bearing the numeric label | **1** | **1** |
| Original Abbott-Smith `def` or `gloss` source records | **11** | **3** |
| Original LSJ exact-source key query | `le/gw` | `o(/ti` |
| Exact LSJ source-key matches (OLT-037D unchanged) | `le/gw1`, `le/gw2` | **None** |
| Strictly lossy, DIAGNOSTIC-ONLY matching source-key notation | `le/gw1`, `le/gw2` | `n75695 / o(/ti^` |

**Specific resolution of the earlier G3754 discovery problem:** in the
original pinned LSJ omicron XML shard, the actual original native entry
key is **`o(/ti^`**, not the originally hypothesized exact
`o(/ti`. The extra original source notation character `^`
explains why a literal exact-key lookup yielded zero results.
The original native LSJ entry ID **`n75695`** is preserved.
Its discovery through a **lossy diagnostic spelling signature**
is **NOT** independent certification that LSJ's entry and a specific
RP2018 biblical occurrence have the same correct sense, and it
does not retroactively modify the frozen OLT-037D exact-key results.

**Another source-join risk identified:** Abbott-Smith's original
`λέγω` entry's native `n` field carries **four different Strong
numbers** (`2036`, `2046`, `3004`, `4483`). Therefore this
dictionary entry **cannot** be used as evidence of a unique,
one-to-one Strong-number-to-headword or contextual-sense relationship.

The pinned generated
[original source crosscheck](../data/quality/olt_037e_abbott_koine_and_lsj_key_diagnostics.json)
is **9,916 UTF-8 bytes**, SHA-256
`f6e0c31f4a7c736df307e55c10d0860ea47edf7aa6dc2c28b61d6b81430ee435`.
The committed source parser stores original Greek source headwords,
all original source entry Strong labels and up to 12 source `def`/`gloss`
records with their original TEI tag names. These source definitions
are **not** promoted to OLT English or verse-by-verse meanings.

## Acceptance test requirements

- Confirm that the original Abbott-Smith **README** both has the
  expected Git blob checksum and **actually contains** its public-domain
  statement. A manifest string alone is insufficient.
- Verify original full XML Git blob SHA-1 and exact file length,
  reject mutation/truncation or unrelated XML before parsing.
- Strictly reject XML external DTD declarations or entity definitions.
  No network XML entity resolution is allowed.
- Count all original lexical `entry` tags; fail on dramatically
  incomplete source files. Save original `n` attributes, source
  `orth` forms and short `def` evidence without automatic selection.
- Compare the exact prior OLT-037D source-key results and OLT-037C
  Greek word-occurrence counts against their pinned SHA-256 records.
- Run negative tests: fake source, fake public-domain statement,
  invented semantic approvals, lossy query promotion, snapshot tampering.
- Require byte-for-byte regeneration of the final frozen
  [OLT-037E source research artifact](../data/quality/olt_037e_abbott_koine_and_lsj_key_diagnostics.json)
  on the exact PR commit and after merge into `main`.
- Maintain separate author/reviewer and owner editorial decision gates,
  untouched by any CI PASS. The Biblical publication gate is **BLOCKED**.

## Reproduction

```sh
mkdir -p /tmp/olt037e-original
python scripts/fetch_olt_037e_abbott.py --output /tmp/olt037e-original/olt037e-abbott-smith.tei.xml
python scripts/fetch_olt_037d_lsj.py --output-dir /tmp/olt037e-original
python -m olt_core.greek_koine_crosscheck \
  --abbott /tmp/olt037e-original/olt037e-abbott-smith.tei.xml \
  --lsj-dir /tmp/olt037e-original --audit
python -m olt_core.greek_koine_crosscheck \
  --abbott /tmp/olt037e-original/olt037e-abbott-smith.tei.xml \
  --lsj-dir /tmp/olt037e-original --verify-checkpoint
```

**This is research-source coverage and index-diagnostic verification
only.** The original published Greek and English biblical
translation remains BLOCKED until the independent philological
review and separate owner approval are actually documented.
