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
