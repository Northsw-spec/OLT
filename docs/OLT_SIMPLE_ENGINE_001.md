# OLT-SIMPLE-ENGINE-001 — Binding lightweight CHES-first English translation engine

**Owner direction, 2026-10-31. This is the current engineering architecture.** It supersedes older directions to implement a large original-language-to-English lexicon/sense/morphology translation engine as the active build path. Historical source research and tested utilities remain valid evidence but are **not** an instruction to rebuild that old engine.

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
