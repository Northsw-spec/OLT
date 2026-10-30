# OLT-037D — independent Perseus LSJ lexicon SOURCE evidence and scholarly review gate

Date: 31 October 2026. **Research only; no approved Greek lemma, Greek sense,
English Bible translation, or published Scripture.**

## Research question

OLT-037A and B indexed original 140,149 Greek word positions against
STEPBible TBESG numeric dictionary reference candidates, retaining 107
ambiguous numeric groups over 12,539 occurrences. OLT-037C independently
pinned original word contexts for two initial study groups: RP2018
editor Strong 3004 (2,315 word occurrences) and 3754 (1,287). But
both share native STEPBible subidentifiers and sense-division metadata.
Two STEPBible dStrong records are **not independent dictionary witnesses**.

OLT-037D therefore adds a **different** historical Greek lexical
resource to the research process: Liddell–Scott–Jones (LSJ),
*A Greek-English Lexicon*, via the Perseus Digital Library/PerseusDL
TEI-XML corpus. LSJ is classical Greek lexicography and must **not**
be treated as sufficient, by itself, to certify Koine/New Testament
grammatical meaning or a literal translated Bible.

It builds an *original-source entry-key inventory*, **not** an automatic
Unicode-to-lexicon equivalence table, verified lemma assignment,
semantic disambiguator, or theological interpretation.

## Independently verified source and reuse terms

Perseus Digital Library digital LSJ project:
https://github.com/PerseusDL/lexica

Pinned upstream Git commit:
`1c34cdf756c63cf37db61bd366d733431dbd7aa0`.

Exactly two original unmodified TEI/XML data shards are downloaded
into an ephemeral GitHub Actions folder:

| Greek research subject | Original upstream shard | Original size | Original Git blob SHA-1 |
|---|---|---:|---|
| G3004, Greek lambda section | `grc.lsj.perseus-eng12.xml` | 6,753,569 bytes | `0cc4c1906a4f8a0e696002dc83728d55b9cd9806` |
| G3754, Greek omicron section | `grc.lsj.perseus-eng16.xml` | 12,280,021 bytes | `b8a1ba605424c2df3b67f04190bde804664441c8` |

Full original paths are in
[`data/engine/olt_037d_perseus_lsj_source_manifest.json`](../data/engine/olt_037d_perseus_lsj_source_manifest.json).
Source data license: **Creative Commons Attribution–ShareAlike 4.0
(CC BY-SA 4.0)**, which is distinct from STEPBible's
**CC BY 4.0**. The original Perseus license file is
`license.md` (blob SHA-1
`033217724f8631eeb12987b30d76e8a62f275ceb`).
License: https://creativecommons.org/licenses/by-sa/4.0/.

Required source attribution: **Liddell, Scott and Jones,
*A Greek-English Lexicon* (1940); machine-readable digital text,
Perseus Digital Library, Tufts University, CC BY-SA 4.0**.
Source repository:
https://github.com/PerseusDL/lexica/tree/1c34cdf756c63cf37db61bd366d733431dbd7aa0/CTS_XML_TEI/perseus/pdllex/grc/lsj

No full-source XML shard or LSJ definition passage is copied into
the OLT repository. The committed output records only native TEI
**entry IDs and key identifiers**, source file identity, source
license and attribution. Do not claim that the original data's
CC BY-SA obligations become CC BY or public domain through this step.

## Original-source key discovery (actual executed GitHub CI)

