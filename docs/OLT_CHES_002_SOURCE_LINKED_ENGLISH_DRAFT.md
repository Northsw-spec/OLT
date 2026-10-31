# CHES-002 — Original-source Genesis 1 verse QA and English-only preview

## What this checkpoint actually verifies

1. **Original PDF / authentic Hebrew verse-level QA:** `scripts/ches_oshb_verse_qa.py` imports the separately licensed Genesis 1 PDF **in memory**, verifies the exact original source PDF SHA-256, size, page count, 31 explicitly printed verse markers and 526 green-source spans against a pinned source manifest, then verifies the **31 canonical Genesis 1 verse identities** and **434 authentic OSHB Hebrew source tokens** using `olt_core.sources.load_ot_book` with existing Git-blob-integrity checks.
2. **Independent English research preview:** `olt_core/english_drafts.py` checks **all 434 existing public OLT Genesis research token identifiers, original script, lemmas and morphology** against the separately pinned OSHB corpus. It outputs the existing 31 **unapproved** English verse research proposals as runnable, traceable data. This is not copied from the private CHES text.
3. **Permanent grammar policy:** all **50 previously tagged Genesis 1 wayyiqtol** cases are rechecked against original morphology, including Qal, Hiphil and Piel wayyiqtol. A narrowly scoped set of actual existing English simple-past research fragments is accepted; a new unreviewed/perfect-tense alternative fails closed. This does not certify philological meaning or tense for other forms outside this pilot.

The two lines of evidence are **NOT a word-level crosswalk**. A green PDF span is not automatically one Hebrew word or one OSHB token; original PDF line typography, Hebrew text, vocalization and word/morpheme segmentation can differ from the independently imported OSHB edition.

## Live commands

With the existing original-language source checkout and PyMuPDF dependency:

```bash
# Read-only preview of one OLT-owned unapproved research draft:
python -m olt_core.english_drafts --verse Gen.1.1

# Complete chapter draft, STILL unapproved, NO private CHES content:
python -m olt_core.english_drafts --verse all

# Strict local original Genesis 1 PDF -> independently pinned Hebrew source VERSE QA.
# Prints metadata only; no licensed green text, no private JSON export.
python -m scripts.ches_oshb_verse_qa --pdf /path/to/gen1.pdf

# Public synthetic safety tests + original OSHB corpus checks.
python -m unittest discover -s tests -p 'test_ches_002_source_first.py' -v
```

CI obtains the **one pinned original Genesis 1 PDF** only into an ephemeral GitHub runner, checks it in memory and retains **no third-party PDF, copied CHES text, public generated extract or downloadable source artifact**. The whole 929-chapter private corpus has **not** been obtained or certified by this checkpoint.

## Stop gates

- No automatic CHES **word/morpheme ↔ OSHB word/morpheme** mapping from left-to-right position, PDF colored spans or matching verse counts.
- Original text, source morphology and existing OLT editorial research must be independently checked. Automated tests do not approve meanings, interpretations, authorship claims or the complete English Bible.
- Translation outputs remain **UNREVIEWED_ENGLISH_DRAFT**, **publication BLOCKED**, full 66-book English work incomplete and owner signoff **NOT DONE**.
- No publication/redistribution rights for CHES material or downstream language derivatives are assumed. Precise provenance and license boundaries remain in [the separate technical ingestion record](OLT_CHES_PRIVATE_INGEST.md).
- English remains the **only active target language**; later target-language repositories are deferred until owner approval of the complete English Bible.

## Next technical milestone

A private, per-verse reviewed word-alignment evidence model: original CHES PDF span coordinates + distinct original Hebrew PDF glyphs + authenticated OSHB source token IDs + explicit ambiguous/many-to-one segmentation flags. No lexical equivalence is accepted merely from page geometry. Build an editorial-review queue first; promote only independently verified token links, preserving original source rights and confidential storage.
