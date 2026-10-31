# OLT-SIMPLE-ENGINE-001 — Binding lightweight CHES-first English translation engine

**Owner direction, 2026-10-31. This is the current engineering architecture.** It supersedes older directions to implement a large original-language-to-English lexicon/sense/morphology translation engine as the active build path. Historical source research and tested utilities remain valid evidence but are **not** an instruction to rebuild that old engine.

## DANMEK-007 — Permanent cancellation: no divine pronoun capitalization

**Owner's latest instruction (2026-10-31):** Do **not** specially uppercase `he/him/his/himself` when the referent is God or the LORD. This overrides and revokes DANMEK-006 entirely. Use ordinary English casing only, not religious-referent-based casing; a divine subject does not turn `·he-is-making` into `·He-is-making`. The unused helper and tests are removed; do not create a referent detector for capitalization. The **separate** subject-before-verb English OLT editorial word-order rule and private unchanged CHES JSON remain in force. [Permanent owner cancellation](DANMEK_007_NO_DIVINE_PRONOUN_CAPITALIZATION.md).

## DANMEK-008 — Optional owner English display: sur faces → faces

The owner requires the awkward original CHES English `sur faces` to appear simply as `faces` **in the derived OLT reading display only**. CHES original private JSON and faithful reader stay intact. The optional `--olt-display-faces` creates a different immutable HTML snapshot and handles an exact phrase in one fragment or exact adjacent whole fragments in the same verse. Do not touch distinct `c` markings, `the` articles, `surfaces` as a single token, or infer a certified Hebrew `pnei` word-link from PDF typography. [Implemented DANMEK-008](DANMEK_008_SUR_FACES_DISPLAY_ONLY.md). **DANMEK-007 still permanently prohibits divine-referent capitalization.**

## DANMEK-005 — Hebrew interlinear correctness vs preferred OLT English order

**Owner's clarification (2026-10-31):** The imported CHES JSON files and their Hebrew-order English interlinear are **not wrong**. The owner requests a **different editorial English OLT reading order**, specifically placing an explicit matched subject before the English verb phrase while preserving explicit referential pronouns (subject `·he-is-...` in suitable contexts). Do not rework source JSON, call source Hebrew word order defective, or simply reorder neighboring green text spans without verified source syntax. Keep two views: unchanged CHES reference and a separately versioned, reviewable OLT English reading. An isolated `c` can be a source morphology marker, and repeated `the` can reflect repeated Hebrew articles: distinguish source-faithful content from genuine extraction/display duplication before hiding anything. This is **not** a completed full-929-chapter transformation. DANMEK-009 supplies a bounded opt-in English reading layer driven solely by privately reviewed, exact source-pinned subject/verb order rules; zero automatically inferred rules or 929-chapter syntax certification are claimed. [DANMEK-009](DANMEK_009_REVIEWED_SUBJECT_FIRST.md). [Detailed owner rule](DANMEK_005_SOURCE_VALID_OLT_ENGLISH_ORDER.md).

## DANMEK-002 — YLT 1898 is authoritative for bounded noun and tense edits

**Latest binding owner rule (2026-10-31):** CHES remains the direct `.json` English source. **Every change to English tense or to an excessively modern CHES noun is adjudicated by the matching verse in Young's Literal Translation (YLT, 1898)**. Example: `portal → door` only where that specific YLT verse actually uses `door`; if YLT says `gate` or the relevant occurrence cannot be established, keep the CHES verse unchanged. Do not perform global find-and-replace, guess Hebrew→English word alignment, or create a new independent lexicon.

The [minimal implemented YLT overlay](DANMEK_002_YLT_NOUN_TENSE_AUTHORITY.md) uses a pinned historic public-domain YLT JSON and a **small candidate table** for nouns/tense only. A candidate requires one CHES original-form occurrence and one YLT target-form occurrence in the same original source chapter/verse; ambiguous/missing crosswalks remain unchanged. The editable DanMek layer is separate from original CHES private JSON. The YLT-only comparison is not Hebrew morphological certification or final English translation quality proof. Historic owner wayyiqtol simple-past policy may conflict with YLT historic presents; record and do not silently claim the two policies have already been harmonized.

