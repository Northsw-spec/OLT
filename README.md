# Olund's Linked Translation

**Binding active scope (2026-10-31): English only.** OLT is being built to translate original Biblical Hebrew/Aramaic/Greek into a complete **66-book English Bible**, subject to the owner's explicit verification and approval of the complete English translation. Japanese, Amharic and **all** other non-English translation work is postponed until that approval. Legacy multilingual schemas are future-only and do not authorize non-English translation work. **Practical next priority: a working, source-aligned English verse-translation prototype.** See [binding English-first policy](docs/OLT_ENGLISH_FIRST_OWNER_GATE.md) and [machine-readable owner gate](data/policy/olt_english_first_owner_verification.json). Current English completeness: NOT DONE; owner approval: NOT DONE; publication: BLOCKED.

**CHES-001 (2026-10-31, merged and CI-verified):** We now have a **private-only** source importer for the CHES v2.0 Hebrew–English sublinear from a separately licensed third-party PDF source. The official OT source index contains **929 unique PDF chapter links** across 39 source filename groups. The actual original Genesis 1 PDF was verified and extracted into **31 source verse labels and 526 green CHES spans** without OCR or KJV contamination; **no complete CHES text is committed to this public repository**. A slow, resumable local 929-chapter-capable ingestion command is available, but **all 929 chapters have NOT been processed** and CHES source spans are **not independently aligned** to OLT's original Hebrew/Aramaic tokens. Machine-readable source use was separately authorized as reported by the owner; wider redistribution and non-English derivative permissions are not assumed. See [CHES import and private commands](docs/OLT_CHES_PRIVATE_INGEST.md), [source-only manifest](data/engine/olt_ches_source_manifest.json), [PR #41](https://github.com/Northsw-spec/OLT/pull/41) and [canonical status](docs/STATUS_CURRENT.md). **Next priority: real English OLT draft output with explicit original source alignment and owner grammatical rules**, not more detached lexicon-only research. English remains the only active target; Scripture publication BLOCKED.

This is the entirely new **canonical project** at https://github.com/Northsw-spec/OLT.

Status: **SOURCE IMPORTED / IDENTIFIERS VERIFIED / NO BIBLE CHAPTER RELEASED**.

The present repository is written anew; no previous draft or script is copied into it. Read docs/MASTERPROMPT.md for the authoritative instructions, docs/RESEARCH.md for research waves, docs/LEXICON.md for word/tense control, docs/LINKS.md for homonyms and Christological links, docs/PUBLISHING.md for documents, lexicon/hebrew.json and links/registry.json for seed data, sources/REGISTRY.md for provenanced source plans, scripts/check.py and tests/test_checks.py for CI, and genesis/STATUS.md for what remains blocked.

The completed foundation is **not** the entire Hebrew Bible lexicon, nor a verified Genesis 1 translation. Such claims require independently parsed source tokens and separate human reviews. Prior GitHub history is not imported; another old repo was inaccessible, so this statement is not a claim of purging its remote history.

