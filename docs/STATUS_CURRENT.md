# OLT — CURRENT STATUS (2026-10-29)

**Project:** Olund's Linked Translation  
**Canonical repository:** https://github.com/Northsw-spec/OLT  
**Latest completed data checkpoints:** OLT-002, OLT-003, OLT-004 and OLT-005.

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

These verify implemented scope only, not the entire Bible translation.