## DANMEK-JSON-001 — Direct authorized CHES JSON is the canonical English input

**Owner confirmation (2026-10-31):** The owner has permission to **use CHES** and directs OLT/DanMek to consume the **existing, locally extracted CHES JSON files directly**. No additional PDF retrieval, CHES reconstruction, lemma sense resolver, dictionary engineering, or intermediate translation engine is required to produce the baseline **private English reading**. Our existing `scripts.ches_015_direct_private_reader` already implements this direct JSON-to-private-HTML path for all present source chapters.

**Minimal operational pipeline:** `~/.olt-private/ches/<source-prefix>.<chapter>.json` → strict existing JSON/source/verse validation → original CHES English fragments in source order → private English chapter reader. Optional localized corrections (including `shaped` and independently source-anchored simple-past changes) belong to a **separate, bounded overlay**, never to the immutable original JSON. Keep CHES's contextual sense choices unless a specific explicit override can be justified.

**No artificial prerequisites:** Completion of the full Hebrew token-by-token mapping, hundreds of thousands of lexical judgments, the old large engine, or fourteen-chapter source pins is **not a prerequisite** to read existing CHES JSON chapters privately. The 14 pinned paths remain optional higher-assurance research, not the default input bottleneck.

**Permissions boundary:** The owner confirms permission to use CHES; record that factual assertion without inventing the exact grant wording or claiming that machine-readable use alone grants a public redistribution/derivative license. Private corpus and rendered pages stay outside public Git. The program can be operationally complete before the entire 929-chapter source download is complete, but it must report incomplete coverage accurately.

## DANMEK-001 — CHES decides every ambiguous contextual English choice by default

**Owner decision 2026-10-31:** Do not create a second Hebrew lemma-sense-selection engine. **For every Hebrew/Aramaic lemma occurrence with multiple possible English senses, use the reading already chosen by CHES in that actual verse as the English default.** Preserve that original verse reading without speculative word-to-PDF-span links. Where token mapping cannot be demonstrated, leave the private CHES stream unchanged rather than run a broad substitute. Only the owner's explicit, bounded original-source-backed overrides (e.g. a specific occurrence of shaped or verified wayyiqtol simple past) may change a local fragment. No universal word-for-word gloss alignment, dictionary-building or chapter-by-chapter owner authorization is required to finish the minimal private reader. See [DanMek contextual default](DANMEK_001_CHES_CONTEXTUAL_DEFAULT.md).

The minimal **offline private CHES reader** is now the immediate runnable deliverable. It is *not* proof of an original-language token-level interlinear or independently authored English edition; separately granted redistribution rights and actual corpus coverage remain required for public publication. Do not substitute CHES for the Greek NT.

## Purpose and scope

Create a **small, working, deterministic Hebrew/Aramaic → English OLT draft system** that reuses CHES v2.0's existing interlinear English glosses as **privately authorized reference/source data** instead of translating every Hebrew word and contextual sense independently from scratch.

- **OT baseline:** privately import the original 929 PDF chapter files only under the owner's reported machine-readable-use permission, with resumability, exact source identity, provenance and failure-on-mismatch; the full 929-chapter import has **NOT** yet been executed or certified. Do not claim otherwise.
- **Original-language authority:** OSHB/WLC Hebrew and Biblical Aramaic provide original-script, verse, token and source morphology checks. CHES is a **third-party proposed English reading**, not a replacement for the original Bible text or an owner-approved English translation.
- **Small English rule/override layer:** apply explicit owner decisions, including `bara → shaped`, `asah → make`, `raqia → firmament` when the original lemma, morphology and context actually justify those renderings; distinguish proposed choices from certified lexical facts. Every independently established Hebrew `wayyiqtol` form must be rendered with **English simple past** (not present perfect, past perfect or archaic perfect forms). Do **not** classify a form as wayyiqtol based on English gloss, PDF layout or a guessed word match.
- **Practical output:** prioritize runnable chapter-level OLT English drafts, with per-verse source locators, provenance, revision trace, deterministic tests, and clear `UNREVIEWED_ENGLISH_DRAFT`/publication stop gates. The first existing 31-verse Genesis draft is an OLT-owned **research pilot**, not yet generated directly from CHES or owner-approved Scripture.
- **New Testament:** continue to use pinned Robinson–Pierpont 2018 Greek source evidence. CHES Hebrew OT is **not** NT Greek text, and no verified Greek→CHES-equivalent English baseline has been established. Treat the Greek/English path as a separate design problem rather than pretending CHES covers all 66 books.
- **Languages:** English is the only active target until the owner explicitly approves the **entire** 66-book English Bible. Other-language implementation remains deferred; no English-only pivot may silently override source-language evidence in future projects.