Initial [OLT-037D GitHub Actions run
41143132363](https://github.com/Northsw-spec/OLT/actions/runs/41143132363)
downloaded both original pinned source files and validated each original
Git blob and byte length before indexing source TEI opening-tag
attributes. Only `<entryFree ...>` **opening attributes**
`id` and `key` are read; external DTD resolution is never used.
Definitions and `sense` trees are **not** parsed, summarized, copied,
or automatically classified.

Measured original-source observations:

| Research case | Source TEI `entryFree` rows indexed | Original exact literal search result |
|---|---:|---|
| G3004, query `le/gw` | **2,958** | Two original key records: `n62204 / le/gw1` and `n62205 / le/gw2` |
| G3754, query `o(/ti` | **4,512** | **No exact key record** matched the specified literal query |

These key strings are **hypotheses for independent philological
inspection**, not verified identity of biblical `λέγω` or `ὅτι`,
not proved relationships between dictionary entries, and **never**
contextual English meanings. The `1`/`2` LSJ key suffixes do
not imply a corresponding STEPBible `G/H` division.

A **missing exact XML key** for G3754 must not be reported as
"LSJ lacks the Greek word" or automatically filled from a nearby
entry, fuzzy search or modern web rendering. Indeed, the separately
available Scaife ATLAS LSJ online entry for `ὅτι`
(https://atlas.perseus.tufts.edu/dictionaries/entry/urn%3Acite2%3Ascaife-viewer%3Adictionaries.v1%3Alsj-n75694/)
provides a subsequent independent **manual lookup lead**, but this
does **not** establish that its live rendering and the two original
pinned XML shards use the same native key or entry schema. It is
not silently merged into OLT's machine-verified evidence.

Complete source-verified metadata:
[`data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json`](../data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json)
(original SHA-256
`ea9f6e031897630cd5645ace24797e91e145f2018e5dba236b8951d5f1aa4973`).
Exact regeneration against the upstream Git objects is required in CI.

## Explicit human-review decision boundary

The actual original Greek verse source and all 189 source-based
contextual samples remain frozen in OLT-037C (SHA-256
`08d58d6ce13b9803ed1936dfde1ed249f3c32e44af7bdc50b8665adb593bab69`).
The OLT-037D source-key inventory must not mutate these words,
morphological annotations, positional locators, or source variants.

The standalone `olt_core/greek_editorial_review.py` generates
**two blank research forms** with explicit requirements for later
qualified human review and owner translation editorial decisions.
Each identifies its earlier immutable original Greek source dossier
and independently licensed Perseus LSJ source evidence.

A valid blank form contains:

- no selected original word occurrence for semantic decision;
- no independently evaluated Greek morphology, lemma or sense;
- no asserted Greek lexicon page/section quotations or external
  Koine-specialist sources unless a future human reviewer supplies and
  checks them;
- no contextual English gloss, translation, scholarly reviewer
  signature, owner editorial approval or target-language release;
- `publication_status=BLOCKED`.

The [two frozen empty research templates](../data/research/olt_037d_independent_greek_review_templates.json)
are generated deterministically from the exact original OLT-037C
Greek-context dossier and the independent source-verified OLT-037D
Perseus key inventory. Every generated human-review, source-citation
and owner-decision field is empty or explicitly false.
`python -m olt_core.greek_editorial_review --verify` must reproduce
the committed file **exactly** from both hash-pinned source-evidence
artifacts before merge and on `main`.

The validator **rejects false PASS and counterfeit approvals**
even when someone hand-edits the source JSON. This is **not** a secure
human-identity or cryptographic-signature scheme; repository Actions
cannot determine the historical accuracy of a proposed dictionary
interpretation. Later actual scholarly research and separately
documented owner approval require a different reviewed checkpoint
and their own source/citation gates.

## Reproduction

```sh
python scripts/fetch_olt_037d_lsj.py --output-dir /tmp
python -m olt_core.greek_independent_lsj --source-dir /tmp --audit
python -m olt_core.greek_independent_lsj --source-dir /tmp --verify-checkpoint
python -m olt_core.greek_editorial_review --emit
python -m olt_core.greek_editorial_review --verify
OLT037D_LSJ_DIR=/tmp python -m unittest discover -s tests -p 'test_olt_037d_independent_lsj.py' -v
python -m unittest discover -s tests -p 'test_olt_037d_editorial_protocol.py' -v
```

Choose a new empty scratch folder instead of `/tmp` if the two
pinned filenames already exist. The source fetch intentionally refuses
to overwrite an existing XML file. The self-hosted workflow on
Ubuntu uses GitHub runner's separate temporary directory and
`permissions: contents: read`.

All tests and reports check only their stated evidence identity and
machine-readable constraints. They do not establish Greek
morphological, philological, historical or semantic correctness.
**Original-language-first translation remains blocked pending
actual scholarly and owner editorial review.**
