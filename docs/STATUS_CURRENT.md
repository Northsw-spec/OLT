# OLT — CURRENT STATUS (2026-10-31)

**Canonical repository:** https://github.com/Northsw-spec/OLT  
**Latest fully merged and post-merge CI-verified engineering checkpoint:** **OLT-037D**, [PR #34](https://github.com/Northsw-spec/OLT/pull/34), original feature merge commit **679a60ab754c4d8d8becf5e32d8a36c1edf56294**. On that exact merged `main`, [mandatory foundation](https://github.com/Northsw-spec/OLT/actions/runs/41143649686) completed **356 tests (352 passed, four intentional external-source integration skips)**, and [dedicated independent Perseus Greek lexicon research](https://github.com/Northsw-spec/OLT/actions/runs/41143649670) completed **8/8 original-source tests and 5/5 editorial safety tests**, including exact regeneration of frozen LSJ key evidence and blank scholarly review templates. The source XML confirms two literal LSJ key records for G3004 and no exact key for G3754 under the frozen query, **not** that LSJ lacks ὅτι. **No original Greek lexical identity, contextual meaning, English lexical choice, translated Scripture or publication has received independent scholarly or owner approval.**
**Translation publication:** BLOCKED. **Independent lexical/morphological signoff:** NOT DONE.

> **Status priority:** This opening section supersedes outdated present-tense claims in the historical chronological log below. Earlier reports of CI jobs failing before test startup describe an **old incident**, not the current CI state. Preserve the older reports as historical evidence, not as a live failure.

## OLT-037D — Independent Perseus LSJ source keys and blank scholarly decision gates (MERGED AND POST-MERGE CI VERIFIED)

- Independent lexical reference research now uses **Liddell–Scott–Jones, *A Greek-English Lexicon***, via Perseus Digital Library's separately pinned original Greek TEI/XML corpus, not another copy of STEPBible's own lexicon. Upstream Git commit `1c34cdf756c63cf37db61bd366d733431dbd7aa0`; two original source shards pinned by exact original Git SHA-1 and file length, **6,753,569** and **12,280,021** bytes. Original Perseus digital lexicon is **CC BY-SA 4.0** (distinct from STEPBible's **CC BY 4.0**), with explicit Perseus/Tufts and original LSJ author attribution. The original XML/definitions are fetched only into temporary CI and **NOT vendored**.
- The strict original-source key scanner indexed **2,958** native `entryFree` records in the Greek lambda XML shard and **4,512** in the omicron shard. For RP2018 editor Strong **3004**, the independent source contains two literal search key records: `n62204 / le/gw1`, `n62205 / le/gw2`. For original Strong **3754**, the source-key hypothesis `o(/ti` produced **NO EXACT XML KEY MATCH**; this is NOT proof LSJ lacks `ὅτι`, and the program does not invent or fuzzy-fill a match. Neither LSJ key ID nor STEPBible dStrong ID establishes an approved Greek lemma or contextual sense.
- Exact generated [LSJ original-source key evidence](../data/quality/olt_037d_perseus_lsj_lexical_entry_keys.json) SHA-256 `ea9f6e031897630cd5645ace24797e91e145f2018e5dba236b8951d5f1aa4973` is linked to [frozen original Greek source-context dossiers](../data/quality/olt_037c_greek_contextual_research_dossiers.json), SHA-256 `08d58d6ce13b9803ed1936dfde1ed249f3c32e44af7bdc50b8665adb593bab69`; both must remain intact.
- Separately [generated two blank scholarly/owner research templates](../data/research/olt_037d_independent_greek_review_templates.json) are linked to the exact original-source evidence. They require separate cited Koine Greek lexicon evidence, grammatical/contextual analysis, documented philological review and owner approval. **All proposed meanings, referenced source quotations, reviewer names/signoffs, owner decisions, English master words and target translations remain empty/false.** Tests reject false PASS, counterfeit approvals or premature publication. Actions CI is not a philological referee.
- [Feature PR #34](https://github.com/Northsw-spec/OLT/pull/34) merged as `679a60ab754c4d8d8becf5e32d8a36c1edf56294`. Exact merged `main` [OLT-037D CI run 41143649670](https://github.com/Northsw-spec/OLT/actions/runs/41143649670) finished **8/8 pinned independent source integration/negative tests + 5/5 false approval tests**, confirmed `original_lsj_source_checkpoint_exactly_reproduced=true` and `blank_review_templates_reproduced_exactly=true`. Required [foundation run 41143649686](https://github.com/Northsw-spec/OLT/actions/runs/41143649686) completed **356 tests (352 passed, four deliberately skipped external-source checks)**, Scripture publication still BLOCKED. External source integration is executed by dedicated OLT-037D Actions.
- Code: `scripts/fetch_olt_037d_lsj.py`, `olt_core/greek_independent_lsj.py`, `olt_core/greek_editorial_review.py`; source manifest `data/engine/olt_037d_perseus_lsj_source_manifest.json`; tests `tests/test_olt_037d_independent_lsj.py`, `tests/test_olt_037d_editorial_protocol.py`; read-only `.github/workflows/olt-037d.yml`; [research method, source licensing and exact limits](OLT-037D_INDEPENDENT_LEXICON_RESEARCH.md).
- **NEXT OLT-037E:** investigate why G3754's literal `o(/ti` query does not match the original pinned XML entry key despite the separate Scaife LSJ online `ὅτι` entry, without conflating editions. Then independently inspect the actual Perseus entries `le/gw1` and `le/gw2` plus a dedicated Koine/NT lexicon and cite true original Greek usage. A future separately reviewed proposal may describe lexical evidence but must not impersonate qualified human/owner approval or auto-publish Scripture.

## OLT-037C — Original Greek contextual sense evidence dossiers (MERGED AND POST-MERGE CI VERIFIED)

- The first targeted human-review research dossiers cover RP2018 editor Strong **3004** (**2,315** original NT word occurrences, **83** exact Greek Unicode surface forms) and Strong **3754** (**1,287** occurrences, **2** exact Unicode surfaces). The first is the primary research case; the second controls whether the same source-evidence workflow works across different original editor morphology categories.
- Exact original STEPBible/TBESG **source** entries: `G3004G` and `G3004H` both contain the same written Greek candidate headword `λέγω`; their published English dictionary gloss evidence is respectively `to say` and `to say: call`. `G3754G` and `G3754H` both have the same written headword `ὅτι`, with publisher glosses `that/since: that` and `that/since: since`. Source notes may say `a Meaning of`; neither the note nor a shared written headword establishes a historical Greek sense assignment or a distinct verified homonym. **None of these glosses is an OLT translation.**
- [Full 266,884-byte original-source research dossiers](../data/quality/olt_037c_greek_contextual_research_dossiers.json) pin SHA-256 `08d58d6ce13b9803ed1936dfde1ed249f3c32e44af7bdc50b8665adb593bab69`. They preserve full Greek source-verse text and punctuation, original editor Beta Code and morphology, original Unicode character offsets, book-level and raw-morphology distributions, and source lexicon references. Deterministic sampled evidence includes **136** G3004 and **53** G3754 original Greek contexts, covering **every observed exact Unicode word form and original editor morphology code** plus first/last source occurrence per book. Contextual meaning is **NOT automatically inferred** from this sample.
- The program scans **all 140,149 source word positions** with original RP2018 text hash-checks, pins and cross-checks the [OLT-037B 107-case review queue](../data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json), and imports the exact external STEPBible TBESG Git blob under **CC BY 4.0** with attribution. The four BP5-only empty slots, all 28 alternative morphology analyses and independent target-language release gates remain unchanged. No English translation is generated.
- [Feature PR #32](https://github.com/Northsw-spec/OLT/pull/32) merged as `980e6b037c52b7e77af052e77d5561e1c8788b9b`. Post-merge [OLT-037C Actions run 41142190415](https://github.com/Northsw-spec/OLT/actions/runs/41142190415) passed **8/8** tests and reported `source_dossiers_regenerated_exactly=true`; required [foundation run 41142190380](https://github.com/Northsw-spec/OLT/actions/runs/41142190380) completed **343 tests (340 passed, three external-source-specific integration skips)**, publication still BLOCKED.
- Implementation: `olt_core/greek_sense_dossier.py`; tests: `tests/test_olt_037c_greek_sense_dossier.py`; read-only Actions: `.github/workflows/olt-037c.yml`; [source, methodology and review protocol](OLT-037C_GREEK_CONTEXTUAL_SENSE_RESEARCH.md).
- **Historical OLT-037C next-step outcome:** OLT-037D has now added an independently pinned Perseus LSJ bibliographic/source-key evidence layer and generated *blank* review forms. It did **not** create human editorial signoffs, certified Greek lemma meanings or any approved English verse translation. These decisions remain blocked pending qualified independent research and owner review.

## OLT-037B — Greek numeric-lexical-ambiguity research queue (MERGED AND POST-MERGE CI VERIFIED)

- From the independently pinned OLT-037A STEPBible TBESG and RP2018 source-word crosswalk, **12,539 original NT Greek word positions with more than one numerical lexical candidate** are now grouped into exactly **107 distinct original RP2018 numeric Strong-reference review cases**. These are **NOT 107 confirmed lexemes, 107 homonyms, or 107 senses**; grouping is a reproducible research-workload decision rather than an independent philological identification.
- The full [451,923-byte reproducible queue](../data/quality/olt_037b_greek_numeric_ambiguity_review_queue.json), SHA-256 `a0291d66b506f7070263e8afc8c78ac160d2f9081720993b487e0cee3bc6db5b`, contains original source word locators, actual accented Greek examples, original editor morphology frequencies, original STEPBible dStrong/eStrong/uStrong references, lexicon-headword candidates and clearly **SOURCE-ONLY** English gloss evidence with CC BY 4.0 attribution. Each of the **28** original alternative Strong/morphology editor analyses remains an explicit **separate** review record on its original word, never a new fabricated Greek token.
- All candidate selections remain null, classification statuses remain **NOT_REVIEWED** or **NOT_YET_DETERMINED**, and approvals remain false. In particular, automatic homonym/sense decisions are prohibited, `selected_dstrong=null`, `selected_greek_lemma=null`, owner editorial approval is false, independent philological signoff is false, and Scripture publication remains **BLOCKED**. The previously verified four source-only empty BP5 verse slots and separate ancillary passage variants are unchanged.
- [PR #30](https://github.com/Northsw-spec/OLT/pull/30) merged as `460fc38d268f1adf2ef816734e96a286d35b3dc2`. On merged `main`, [OLT-037B Actions run 41141177100](https://github.com/Northsw-spec/OLT/actions/runs/41141177100) executed **8/8 PASS**, downloading and hash-verifying original TBESG before matching **all 107 groups and 140,149 word positions** and confirming `exact_committed_queue_reproduced=true`. Required [foundation Actions run 41141177073](https://github.com/Northsw-spec/OLT/actions/runs/41141177073) completed **335 tests (333 PASS, 2 intentionally skipped external-source integrations)** and confirmed publication remains blocked. All skipped external-source checks execute in the applicable dedicated source-fetching workflows.
- Source-first research implementation: `olt_core/greek_lemma_triage.py`; negative and source-integration tests: `tests/test_olt_037b_greek_lemma_triage.py`; dedicated read-only workflow: `.github/workflows/olt-037b.yml`; [method and licensing limitations](OLT-037B_GREEK_LEMMA_REVIEW_QUEUE.md).
- **Historical next step completed in OLT-037C:** G3004 and G3754 now have reproducible original Greek contextual **evidence dossiers** and explicit human-review criteria. Their lexical-sense assignments, independent Greek morphology/lemma review, and owner English master choices remain unapproved. Statistical frequency and shared numeric reference are not philological proof.

## OLT-037A — Greek lexicographic source evidence (MERGED AND POST-MERGE CI VERIFIED)

- Separate original-language Greek lexical **research candidate** layer added from [STEPBible TBESG](https://github.com/STEPBible/STEPBible-Data), published under **CC BY 4.0** with explicit attribution to STEP Bible and Tyndale House Cambridge. STEPBible source commit `be4191f0082aeedddb0eff0c02c966292b2bd641`, original Git blob `efe271a1dbb73fa01f8fa6e0f164c6687757a9ae`, exactly **4,736,912 bytes**. The original 4.7 MB source is deliberately not vendored: GitHub Actions fetches the pinned commit and validates exact source bytes before reading.
- The actual source has **11,035 unique dStrong rows** under **10,847 numeric reference groups**. The official RP2018 Greek source has **5,380 different primary Strong numbers** across **140,149** source word occurrences. Numeric-only candidate lookup yields **127,610 occurrences with one dictionary candidate, 12,539 with multiple UNRESOLVED candidates, and 0 with no numeric candidate**. These are **candidate counts per source WORD OCCURRENCE**, not approved lexical identities or sense counts.
- STEPBible `eStrong`, `dStrong`, and `uStrong` remain distinct; **numeric agreement only** is used to enumerate candidates. Every original editor alternative Strong/morphology parsing retains its own separate candidate set on the **same** Greek word, rather than becoming an extra token. Even a unique candidate remains unapproved: `selected_lemma=null`, `selected_sense=null`, no owner English translation and no target-language publication.
- Reproducible committed [full candidate audit](../data/quality/olt_037_lexicon_candidate_audit.json) must exactly regenerate from both pinned sources in CI. [Research method and license limits](OLT-037_GREEK_LEMMA_EVIDENCE.md), source manifest `data/engine/olt_037_tbesg_source_manifest.json`, parser `olt_core/greek_lexicon.py`, 8 dedicated tests and fail-closed fetcher are in the repository.
- [PR #28](https://github.com/Northsw-spec/OLT/pull/28) merged as `d78f5263f325ad14c2b72d3ef8942790f8cb7912`. On merged main, [OLT-037 Actions](https://github.com/Northsw-spec/OLT/actions/runs/41138177086) passed **8/8**, while [mandatory foundation](https://github.com/Northsw-spec/OLT/actions/runs/41138177390) completed **327 tests (326 pass, one intentionally skipped in the offline foundation environment)** and retained **BLOCKED** publishing. The same integration test was executed successfully by the dedicated source-fetching workflow.
- **Historical OLT-037A next-step note:** the subsequent OLT-037B now supplies a source-verified **unreviewed research queue** for candidate ambiguity. It does not supply the still-required independent lemma-form, morphology, contextual lexical-sense, cross-source, homonym or owner editorial decisions. Engineering numeric coverage is NOT philological certification or owner approval.

## OLT-036 — Verified source Greek BP5/Unicode word-position alignment (MERGED, POST-MERGE CI VERIFIED)

- **All 27 RP2018 NT books** now have a strict, reproducible **Greek word-position crosswalk** between the pinned original editor's unaccented `source/Strongs/*.BP5` representation and the separate pinned accentuated Unicode verse CSVs. The join requires the same reference, **identical number of source words**, same ordinal and equivalent unaccented Greek base spelling for **all 140,149 words in all 7,953 word-bearing verses**. No fuzzy joins, guessed word IDs, inserted words or silent variant splices.
- **Source spelling preservation is mandatory.** Unicode word forms, their exact source offsets, original Beta Code forms, Strong references and all morphology annotations are retained. The comparison discards a documented finite set of accents, breathings, diaeresis and **iota subscript**; the latter is orthographically meaningful and is flagged explicitly for **7,675 words**. Accordingly, the equivalence is **position + lossy-normalized orthography**, NOT identical full spelling, independent text-critical evaluation or verified lexical analysis.
- **Four** BP5-only positions (Luke 17:36 and Acts 8:37, 15:34, 24:7) contain **zero original Greek words**. The **28** alternative editor morphology pairs stay attached to the same source words. Derived locators are **OLT IDs**, never publisher-native original word IDs.
- [PR #26](https://github.com/Northsw-spec/OLT/pull/26) was merged as `837daa0d7991f59de3f604da5e578e21ec833a63`; after merge, required [foundation](https://github.com/Northsw-spec/OLT/actions/runs/41136042130) passed **319/319** tests and dedicated [OLT-036](https://github.com/Northsw-spec/OLT/actions/runs/41136042172) passed **11/11** with an actual full-corpus audit and deliberate negative tampering tests. The check includes the unchanged **BLOCKED** release gate.
- Implementation: `olt_core/greek_alignment.py`; tests: `tests/test_olt_036_greek_word_alignment.py`; [methodology and limitations](OLT-036_GREEK_WORD_ALIGNMENT.md). **Greek lemma forms/senses, independent grammatical verification, approved English master lexicon, target translations and Scripture publication all remain NOT DONE / BLOCKED.**

## OLT-035D — Original editor Greek word/morphology sources (MERGED AND POST-MERGE CI VERIFIED)

- **All 27 official ByzTxt RP2018 source/Strongs/*.BP5 files** were merged byte-identically into main through [PR #24](https://github.com/Northsw-spec/OLT/pull/24); upstream v3.3.2, commit 27a45ff1b7be6c17ccbfeac414f3f55732ae8e28, public domain.
- The editor's actual annotated original Greek data contains **140,149 primary Beta Code word forms** with a Strong reference and morphology tag and **28 alternative parsing pairs** on existing words. **Source verse slots: 7,957, including four EMPTY positions** (Luke 17:36; Acts 8:37, 15:34, 24:7), leaving **7,953 nonempty** word-containing verse slots that align at the **verse-reference level only** with the Unicode Greek source corpus. The empty positions contain NO original Greek words.
- Source-traceable word-position IDs are **OLT-derived**, not original native publisher word IDs. **At checkpoint OLT-035D**, Greek lexical lemma forms, the later verified lossy-normalization Unicode word-position join, independent morphology review, English master lexicon and target-language translations were NOT DONE. The newer **OLT-036** section above supersedes only the Unicode word-position join status; all scholarly and translation approval blockers remain.
- New source registry `data/engine/olt_035d_greek_word_source_manifest.json`, parser `olt_core/greek_words.py`, detailed [research notes](OLT-035D_RP2018_OFFICIAL_GREEK_WORDS.md), dedicated GitHub Actions and negative tests have **passed on merged main** (OLT-035D run 41132815893: 18/18; mandatory foundation run 41132815871: 308/308). Earlier failing PR attempts and subsequent source-faithful corrections are recorded in CI history; no tests were bypassed. All original OLT owner translation/publishing restrictions remain intact.

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
