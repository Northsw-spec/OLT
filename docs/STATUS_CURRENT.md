# OLT — CURRENT STATUS (2026-10-30)

**Canonical repository:** https://github.com/Northsw-spec/OLT  
**Latest fully merged and CI-verified engineering checkpoint:** **OLT-035B**, [PR #22](https://github.com/Northsw-spec/OLT/pull/22), main commit **274279701a52aae5c82727cd71420f65531a5789**. Post-merge GitHub-hosted Actions verified **foundation 290/290 PASS** (Genesis release still BLOCKED), **OLT-035B 15/15 PASS** (27 RP2018 Greek source books, 7,953 Greek verse rows and two ancillary texts), **OLT-035 16/16 PASS** (39 OT imported books, 301,837 Hebrew and 4,948 Aramaic tokens), and **OLT-034 20/20 + 5/5 PASS** (source-first multilingual core).  
**Translation publication:** BLOCKED. **Independent lexical/morphological signoff:** NOT DONE.

> **Status priority:** This opening section supersedes outdated present-tense claims in the historical chronological log below. Earlier reports of CI jobs failing before test startup describe an **old incident**, not the current CI state. Preserve the older reports as historical evidence, not as a live failure.

## OLT-035D — Original editor Greek word/morphology sources (WIP, CI under review)

- **All 27 official ByzTxt RP2018 source/Strongs/*.BP5 files** are copied byte-identically to OLT on branch `olt-035d-official-rp2018-greek-morphology`; upstream v3.3.2, commit 27a45ff1b7be6c17ccbfeac414f3f55732ae8e28, public domain.
- The editor's actual annotated original Greek data contains **140,149 primary Beta Code word forms** with a Strong reference and morphology tag and **28 alternative parsing pairs** on existing words. **Source verse slots: 7,957, including four EMPTY positions** (Luke 17:36; Acts 8:37, 15:34, 24:7), leaving **7,953 nonempty** word-containing verse slots that align at the **verse-reference level only** with the Unicode Greek source corpus. The empty positions contain NO original Greek words.
- Source-traceable word-position IDs are **OLT-derived**, not original native publisher word IDs. Greek lexical lemma FORMS, actual accented Unicode word-level alignment, independent morphological reviews, English master lexicon and other-language translations remain NOT DONE.
- New source registry `data/engine/olt_035d_greek_word_source_manifest.json`, parser `olt_core/greek_words.py`, detailed [research notes](OLT-035D_RP2018_OFFICIAL_GREEK_WORDS.md), dedicated GitHub Actions and negative tests are being reviewed. All original OLT owner translation/publishing restrictions remain intact.

## OLT-035B — Whole Greek NT source book-file import (MERGED AND POST-MERGE CI VERIFIED)

- The source repository contains **all 27 continuous-text RP2018 Greek NT book UTF-8 CSV files**, exact Git blob matches to ByzTxt `v3.3.2` at pinned upstream commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`. Total main source text files ~1.74 MB, all authentic Greek verse text, not fabricated from English or an alternate Greek edition.
- **PA** (John 7:53–8:11) and **ACT24** (Acts 24:6–8) are separately retained exact-source ancillary readings. Do NOT silently merge their contents into continuous-text verses; textual apparatus and owner editorial decisions must be reviewed.
- `data/engine/olt_035b_rp2018_verse_inventory.json` pins upstream paths, hashes and lengths for all 29 source CSVs (27 main + 2 ancillary). `olt_core/nt_corpus.py` parses/validates Greek source verse references and creates no Greek word tokens, lemma IDs, morphology or translated Scripture. [Source and release detail](OLT-035B_COMPLETE_RP2018_GREEK_VERSES.md).
- **Full NT Greek VERSE TEXT files are imported, but original Greek WORD-LEVEL identities, morphology, lexical sense review, English master translation, locale translations and publication are NOT DONE.**
- OLT-035B **post-merge main verification:** GitHub Actions run 41127319395 verified 27 original Greek source books, 7,953 parsed Greek verse rows and two ancillary files (15/15 tests PASS); required foundation run 41127319379 checked 290/290 tests and confirmed the release gate still BLOCKED. The OLT-035 first 3 John-only scope below is an earlier historical checkpoint and is now superseded for verse-file import coverage.

## OLT-035 — OT provenance and first Greek source stage (MERGED AND POST-MERGE CI VERIFIED)

- All **39 existing imported OT book JSON snapshots** are now pinned by Git blob SHA-1, plus the 39 original upstream XML SHA-256 values **recorded in the earlier importer manifest**. The original XML is **not redownloaded or rehashed in this checkpoint**. Imported audit totals: 23,213 verses / 306,785 source words, including **301,837 H-tagged Hebrew** and **4,948 A-tagged Aramaic** words. Source morphology is NOT independently reviewed.
- **RP2018 Greek original source revision is now pinned to ByzTxt v3.3.2**, commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`. An identical Git blob `296e85242768aab57007a69cf62b92aef0b5067b` of **3 John, 14 Greek verse strings** has been added from its Unicode CSV source. This means one source book is imported at **verse level**, NOT that 27 NT books have imported Greek word IDs, lemmas, morphology or full source alignment.
- New `olt_core/sources.py`, 16 focused unit tests, read-only `olt-035.yml` and [full source provenance report](OLT-035_SOURCE_PROVENANCE.md) await checks in this development snapshot. NO translation approvals and NO Bible publication.
- This section **supersedes the older OLT-034 snapshot wording** stating that the Greek text *release itself* was unpinned. Source pinning is now done only for the selected RP2018 revision and first sample; **complete Greek NT word-level sourcing remains NOT DONE**.

## Owner decisions — OLT-033 and multilingual OLT-034

- **OLT-033 (MERGED, independently CI-executed):** every applicable named entity and distinctive source-language meaningful title across **both Testaments** requires a source-aware research decision and a vertical English underword only when justified. The ten example candidates include **God/Elohim — Mighty Governance** (owner interpretive association, NOT a proven literal Hebrew word gloss) and **Noah — Rest** (associated with Hebrew nuach, distinct from Gen 5:29 nacham/comfort wordplay). Initial cases do not mean a completed Bible-wide name inventory. [Binding name policy](../docs/OLT-033_BIBLEWIDE_NAMES_UNDERWORDS.md).
- **OLT-034 (MERGED, post-merge GitHub Actions verified on main):** one **source-first OLT core** in the current repo with separately versioned future language repositories. Source authority is original Hebrew, Biblical Aramaic where appropriate, and original Greek once RP2018 is pinned/imported; **English master lexical research is a reference and NOT a translation pivot**. Versioned Python source-packet generator, schema contracts and six EMPTY locale profiles do not translate a single chapter. [Architecture and release boundaries](../docs/OLT-034_MULTILINGUAL_ARCHITECTURE.md).
- The multilingual work retains every prior Genesis English word lock, OLT-022 In/with interpretation and note, and all independent linguistic/publication blockers. **No translation has been independently approved or released.**

## GitHub engineering status — VERIFIED

- OLT repository is **PUBLIC**. GitHub branch API reports **main protected** with required status check **foundation** (app ID 15368, enforcement level **everyone**). The complete protection policy, including possible administrative bypasses or review settings, is **not accessible** through the connected integration; do not assume those sub-settings.
- The required foundation workflow runs on **every Pull Request**, without path filters. OLT-030 set explicit contents: read, checkout persist-credentials: false, and Node 24 GitHub actions checkout@v6 and setup-python@v6. Its release gate fails if Genesis becomes falsely publishable.
- The OLT-030 PR check passed **205/205** Python tests; the OLT-031 PR check passed **217/217** Python tests. The dedicated OLT-031 source review triage passed **12/12** tests, with exact committed-output regeneration.
- On the OLT-031 merged main commit, the foundation, OLT-031 and lexicon candidate GitHub Actions completed successfully.
- OLT-025 through OLT-029 converted all 16 previously directly writing workflows to **read-only research verifiers** and included output-only PR-trigger coverage. The all-workflows negative test no longer assumes exactly 22 workflows; it checks **every existing workflow** as new ones are added.
- The old runner-admission problem is historically recorded in [OLT-CI-001](https://github.com/Northsw-spec/OLT/issues/7), **closed after hosted jobs began executing**. Its original root cause was not conclusively determined.
- **Remaining CI maintenance:** some specialized workflows still refer to older GitHub JavaScript action versions. The required foundation check has already been upgraded. A future CI modernization must be tested rather than presumed compatible.

## Hebrew corpus, Genesis 1 and edition boundary — VERIFIED SOURCE COUNTS

- **39** imported OT books; **23,213** verses; **306,785** original source word tokens. Full-source imports and original-ID crosswalk are linked to pinned upstream revisions; imported annotations and dictionary meanings do **not** constitute independent OLT philological approval.
- **9,519** distinct exact observed lemma-component keys; **9,252** mapped through original-source identifier evidence and **267** unresolved (256 plus-marker keys and 11 other missing-key cases). Unresolved IDs are **not** silently merged with a similar root or Strong number.
- Genesis 1: **31 verses**, **434** actual source word tokens, **97** exact source lemma IDs, **427** word tokens with numeric lemma and **7** nonnumeric grammar-only word tokens. **50** wayyiqtol-labelled forms are counted from original OSHB source morphology, not independently reanalyzed by a scholar.
- **3 owner-locked English lexical families** remain bara = shape, asah = make, raqia = firmament; **94** non-owner English lexical families still require editorial decision. No additional English family was approved in OLT-031.
- [OLT-031 multi-fragment triage](../data/research/olt_031_lemma_variation_triage.json) contains **42** exact-source lemma cases with more than one **unapproved** English research fragment, including **322** original-source word contexts. Another **55** lemmas have one research fragment in the current corpus. Fragment differences alone do not establish polysemy, semantic homonymy, lexical identity or alternative words suitable for linked underword display.
- The 31-verse English chapter is a **complete source-aligned RESEARCH PREVIEW**, not an independently reviewed English Bible translation. Its research wording, editorial bracketed supplements and scholarly notes remain unapproved for publication.

## Binding translation decisions, preserved

- Genesis 1:1 main research sentence: **In the Beginning [of His Power] God — He shaped the Heavens and the Earth.** The bracketed supplement is a clearly disclosed theological/intertextual addition, absent from original Hebrew Genesis 1:1, with the separate research note.
- In Genesis 1:1 **only**, purple **In** is displayed with a blue lower-case **with** directly beneath it. This is an explicitly owner-selected **binitarian canonical interpretation**, not a verified instrumental Hebrew gloss or a proven homonym. See [OLT-022](OLT-022_GENESIS_1_1_IN_WITH_UNDERWORD.md) and [OLT-023](OLT-023_GENESIS_1_1_HTML_RESEARCH_LAYOUT.md).
- Genesis 1:4 first clause remains exactly **And God — He saw the light, that [he was] — good.**
- OLT wayyiqtol policy: independently identify each actual Hebrew verb form; when it is **wayyiqtol**, use English **simple past**, not perfect/pluperfect. Do not misclassify jussive, participle, qatal or yiqtol forms.
- The owner-defined binitarian framework includes **one God, the eternal uncreated Son, and the Father's and Son's common creation work**. The doctrinal framework does not authorize changing the Hebrew source or asserting that a theology is a compulsory lexical gloss. See [Masterprompt](MASTERPROMPT.md) and [OLT-021](OLT-021_BINITARIAN_CREED_CLARIFICATION.md).

## Still open — substantive work

The standing [OLT-017 independent lexical review issue](https://github.com/Northsw-spec/OLT/issues/6) requires independent Hebrew morphology verification, source-based lexical sense selection for the **94** pending families, assessment of the 42 contextual-fragment variation cases, genuine evidence-based linkage decisions, and owner editorial approval. The existing OLT-017A/017B research sources are **not** a completed independent signoff.

A bilingual A4 ODT/PDF with physically verified footnotes and visual print QA, independent lexical/verse approvals, and a separate publication authorization remain **BLOCKED**. **Passing GitHub Actions is engineering evidence, never automatic approval of biblical scholarship.**

---

## Historical checkpoint chronology (recorded 29–30 October 2026; superseded status where noted)


**Project:** Olund's Linked Translation  
**Canonical repository:** https://github.com/Northsw-spec/OLT  
**Latest completed data checkpoints:** OLT-002, OLT-003, OLT-004, OLT-005, OLT-006, OLT-007, OLT-008, OLT-009, OLT-010, OLT-011, OLT-012, OLT-013, OLT-014, OLT-015 and OLT-016.

## VERIFIED BY ACTUAL FILES AND GITHUB ACTIONS (AUTOMATIC DATA VALIDATION)
- 39 WLC/OSHB Old Testament book datasets, 23,213 verses, 306,785 source word tokens.
- 9,519 distinct **exact OSHB lemma-component keys**, including disambiguating letters and special plus-marked keys.
- Pinned OSHB source and HebrewLexicon commits, SHA-256 provenance and CC BY 4.0 attribution.
- OLT-004 crosswalk: **9,252** observed exact keys have explicit AugIndex → LexicalIndex mapping, with target BDB and Strong IDs validated against the original XML entry records.
- **267** remain without exact AugIndex links: **256** plus-marked keys and **11** other missing-key cases; not silently merged with other lemmas.
- Genesis 1: all **434** original word tokens from 31 verses appear in the source-ledger; **97** unique exact lemma IDs all have direct LexicalIndex/BDB/Strong crosswalks; **50** wayyiqtol-labelled original tokens appear in the OSHB morphology.
- Genesis owner locks attached to exact imported source identifiers: `1254 a` (bara) **5** tokens; `6213 a` (asah) **7** tokens; `7549` (raqia) **9** tokens.
- All generated reports explicitly mark **English choices and independent philological verification as NOT APPROVED / NOT DONE**.

## SOURCE-OF-TRUTH ARTIFACTS
- `data/imported/manifest.json`: source import and hashes.
- `data/quality/corpus_audit.json`: MT word identities, morphology/source discrepancies.
- `data/quality/verified_id_crosswalk.jsonl`: verified lookup ID chain for all 9,519 source lemma keys, including unresolved statuses.
- `data/quality/verified_id_crosswalk_report.json`: 9,252/267 resolution.
- `data/quality/genesis_01_source_review_dossier.json`: Genesis 1 first source-backed **434-word review dossier**; each token has dictionary references and blank English alignment.
- `data/quality/unresolved_lexeme_triage.json`: all 267 source-ID exceptions with real occurrences and no unauthorized lemma merges.
- `data/quality/genesis_01_dictionary_study_cards.json`: all 97 Genesis 1 lemma research cards; 94 new English decisions pending, three owner-locked families present.
- `docs/OLT-006_STATUS.md`: scope, limitations and next review gates.
- `lexicon/hebrew.json`: separate seed of owner-locked word families, NOT full approved lexicon.
- `docs/MASTERPROMPT.md`: governing style and tense rules; under-word links are vertical.

## WHAT IS *NOT* COMPLETE
1. The entire 9,519-entry OLT English **approved** lexicon: it is an *automatic sourced candidate lexicon*, not 9,519 approved English choices.
2. Independent academic review of actual morphology and all cross-references.
3. Interpretation of OSHB special `+` lemma markers and analysis of the 11 other missing AugIndex IDs.
4. The Genesis 1 translation: none of the 434 word-to-English surface alignments has yet been certified. A complete prose translation must be rebuilt from the source, not copied from prior drafts.
5. Scholarly notes and justified lexical/homonym/Christological links bound to actual verse anchors.
6. Visually inspected bilingual ODT/PDF and independent verse-by-verse release approval.

**Correct status:** automated source/identifier coverage **PASS**; human lexical research, grammar verification and biblical publication **BLOCKED**.

## VERIFIED CI RUNS
- [OLT-004 exact XML mapping](https://github.com/Northsw-spec/OLT/actions/runs/40922220919)
- [OLT-005 Genesis review dossier](https://github.com/Northsw-spec/OLT/actions/runs/40922541903)
- [OLT-006 exception triage and study cards](https://github.com/Northsw-spec/OLT/actions/runs/40925657427)

These verify implemented scope only, not the entire Bible translation.

## OLT-007 — FULL STRUCTURED BDB IMPORT, SOURCE-LEVEL PASS
- The pinned original `BrownDriverBriggs.xml` has been re-imported into a deterministic compressed JSONL preserving every original XML entry's tree of nodes, attributes, text and tails. **11,845** source BDB entries, with **8,989** nested sense nodes and **3,952** reference nodes across the corpus.
- Original-source SHA-256 and reproducible archive SHA-256 recorded in `data/quality/bdb_nested_manifest.json`.
- All **97 Genesis 1 research cards** have source-linked, structured BDB sense evidence and **97 distinct referenced BDB entries**, in `data/quality/genesis_01_bdb_sense_evidence.json`.
- Full structured dictionary archive: `data/imported/lexicon/bdb_nested.jsonl.gz`.
- The archive is **imported dictionary research evidence**, not an OLT-approved gloss or translation. Morphology independent review, 94 new Genesis lemma choices, the full English/MT chapter and publication remain **BLOCKED**.
- [OLT-007 GitHub Actions](https://github.com/Northsw-spec/OLT/actions/runs/40926253088) checks exact data scope, the nested XML structure and the explicit release blocker.

## OLT-008 — First literal English research alignment: Genesis 1:1
- [Genesis 1:1 original-source alignment proposal](../data/research/genesis_01_verse_01_alignment_proposal.json): all **7** original Hebrew word tokens mapped to provisional English surfaces; both direct object markers accounted for; BARA source tag **HVqp3ms (Qal qatal 3ms)**, not wayyiqtol.
- First plain lexical candidate: **“In the Beginning God — He shaped the Heavens and the Earth.”**
- `[of His Power]` appears only as a separate optional intertextual-theological research variant, explicitly not a word in Hebrew Genesis 1:1.
- [Genesis 1 word-family research queue](../data/research/genesis_01_97_lemma_review_queue.json) includes **97** distinct lemma keys, **94** awaiting new English-family decisions and **3** with already owner-locked English families.
- Seven additional original tokens in Gen 1:11, 12, 28–30 have only preposition + pronominal suffix and **no numeric lemma ID**. All seven are now accounted for individually as grammar-only research proposals (`in him`, `to them`, `to you`), not fabricated dictionary lemmas. They are separate from 427 numeric-lemma component occurrences among 434 source word tokens.
- A negative test rejects neutral `it` even inside proposed grammatical-source English, as well as fabricated token ID, wrong Hebrew morphology and owner lock changes.
- [OLT-008 GitHub Actions PASS](https://github.com/Northsw-spec/OLT/actions/runs/40929329346): source fixture/proposal checks only, not independent grammar or publication approval.

**Still blocked:** The proposed Genesis 1:1 English is *not a published approved verse*. Genesis 1 remaining 94 new English word families, full 434 word alignments, independent Hebrew morphology, original Hebrew+English ODT/PDF, all real footnotes, optional typological links, and human final philological review remain unfinished.

## OLT-009 — Genesis 1:2–5 real Hebrew token alignment / research proposals

- All **45 of 45** actual original source word tokens across Genesis 1:2–5 have a fresh proposed English source span, original Hebrew form, OSHB ID, exact lemma, morphology code, and linked dictionary references in `data/research/genesis_01_verses_02_to_05_research.json`.
- Source token counts: Genesis 1:2 (**14**), 1:3 (**6**), 1:4 (**12**), 1:5 (**13**).
- **Seven source-tagged wayyiqtol forms** are rendered in English simple past. Gen 1:3 `yehi` remains jussive and Gen 1:2 `merachephet` remains Piel feminine participle. Gen 1:5 second `qara` remains qatal, not wayyiqtol.
- Genesis 1:4 EXACT approved first clause: `And God — He saw the light, that [he was] — good.`
- The four English verse paragraphs and **9** scholarly-note outlines are research proposals, not independent lexical approval.
- Genesis 1:2 `ruach` is recorded as potentially **spirit/wind/breath**; the OLT choice `Spirit of God` is still a researched proposed interpretation.
- The general grammatical-gender explanation is restricted to Bible page one, never repeated as boilerplate.
- Combined Gen 1:1–5 source-aligned research now covers **52 original word tokens**, of 434 in full Genesis 1. This is not a finalized 52-word Bible translation.
- Negative tests now include wrong source IDs, incorrect morphological form, invalid wayyiqtol English tense, false jussive/participle classification, wrong feminine `Earth — she was` agreement, owner-locked Gen 1:4 wording violation, prohibited `it`, invented object-marker rendering and typology wrongly upgraded to lexical homonymy.
- [OLT-009 source-scoped CI](https://github.com/Northsw-spec/OLT/actions/runs/40931923716) and [working original-token research dataset](../data/research/genesis_01_verses_02_to_05_research.json).

**Release remains BLOCKED:** the other 382 original Gen 1 word-token English alignments, independent morphological review, remaining 94 owner-unapproved lexical families, detailed footnotes, printed English/Hebrew ODT/PDF, scholarly signoff and validated under-word links.

## OLT-010 — Genesis 1:6–10 source-backed research, GitHub Actions PASS

- Pinned OSHB/WLC source-alignment dataset: [data/research/genesis_01_verses_06_to_10_research.json](../data/research/genesis_01_verses_06_to_10_research.json).
- **63 of 63 original word tokens** accounted for in five verses: 11 + 17 + 10 + 13 + 12. Their source entries contain the original pointed Hebrew word, original lemma annotation, morphology, stable token ID and dictionary source references.
- **31 exact lemma identifiers** occur, and **11 OSHB-source-tagged wayyiqtol** verb forms are rendered through simple-past English.
- Original Hebrew yiqqawu in 1:9 is Niphal jussive 3mp, and veteraeh is Niphal imperfect 3fs; neither is improperly treated as narrative wayyiqtol. In 1:6 yehi is jussive, vihi is imperfect in a volitive context, and mavdil is a Hiphil participle. Note the distinction between the two called forms in Genesis 1:10.
- `asah (6213 a) → made` and `raqia (7549) → firmament` are enforced with source-aware negative tests. The zero English lexical surface of the Hebrew direct-object marker is explicit.
- Research-only proposed English wording preserves deliberately unfamiliar syntax (for example, `between waters to waters` and `day second`); editorial choices and potential supplied words remain marked as such. No independent approval is inferred.
- The Genesis 1:6–10 research ledger has **13** linked preliminary philological/semantic note records. Special concerns include the possible later ritual connotations of miqveh, which must not automatically become lexical homonym claims.
- **Cumulative Genesis 1:1–10:** 7 + 45 + 63 = **115 / 434 original source word tokens** now have English research proposals (**26.5%**). **319 tokens remain** for later preliminary English alignment.
- [OLT-010 GitHub Actions PASS](https://github.com/Northsw-spec/OLT/actions/runs/40937873061) and [foundation CI PASS](https://github.com/Northsw-spec/OLT/actions/runs/40937873432).
- Next checkpoint: [OLT-011 – Genesis 1:11–15](https://github.com/Northsw-spec/OLT/issues/5).

**Non-certification:** This verifies automated source matching and explicit research-proposal tests, not independent philology, approved word families, proofread scholarly notes, final visually inspected bilingual ODT/PDF or Genesis 1 publication. The full approved OLT English lexicon remains incomplete and chapter RELEASE remains BLOCKED.

## OLT-011—016 — FULL Genesis 1 original-source research coverage (not an approved translation)

A clean sequence of independent source-corpus audits and research proposal tests has now produced:
- Gen 1:11–15 (OLT-011): **69** source word tokens, **8** source wayyiqtol, including two preposition/pronominal-suffix nonnumeric tokens. [Source research](../data/research/olt_011_genesis_11_15.json), [CI PASS](https://github.com/Northsw-spec/OLT/actions/runs/40941977638).
- Gen 1:16–20 (OLT-012): **59** source word tokens, **6** source wayyiqtol. [Source research](../data/research/olt_012_genesis_16_20.json), [CI PASS](https://github.com/Northsw-spec/OLT/actions/runs/40941977646).
- Gen 1:21–25 (OLT-013): **74** source word tokens, **9** source wayyiqtol. [Source research](../data/research/olt_013_genesis_21_25.json), [CI PASS](https://github.com/Northsw-spec/OLT/actions/runs/40941977648).
- Gen 1:26–31 (OLT-014): **117** source word tokens, **9** source wayyiqtol, including five additional nonnumeric grammatical pronoun/preposition tokens. [Source research](../data/research/olt_014_genesis_26_31.json), [CI PASS](https://github.com/Northsw-spec/OLT/actions/runs/40942358751).
- Combined OLT-008 through OLT-014: **434 / 434 original Hebrew word tokens**, **31 / 31 verses**, **50 actual OSHB-source-tagged wayyiqtol forms**, **97 distinct source lemma IDs**, **7 nonnumeric grammar-only tokens** and **13 zero-surface Hebrew object markers**. The cross-check verifies token uniqueness, original verse/ordinal, original Hebrew spelling, source lemma/morphology and the locked lexical families. [Whole-chapter alignment JSON](../data/research/genesis_01_complete_research_alignment.json), [Hebrew+English RESEARCH preview](../genesis/GENESIS_01_SOURCE_RESEARCH_PREVIEW.md), [OLT-015 CI PASS](https://github.com/Northsw-spec/OLT/actions/runs/40942756926).
- OLT-016 creates a [97-lemma source-linked editorial decision queue](../data/research/genesis_01_lexeme_editorial_queue.json) with all actual original words, dictionary IDs, contextual English fragments and empty under-word homonym slots. **42** source lemmas appear with multiple English-fragment forms (often due to word inflection, conjunctions and context; NOT proof of semantic homonymy), **94** new English lexical families remain unapproved and **3** families remain owner-locked. [OLT-016 CI PASS](https://github.com/Northsw-spec/OLT/actions/runs/40943256086).

### Hard noncertification limits
1. **English lexical approval = NOT COMPLETE.** The 94 new English families are candidates, not certified meanings. An owner-approved `bara/asah/raqia` family does not turn an entire verse into a final approved translation.
2. **Hebrew morphology = SOURCE-TAG AUDITED, NOT INDEPENDENTLY REVIEWED.** The 50 wayyiqtol forms are counted from real OSHB morphology annotations; this is not independent academic approval of every parse.
3. **Homonyms = NO VERIFIED UNDER-WORD ALTERNATIVES YET.** Source IDs and spelling alone do not authorize theological or linguistic word links. Future evidence-backed homonym alternatives must display *below* the associated English word, never as inline slash text.
4. **Christian cross-references = RESEARCH ONLY**, even where canonical comparisons to John 1:1–3 and Col 1:15–17 are recorded. A canonical Christological interpretation is not a new Hebrew dictionary meaning.
5. **Print edition = NOT COMPLETE.** The entire Markdown chapter is labeled unapproved. Genuine edited footnotes, verified root correspondences, original-script book design and visual ODT/PDF quality assurance are unfinished. The basic Hebrew grammatical-gender notice is to appear only once on the eventual Bible opening page.
6. **Genesis 1:1 and 1:4 exact owner decisions remain visible**, with theological additions such as `[of His Power]` transparently separate from base source Hebrew.

**Correct present state:** Genesis 1 original token-to-research-English coverage **100%**; approved OLT translation, complete whole-OT English lexicon and publication **BLOCKED**.

## OLT-017A — First contested-lexeme scholarly review wave

Five source-linked, explicitly research-only scholarly dossiers have been added in [OLT-017A scholarly report](OLT-017A_SCHOLARLY_REVIEW.md) and [machine-readable evidence](../data/research/olt_017a_scholarly_wave.json):
1. Gen 1:1 reshit: Kantor (2025) vs Holmstedt (2022) published abstracts disagree on traditional/adverbial readings. The optional [of His Power] is not an independently attested Hebrew word in Gen 1:1.
2. Gen 1:2 ruach: the wind/breath/spirit semantic range and published scholarly debates remain open.
3. Gen 1:21 tanninim: varying marine creature, serpent and dragon contexts, without false zoological precision.
4. Gen 1:26 tselem and demut: different lexical source words, a scholarly parentage reading and Christian canonical interpretive comparisons, not automatically Hebrew lexical synonyms.
5. Gen 1:28 vekhivshuha: an imperative with a 3fs object suffix; provisional and subdue her preserves an original feminine referent.

Research source limitations are disclosed, including abstract-only conclusions when full journal articles were unavailable. [OLT-017A GitHub Actions](https://github.com/Northsw-spec/OLT/actions/runs/40943849658) validates research metadata, not the scholarly conclusions themselves.

Approved new English word families: **0**. Approved homonym links: **0**. The 94 unapproved Genesis 1 English lexical families, all independently reviewed word-level semantics and the final bilingual edition remain **BLOCKED**.

## OLT-018 — Genesis 1:1 bracketed intertextual supplement placed in MAIN research text
- Supersedes the prior OLT-008 plain-primary/optional-bracket draft (historical entries above remain for checkpoint traceability).
- Current main research reading: **In the Beginning [of His Power] God — He shaped the Heavens and the Earth.**
- The exact phrase `[of His Power]` is an owner-selected editorial/theological supplement, not an original Hebrew expression, and must carry a note comparing Gen 49:3 (`וְרֵאשִׁית אֹונִי`) and Deut 21:17 (`רֵאשִׁית אֹנוֹ`). Those passages use the separate noun `אֹון` meaning strength/vigor. `His` is also supplied.
- Original seven source word IDs and all lexical owner locks are unchanged. Stage: owner wording/placement accepted; independent philological proofread and publication remain BLOCKED.

## OLT-019 — Inline-anchored Genesis 1:1 research footnote (CI status unresolved)
- The owner-selected wording remains exactly `In the Beginning [of His Power] God — He shaped the Heavens and the Earth.`.
- GitHub Markdown footnote marker now appears immediately after `[of His Power]`, not after the end of the verse.
- New reusable `scripts/research_footnotes.py` and negative tests check a unique note ID, exact phrase anchor, verse reference, source evidence, and nonpublication status.
- The combined 434-token research JSON includes one note-anchor manifest entry; all original Hebrew source tokens remain unchanged.
- The first GitHub Actions attempts for this checkpoint on October 30, 2026 failed **before any job steps started**, with no test logs available; retry also failed before steps. Do not report OLT-019 as CI PASS until the required workflows actually run successfully. Prior OLT-018 CI success does not verify this new code.
- **Research preview only**: genuine page-bottom typography, scholarly review and publication remain BLOCKED.

## OLT-019 and OLT-017B — continuing work, test-runner caveat
- OLT-019 makes footnotes reusable and puts the Genesis 1:1 `[^gen-1-1-power]` marker directly after the exact main text anchor `[of His Power]`; the substantive verse wording is unchanged. A `research_note_anchor_manifest` in the 434-token research JSON records anchor ID, verse, evidence refs and status.
- Source-aware negative tests for duplicate IDs, nonexistent/repeated anchor, different reference, missing source evidence, false publication status were committed. The preview itself is synced and shows `[of His Power][^gen-1-1-power] God`.
- OLT-017B adds four documented original-source lexical dossiers (Gen 1:2 exact IDs: `8414`, `922`, `8415`, `7363 b`), with source wording, morphological annotation, BDB readings and scholarly caveats. New owner English lexical approvals: **0**; new homonym links: **0**.
- **Verification LIMIT:** GitHub Actions [OLT-019](https://github.com/Northsw-spec/OLT/actions/runs/41091217157) and [OLT-017B](https://github.com/Northsw-spec/OLT/actions/runs/41092053582) FAILED TO START JOB STEPS. The API reported empty job steps and no assigned hosted runner, including a failed OLT-019 retry. No claim of a green GitHub test can be made. Follow [OLT-CI-001](https://github.com/Northsw-spec/OLT/issues/7). Previous older green runs remain valid only for their original commits.
- No new scholarly or owner final English approval was inferred. **Genesis 1 publication remains BLOCKED.**

## OLT-020 — owner-approved permanent binitarian framework

OLT is **binitarian, not Trinitarian**. Exact owner assertion: **“THE LORD JESUS IS THE SPIRIT.”** This governs interpretive commentary while leaving the actual original-language source evidence and disputed grammatical readings separate. Hebrew `בְּ` is to be analyzed contextually; instrumentality is not inferred for every occurrence. See [doctrinal framework](DOCTRINAL_FRAMEWORK.md) and [binding decisions](DECISIONS.md).

This decision is recorded on `main`, but a GitHub Actions PASS must not be claimed until OLT-020 tests actually run. The existing Actions runner incident remains open, and chapter publication is BLOCKED.

## OLT-021 — Owner clarification: eternal uncreated Son, Father–Son unity and incarnation
- **Owner authority, 30 Oct 2026:** OLT is binitarian: **one God; the Father and Son are one; one faith; one Lord Jesus Christ; the Lord Jesus is the Spirit**.
- The Son is **ETERNAL and UNCREATED**, existed with the Father **before the foundation of the world**, and creation was their **joint Father–Son work** before incarnation.
- The eternal Son **became human through Mary**; human birth **did not initiate his eternal existence**.
- The owner's use of **Firstborn Son** / Revelation 3:14 **does NOT mean that the Son is God's first created being**. Any older assistant formulation suggesting that is expressly superseded.
- All these are owner-approved **theological/editorial interpretations**, not automatic Greek/Hebrew lexical translations. Greek `ἀρχή` and the exact meaning of each original passage still require separate source-grounded work.
- Canonical documents: [Masterprompt](MASTERPROMPT.md), [binding creed clarification](OLT-021_BINITARIAN_CREED_CLARIFICATION.md), [doctrinal framework](DOCTRINAL_FRAMEWORK.md), [decisions](DECISIONS.md), machine policy `data/policy/olt_theological_framework.json` (v2), and dedicated regression tests.
- Do not claim GitHub Actions PASS until a runner executes the test suite. Independent philological approval and Bible publication remain **BLOCKED**.

## OLT-022 — owner-selects exactly one Gen 1:1 In / with under-word
- First word **In** in Genesis 1:1 receives **with directly beneath** in the linked presentation. The unchanged primary main sentence is `In the Beginning [of His Power] God — He shaped the Heavens and the Earth.`; the `[of His Power]` research footnote remains anchored immediately after its brackets.
- This is a distinct **owner-selected binitarian canonical interpretation**, where `Beginning` refers theologically to the eternal uncreated Son who created with the Father. It is **NOT** labeled an independently established instrumental parse of `בְּ` in this verse, a separate source word or a proved homonym.
- The one allowed original-token link is `Gen.1.1:01xeN` (prefix `בְּ`, source raw `b/7225`, morphology `HR/Ncfsa`), with future print colors In purple / with blue. Nothing is automatically propagated to other English *in* words.
- [Policy](../data/policy/olt_underword_overrides.json), [documentation](OLT-022_GENESIS_1_1_IN_WITH_UNDERWORD.md), and [underword QA](../tests/test_olt_022_underwords.py). Existing complete Genesis source alignment remains 434/434; all final publication approvals remain BLOCKED.
- GitHub Actions PASS cannot be claimed unless the newest workflows actually execute and succeed; CI runner issue may still apply.
