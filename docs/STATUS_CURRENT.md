# OLT — CURRENT STATUS (2026-10-29)

**Project:** Olund's Linked Translation  
**Canonical repository:** https://github.com/Northsw-spec/OLT  
**Latest completed data checkpoints:** OLT-002, OLT-003, OLT-004, OLT-005, OLT-006, OLT-007, OLT-008, OLT-009 and OLT-010.

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