## Cost and complexity control: avoid rebuilding the previous engine

1. **Reuse first.** Extract and normalize existing authorized CHES information, preserving source boundaries. Do not recreate full lexical entry/sense inventories, exhaustive etymology, generalized grammatical generation or every contextual English decision as prerequisites to the first working chapter.
2. **Automate routine QA.** Validate chapter/verse inventory, original file hashes, exact verse references, morphology where available, known owner override rules, integrity, retry/resume and negative tests. Never equate a PDF green *text span* to a Hebrew *word* without evidence.
3. **Exception-based review.** Generate conservative candidate links/outputs and flag only ambiguous segmentation, unsupported source correspondence, textual variants, conflicting English rules, lexical uncertainties and explicit release-critical issues for manual inspection. A CHES-003-style review ledger is an **exception pathway**, **not** a requirement that a human independently reconstruct hundreds of thousands of word-to-gloss links.
4. **Bounded proof before scaling.** Test a genuine Genesis sample across multiple verse layouts and compare the real source Hebrew against CHES; record error/exception categories. Only then expand incrementally chapter by chapter. Fail closed or mark unresolved portions instead of manufacturing mappings or silently assuming correctness.
5. **Avoid expensive parallel redesign.** Do not resume the former full standalone engine, huge per-lemma scholarly queue or permanent token-by-token human validation as the default implementation roadmap. Introduce complex components only with documented, reproducible blockers and measured benefit.

## Legal, source, publication and version-control boundaries

- The owner reports permission to use CHES as **machine-readable source data**. Do not infer public redistribution, modified PDF distribution, training permission, commercial terms, translation-derivative permissions or later-language rights without reviewing the actual grant.
- Keep copyrighted CHES text, source PDFs and internal alignments in `.olt-private/`; public GitHub may retain importer code, reproducible synthetic tests, metadata and accurate attribution in the relevant technical/source documentation.
- A green GitHub Actions run demonstrates engineering checks, **not** linguistic correctness, granted copyright rights, owner approval or Scripture publication.
- **`README.md` stays exactly zero bytes**, with its own regression test. Do not restore a landing-page status.
- **Retain the existing Git commit history** for reproducibility, incident traceability, test provenance and rollback. Do not force-push a rewritten history, delete the repository or remove source attribution as a search-engine-visibility tactic without a separate, explicit owner decision and impact review. Historical commits and external caches might persist regardless.

## Priority order

**CHES-004 and onward:**
1. Make the private import robust across representative OT chapter layouts and establish trustworthy verse-level correspondence with authentic OSHB/WLC.
2. Implement a **lightweight CHES-informed English draft generator** with explicit owner overrides, source-referenced uncertainty and no false word-equivalence claims. Produce and inspect real Genesis output.
3. Evaluate QA coverage and exception rates; scale progressively across OT only when safe, with resumption and copyright boundaries.
4. Design a separate lean Greek/NT English workflow using evidence from the already pinned Greek editions.
5. Maintain owner review/signoff and publication gates throughout; wait on all other language projects.

## Precedence and continuity

This file and the opening `OLT-SIMPLE-ENGINE-001` section of `docs/MASTERPROMPT.md` govern **active engineering strategy** where earlier instructions conflict. `docs/OLT_ENGLISH_FIRST_OWNER_GATE.md` continues to govern target-language priority and owner approval; source manifests/tests govern facts about corpora; explicit owner literal/grammatical/doctrinal policies remain in force, without turning theological interpretation into falsely certified source-language lexical meaning. Older plan documents are retained for traceability, not as parallel obligations to implement the superseded expensive architecture.
