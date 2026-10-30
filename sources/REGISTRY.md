# Corpus and reference register

## Masoretic Hebrew (OT)
Candidate: **Open Scriptures Hebrew Bible**, OSIS XML based on public-domain Westminster Leningrad Codex, with CC BY 4.0 morphology/lemma annotations. URL: https://github.com/openscriptures/morphhb . Upstream commit inspected on 2026-10-29: **3d15126fb1ef74867fc1434be1942e837932691f**. Book file path: wlc/Gen.xml.

Required attribution: “Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb”. The WLC text is public-domain; annotation and morphology require CC BY 4.0 attribution. The exact source file **has not yet been imported or inspected in this new project**; no independently checked Genesis 1 morphology claim is made.

Reading comparison source: https://mechon-mamre.org/p/pt/pt0101.htm .

## NT Greek
Robinson–Pierpont Byzantine Textform: choose RP2018 as editorial source, following https://github.com/byztxt/byzantine-majority-text and https://byzantinetext.com/study/editions/robinson-pierpont/ . Exact file/checksum still UNPINNED, and no Greek book imported. Do not silently change to a newer edition.

## Secondary
Noah-rest wordplay (Gen 5:29; Gen 8:9; Deut 28:65).
Pitch/atonement lexical issue: https://classic.net.bible.org/verse.php?book=Gen&chapter=6&verse=14 .
Serpent/divination: separate נחש noun and verb requiring lexical analysis.
Noah/Christ typology: 1 Pet 3:20–21, subject to pinned RP original before direct quotations.

Before release: record exact source revision, hash, local retained copy, all word IDs, parsed morphology schema and uncertainties, source licenses, scholarly notes and reviewer identity.

## OLT-034 — source provenance for a shared multilingual motor (current status)

All target-language projects will consume original biblical source tokens with edition/revision metadata and appropriate license/attribution from the same OLT core. The OT OSHB/WLC original-language material has been imported into this project in later checkpoints than the initial registry note above; **source-tagged morphology does not equal independent scholarly verification**. OT Biblical Aramaic should be distinguished from Biblical Hebrew by its actual source language when imported and reviewed. The chosen NT RP2018 Greek original is still **not pinned or imported**, and must not be replaced with a fabricated or inferred Greek token ID. The existing first-section registry's initial "not yet imported" wording is historical and superseded by this note for the present OT status.

The English master lexicon is a research reference not an alternate canonical source. Every external target-language repo must pin a version/commit and immutable source snapshot and preserve attribution and any required reuse conditions. See docs/OLT-034_MULTILINGUAL_ARCHITECTURE.md.

## OLT-035 — current exact source registry (supersedes stale import/unpinned statements above)

**Source contract:** `data/engine/olt_035_source_provenance.json`; `olt_core/sources.py`; [implementation report](../docs/OLT-035_SOURCE_PROVENANCE.md).

- OT: 39 existing OSHB/WLC imported JSON books from pinned Open Scriptures `morphhb` `3d15126fb1ef74867fc1434be1942e837932691f`. Per-book imported Git blob SHA-1 is now frozen. The corresponding 39 upstream XML SHA-256 values are retained from prior manifest; this checkpoint did **not** recompute SHA-256 against newly downloaded original XML. Imported total 23,213 verses, 306,785 word tokens, 301,837 H (Hebrew) and 4,948 A (Biblical Aramaic) original source tags. WLC text public domain; OSHB lemma/morphology CC BY 4.0 with required attribution.
- NT: Robinson–Pierpont Byzantine Textform **RP2018** from official [ByzTxt GitHub](https://github.com/byztxt/byzantine-majority-text), release `v3.3.2`, immutable commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`. Public-domain LICENSE. Original editor files are `source/Strongs` and `source/CCAT`; derived Unicode CSV is provided for convenience. One genuine full Greek book, **3 John**, has been copied byte-identically from `csv-unicode/ccat/no-variants/3JO.csv`, Git blob `296e85242768aab57007a69cf62b92aef0b5067b`. That is **14 verse strings**, not a completed 27-book NT or imported Greek word/morphology ledger.
- No source bytes or tagged morphology have been independently certified as philologically accurate. No additional owner English or other-language lexical decisions or publication approvals are inferred. Future language repositories must retain the exact original source pins and licensing attribution.

## OLT-035B — active RP2018 full verse-file source registry, not word lexicon

**Later checkpoint superseding the old Greek NT unpinned / 3 John-only status statements above:** all **27 canonical RP2018 Greek NT continuous book CSV source files** were imported verbatim from ByzTxt release `v3.3.2` (commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`). Each source's upstream Git blob SHA-1 and exact byte length are frozen in `data/engine/olt_035b_rp2018_verse_inventory.json`. The separate original **PA.csv** (John 7:53–8:11) and **ACT24.csv** (Acts 24:6–8) source files are preserved under `data/imported/nt/rp2018/ancillary/`, without unreviewed automatic placement in continuous main text. The upstream license is public domain; original source-of-truth files are `source/Strongs` and `source/CCAT`, while the imported Unicode verse CSVs are a generated convenience format. Complete Greek **verse text bytes** do NOT provide stable original Greek word IDs, lemma or morphology; these source capabilities and all independent textual/linguistic verification and publication remain blocked. See `docs/OLT-035B_COMPLETE_RP2018_GREEK_VERSES.md`.

## OLT-035D — original editor Greek word/morphology snapshot active

**Latest Greek word-level SOURCE checkpoint:** All **27 official ByzTxt RP2018 source/Strongs/*.BP5** files at v3.3.2 / commit 27a45ff1b7be6c17ccbfeac414f3f55732ae8e were imported with **byte-identical Git blob SHA-1** hashes (total 2,745,008 bytes). These original unaccented Beta Code files provide **140,149 editor word-form / Strong / morphology records** plus **28 additional parsing pairs** on some existing original words. They contain 7,957 original verse reference positions including **four empty placeholders**: Luke 17:36; Acts 8:37, 15:34, 24:7. They do NOT contain Greek source text in these four empty slots. All 7,953 nonempty BP5 references have corresponding Unicode source verses, but individual word-level accented Greek alignment is still UNVERIFIED. Strong references and morphology are editorial source annotations, not independent scholarly reviews, and no native source word IDs were provided; source-position locators are generated by OLT and labeled accordingly. Manifest: data/engine/olt_035d_greek_word_source_manifest.json; reader: olt_core/greek_words.py. Official editor source format: https://github.com/byztxt/byzantine-majority-text/blob/v3.3.2/source/README.md. Upstream public domain; Bible publication BLOCKED.
