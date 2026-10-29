# OLT-002 — Complete OT machine-readable corpus and lexicon import

## Provenance and scope
This importer creates an **entire OT word-token source catalog**, derived from pinned
Open Scriptures Hebrew Bible (morphhb) and Open Scriptures Hebrew Lexicon.
It is a dataset bootstrap, NOT an automatically certified OLT translation.

- MorphHB commit: `3d15126fb1ef74867fc1434be1942e837932691f`
- HebrewLexicon commit: `21c9add13bc727d3a951361778e97e3ff7afd1ce`
- WLC original Hebrew text: public domain.
- Morphological analyses and edited lexical data: CC BY 4.0.
- Required attribution: “Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb”.

The source also includes biblical **Aramaic** embedded in parts of the OT.
This material must be represented, not mislabeled as Hebrew.

## Imported components
- All 39 XML books into `data/imported/books/*.json`, with exact UTF-8 word
  spelling, OSHB ID, the original unmodified lemma/morphology annotation,
  verse address and ordinal.
- `data/imported/lexicon/observed_lemmas.jsonl`: **all distinct numeric
  lemma identifiers actually detected in the corpus**, frequencies, etc.
- `data/imported/lexicon/strongs.jsonl`: indexed dictionary records.
- `data/imported/lexicon/lexical_index.jsonl`: lexical crosswalk.
- `data/imported/lexicon/bdb.jsonl`: BDB entries.
- `data/imported/lexicon/aug_index.jsonl`: OSHB augmented-number → lexical
  index ID, without guessing homonym equivalences.
- `data/imported/lexicon/homograph_candidates.jsonl`: consonantally identical
  dictionary headwords flagged for **human review**.
- `data/imported/manifest.json`: source commit IDs and file SHA-256 hashes,
  coverage measurements, missing data and non-verification statements.

## Critical boundaries
A complete source dictionary is **not yet the approved complete OLT lexicon**.
Every observed source lemma still needs a vetted English rendering, KJV vocabulary
readability, morphology-aware occurrence alignment, actual homonym distinction,
and (where justified) a blue below-word link and English note. The owner-locked
renderings bara→shape, asah→make, raqia→firmament, waw→and remain authoritative
in `lexicon/hebrew.json` pending verified mapping to actual OSHB lemma IDs.

**The importer does not claim every morphological tag is correct, that a common
consonant spelling proves homonymy, or that a Bible chapter is publication-ready.**

Run via `.github/workflows/import-ot.yml`; a workflow PASS means corpus
**import coverage**, not independent lexical or theological review.
