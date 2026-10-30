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