## OLT-035D — Original Greek editor word forms + morphology are now source-pinned
**OLT-035D VERIFIED ON MERGED MAIN (2026-10-30):** [PR #24](https://github.com/Northsw-spec/OLT/pull/24) merged at `82792e7af11adbd0830b040d0f9c066e666db564`. Required GitHub-hosted Ubuntu `foundation` **308/308 PASS**; original Greek editor word-source tests **18/18 PASS**, source corpus: **140,149 original word-form records and 28 alternative parsings**, 7,957 BP5 reference slots including four empty slots. **No final Greek lemma meanings, accented-word crosswalk or independent translation approval.**



The shared OLT core has imported **all 27 original RP2018 editorial Strong/Beta Code morphology source files**, exact Git blob matches. They contain **140,149 original word-form/Strong/morphology triples**, with **28 additional parsing possibilities** on existing Greek words (not additional original words). The official sources have **7,957 verse positions**, including **4 EMPTY placeholders**, leaving **7,953 Greek word-containing verse slots**, corresponding by reference to the Unicode Greek main texts.

- [Exact original Greek source and parser report](docs/OLT-035D_RP2018_OFFICIAL_GREEK_WORDS.md)
- [Pinned 27-book Greek editor morphology manifest](data/engine/olt_035d_greek_word_source_manifest.json)
- [Read-only source-index and ambiguity parser](olt_core/greek_words.py)

```sh
python -m olt_core.greek_words --audit
python -m olt_core.greek_words --verse MAT Matt.1.1
python -m olt_core.greek_words --verse MAT Matt.26.45
```

The editor's Strong numbers and morphology are **source annotations**, not independent approval of Greek lemma forms or meaning. Per-word accented Unicode alignment, independent philology, English reference decisions and all target-language translations remain NOT DONE. Bible publication BLOCKED.

## OLT-035B — All 27 RP2018 Greek NT books now imported as source verse text
**OLT-035B VERIFIED (2026-10-30):** [PR #22](https://github.com/Northsw-spec/OLT/pull/22) merged to `274279701a52aae5c82727cd71420f65531a5789`. Official RP2018 Greek verse source: **27 book files / 7,953 Greek verse rows**, plus **2** separately preserved Greek passages. Post-merge GitHub Actions: required foundation **290/290 PASS**, Greek source QA **15/15 PASS**, OT source QA **16/16 PASS**, multilingual core **25/25 PASS**. **No Greek word/lemma/morphology ledger, finished translation, or Bible release is claimed.**


The OLT core now contains the **27 original RP2018 Greek continuous-text NT book CSVs**, copied byte-identically from official ByzTxt `v3.3.2` (commit `27a45ff...`). In addition, the separate original Greek **PA.csv** (John 7:53–8:11) and **ACT24.csv** (Acts 24:6–8) files are preserved under a separate ancillary directory without altering continuous-text verses automatically.

- [OLT-035B source inventory and critical restrictions](docs/OLT-035B_COMPLETE_RP2018_GREEK_VERSES.md)
- [27-book Greek source hash/edition contract](data/engine/olt_035b_rp2018_verse_inventory.json)
- [Byte-verifying Greek verse reader and complete corpus audit](olt_core/nt_corpus.py)

```sh
python -m olt_core.nt_corpus --audit
python -m olt_core.nt_corpus --verse MAT Matt.1.1
python -m olt_core.nt_corpus --verse 3JO 3John.1.1
python -m olt_core.nt_corpus --ancillary PA
```

The complete original Greek **verse text collection** is NOT a complete Greek word-level lexicon or morphological analysis. Exact authenticated Greek word IDs, lemma alignment, optional textual variants review, English master translation and target-language translations remain separate uncompleted gates. **Publication BLOCKED.**

## OLT-035 — Source provenance and Greek source import stage (October 30, 2026)

The shared OLT core now has source-verifying adapters for all **39 imported OT books**, retaining exact original OSHB word IDs, historical upstream XML checksums, 39 frozen imported file Git hashes, and 301,837 Hebrew vs 4,948 Aramaic source-tagged token identities. The **Robinson–Pierpont 2018** Greek source revision is pinned to upstream ByzTxt **v3.3.2** / `27a45ff...`. Its authentic **Third John** text is imported verbatim with a matching upstream blob digest (**14 Greek verses, no Greek word IDs or lemma/morphology import yet**).

- [OLT-035 source provenance, boundaries and commands](docs/OLT-035_SOURCE_PROVENANCE.md)
- [Machine-readable 39-OT-books + RP2018 pin registry](data/engine/olt_035_source_provenance.json)
- [Read-only original language source adapters](olt_core/sources.py)
- [Original RP2018 Greek 3 John source CSV](data/imported/nt/rp2018/3JO.csv)

Research-only commands, Python standard library:

```sh
python -m olt_core.sources --audit-ot
python -m olt_core.sources --ot-verse Gen Gen.1.1
python -m olt_core.sources --ot-verse Dan Dan.2.5
python -m olt_core.sources --greek-3john
```

No independent morphological signoff, full NT import, translation or publishing is claimed. **Publication remains BLOCKED**.

## New architectural direction — OLT-033/034 (30 October 2026)
**OLT-034 VERIFIED GITHUB CHECKPOINT (2026-10-30):** [PR #19](https://github.com/Northsw-spec/OLT/pull/19) merged at 8179853cbfd241c0d836af576793563ecbef3145; required foundation **259/259 PASS**, multilingual engine checks **25/25 PASS**, name rules **13/13 PASS**, doctrinal checks **6/6 PASS** on post-merge main. **No target-language Bible has been translated or approved.** See docs/STATUS_CURRENT.md for the current canonical status.


**OLT is the shared original-language-first foundation for future Bible translations into multiple languages.** Keep original Hebrew/Biblical Aramaic/Greek corpus evidence, morphology, lemma/verse/token IDs and research together in this canonical repository. English is a **source-linked master reference**, not an intermediary that Japanese, Amharic, Icelandic, Chinese or other target languages must translate from. Each future target language will get its **own GitHub repository** and independently reviewed locale grammar/lexicon, notes and release. No locale repos have been created as part of OLT-034.

- [OLT-034 multilingual architecture, planned rollout and explicit blockers](docs/OLT-034_MULTILINGUAL_ARCHITECTURE.md)
- [Machine-readable binding core/locale design](data/engine/olt_034_architecture.json)
- [English master **reference**, not a complete published lexicon](lexicon/english_master_manifest.json)
- [Versioned reusable source-first Python core](olt_core/engine.py) and [read-only CLI](olt_core/cli.py); 6 empty language profiles in locales/
- [OLT-033 Bible-wide proper-name and meaning-underword decisions](docs/OLT-033_BIBLEWIDE_NAMES_UNDERWORDS.md), including owner-corrected God (Elohim) / Mighty Governance and Noah / Rest

Use Python 3.12 standard library, with no installation required for this research example:

    python -m olt_core.cli --locale ja --pretty
    python -m olt_core.cli --locale am --pretty
    python -m unittest discover -s tests -p 'test_olt_034_multilingual_core.py' -v

These commands generate **source-token research JSON**, not Japanese or Amharic Scripture translations. The NT Greek edition RP2018 is still unpinned and unimported. All English word-family approvals, independent philological signoff, complete OT/NT lexicon and multi-locale Bible publication remain BLOCKED.

**Historical notice:** The older CI runner warnings further below describe an already resolved historical incident. Consult [the canonical current status](docs/STATUS_CURRENT.md) and actual GitHub Actions runs instead of interpreting those historical warnings as an active outage.

## Current progress

[Latest verified checkpoint and release blockers](docs/STATUS_CURRENT.md) — all OT source words imported; 9,252/9,519 exact dictionary-ID chains verified; Genesis 1 has all 434 original word tokens and 97 source-linked lemmas in its first review dossier. The entire imported BDB lexicon is now preserved with nested sense hierarchy; all 97 Genesis 1 lexical study cards have attached BDB source evidence. OLT-008 now contains the first seven-token Genesis 1:1 literal research proposal and a ranked 97-lemma study queue. **No final OLT English lexicon or Genesis chapter is yet approved.**

**Latest source-first research:** [OLT-009 Genesis 1:2–5 – 45 original word-token alignments](data/research/genesis_01_verses_02_to_05_research.json). Together with Genesis 1:1, the new non-published study contains 52 source-token English proposals; the rest of the chapter remains blocked.

**OLT-010 verified source-research checkpoint:** [Genesis 1:6–10](data/research/genesis_01_verses_06_to_10_research.json) — 63 original source tokens, 11 OSHB-wayyiqtol forms, 31 source lemma IDs. Together with OLT-008/009, Genesis 1:1–10 has **115/434 token-linked English research proposals**, none independently certified for release. Next: [OLT-011](https://github.com/Northsw-spec/OLT/issues/5).

## Source-first research milestone OLT-015/016
All **31 Genesis 1 verses / 434 original word tokens** now have **unapproved Hebrew-English research alignments**, machine-checked against the pinned OSHB source. The 50 original source-tagged wayyiqtol verbs, 97 source lemma IDs and seven grammar-only words are accounted for.

- [Genesis 1 research preview (NOT approved Scripture)](genesis/GENESIS_01_SOURCE_RESEARCH_PREVIEW.md)
- [434-token complete source ledger](data/research/genesis_01_complete_research_alignment.json)
- [97-lemma editorial review queue: 94 English word families pending approval](data/research/genesis_01_lexeme_editorial_queue.json)
- [Current status and release blockers](docs/STATUS_CURRENT.md)

**Caution:** Machine source coverage is not a complete, philologically approved OLT translation. No final bilingual ODT/PDF or homonym links are released.

**OLT-017A:** [Five contested-lexeme scholarly research questions](docs/OLT-017A_SCHOLARLY_REVIEW.md), including competing published perspectives and disclosed abstract-only evidence. The **94 unapproved Genesis 1 English word families** remain pending.

## OLT-019 and OLT-017B — Latest source research (October 30, 2026)

- [OLT-019](docs/OLT-019_FOOTNOTE_ANCHORING.md): Genesis 1:1's `[of His Power]` carries a Markdown note marker **immediately after the bracketed expression**. Its note still distinguishes the *separate* `rēʾšît` and `ʾôn` lexemes in Gen 49:3 / Deut 21:17. The main English sentence and original seven source word IDs were not changed.
- [OLT-017B](docs/OLT-017B_GENESIS_1_2_LEXICAL_RESEARCH.md): four separate source-anchored research dossiers for `tohu`, `bohu`, `tehom` and `merachephet` in Gen 1:2, with alternative English readings and explicitly disputed/limited scholarly evidence. No new lexical meaning or under-word homonym link is approved.
- **CI ALERT:** [OLT-CI-001](https://github.com/Northsw-spec/OLT/issues/7): new GitHub-hosted Actions runs have failed **before any steps executed** (`runner_id=0`, `steps=[]`). These new checkpoints have **NOT PASSED CI**. Prior OLT-018 green runs do not cover newly added tests. See [latest OLT-015 run](https://github.com/Northsw-spec/OLT/actions/runs/41091217157) and [OLT-017B run](https://github.com/Northsw-spec/OLT/actions/runs/41092053582).

All publication gates remain **BLOCKED**. Do not claim independent scholarly approval, final English lexical choice, final footnotes at page bottom, or bilingual ODT/PDF merely from a source research document.

## OLT-021 — Binding binitarian clarification

The owner has clarified that **God is one; the Father and Son are one; one faith; one Lord Jesus Christ; the Lord Jesus is the Spirit**. The **Son is eternal and uncreated**, existed with the Father before the world's foundation, and joined the Father in creation prior to incarnation. **The eternal Son became human through Mary**; this was not the start of his existence. The owner emphatically **rejects “Jesus was the first being God created”** as a misreading of the Firstborn Son / Revelation 3:14 interpretation.

This confession governs OLT's interpretive notes while preserving original-language source evidence and uncertain grammar. See [Masterprompt](docs/MASTERPROMPT.md), [the precise owner correction](docs/OLT-021_BINITARIAN_CREED_CLARIFICATION.md), [doctrinal framework](docs/DOCTRINAL_FRAMEWORK.md), and [machine-readable policy](data/policy/olt_theological_framework.json). No new biblical publication approval is implied.

**OLT-022 – Owner's Genesis 1:1 under-word exception:** In the [Genesis 1 linked reading](genesis/GENESIS_01_SOURCE_RESEARCH_PREVIEW.md), lowercase **with** sits immediately beneath initial **In**. The second reading is clearly marked **binitarian interpretive**, not a certified instrumental Hebrew gloss. See the [precise source policy](data/policy/olt_underword_overrides.json) and [research reasoning](docs/OLT-022_GENESIS_1_1_IN_WITH_UNDERWORD.md). Other occurrences of *in* remain context-dependent and do not automatically get *with*.
