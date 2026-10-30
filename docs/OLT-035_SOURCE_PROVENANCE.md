# OLT-035 — Original-language source fingerprints and bilingual-corpus staging

**Date:** 2026-10-30. **Canonical source:** Northsw-spec/OLT. **Status:** engineering research checkpoint; no scholarly release.

## Scope, actual deliverables and limits

OLT-035 strengthens OLT-034 from a Genesis 1:1 research packet example into a reusable source-reader boundary. Its goal is **cryptographic snapshot verification before every original-language record is used**, not a machine-translated Bible.

1. The existing 39 imported Open Scriptures Hebrew Bible / Westminster Leningrad Codex JSON books are fingerprinted by Git object blob SHA-1 in `data/engine/olt_035_source_provenance.json`. These digests represent exactly what was in canonical OLT main commit `bfbd7368b3b69dcf2b13e7dfa5f4dedf287c77c3`; they do NOT identify an independently reviewed translation.
2. All 39 upstream XML SHA-256 values copied from the earlier OLT import are retained separately. Their source is Open Scriptures `morphhb` commit `3d15126fb1ef74867fc1434be1942e837932691f`. **This checkpoint does not redownload/recompute the remote original XML SHA-256**, only verifies that those values are the same ones in OLT's previously committed import manifest. The original files are not stored in this repository.
3. The current OT audit contains **39 books, 23,213 verses, 306,785 source word tokens, 301,837 source-tagged Hebrew words and 4,948 source-tagged Biblical Aramaic words**. Existing source tagging, original immutable word IDs, prefixes, augmented homonym suffixes (`1254 a`, `1254 b`), plus-marker ambiguity, vowel points and accents are kept without semantic guesses.
4. A first **RP2018 Greek NT source sample** has been imported: the entire **Third Letter of John**, 14 genuine Greek **VERSE TEXTS**. It is a UTF-8 CSV file copied byte-for-byte from the upstream ByzTxt repo release **v3.3.2**, exact upstream commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`. Source path `csv-unicode/ccat/no-variants/3JO.csv`; exact Git blob `296e85242768aab57007a69cf62b92aef0b5067b`. Local path `data/imported/nt/rp2018/3JO.csv`.
5. A new Greek verse-only schema forbids claim of real lemma, morphology or source word IDs when working with the convenient Unicode CSV, because **that CSV does not encode stable original word IDs or Greek morphology**. The Greek material is authentic source verse text, not an independently verified full 27-book NT word index. Original `source/Strongs` and `source/CCAT` files are identified by the upstream as the authoritative inputs; derived Unicode CSV must be compared to those originals before claiming full textual certification.
6. Original Hebrew/Aramaic words and Greek verse strings are **separate evidence objects** from English master research and from all target-language translations. OLT-034's sample English reference is not promoted into a Greek or Amharic source.

## Data sources and rights

- **OSHB / Westminster Leningrad Codex (WLC):** https://github.com/openscriptures/morphhb — WLC text public domain; Open Scriptures original lemma/morphology annotations CC BY 4.0. The source and downstream consumers must give required attribution: “Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb”. The committed source manifests include original import hashes; source language `H` => Biblical Hebrew `hbo` and `A` => Biblical Aramaic `arc`, based on imported morphology tags, without claiming independent manual approval.
- **ByzTxt Robinson–Pierpont 2018:** https://github.com/byztxt/byzantine-majority-text/tree/27a45ff1b7be6c17ccbfeac414f3f55732ae8e28 — GitHub repository identifies release v3.3.2 as RP2018. The upstream LICENSE declares public domain, including text/code. Its `README.md` warns that Unicode CSV is converted and original `source/CCAT` / `source/Strongs` files are the editors' source of truth.
- **Edition scope:** RP2018 is selected by the owner, not silently replaced by later RP2026 publications. A commit from December 2024 may pin RP2018's digital text; version date and textual edition date are separate things.

## Code and output

The new module `olt_core/sources.py` provides:

- `git_blob_sha1(raw_bytes)`: exact file Git object hash.
- `read_provenance()`: checks that the registry is research-only, 39 source books are represented, and the named editions/commits match.
- `load_ot_book(book)`: refuses any imported OT book whose bytes, word-level source-import commit or path differ from its committed snapshot.
- `normalize_ot_verse(book, verse_id)`: returns exact source-token rows with original unicode, stable OSHB word ID, raw lemma and morphology, encoded source language (Hebrew versus Aramaic), unresolved lemma warning and no target-language Bible text.
- `verify_ot_corpus()`: checks all 39 stored book blobs, 23,213 verses, 306,785 original unique IDs and exact Hebrew/Aramaic morphological tag counts.
- `read_greek_3john()`: insists on the exact upstream RP2018 blob before returning 14 authentic Greek source verse strings with `word_token_ids: null`, `lemma_ids: null`, `raw_morphology: null`, `translation: null`.
- Read-only CLI (Python 3.12, no external dependencies):

```sh
python -m olt_core.sources --audit-ot
python -m olt_core.sources --ot-verse Gen Gen.1.1
python -m olt_core.sources --ot-verse Dan Dan.2.5
python -m olt_core.sources --greek-3john
```

Use `python -m unittest discover -s tests -p 'test_olt_035_source_adapters.py' -v` to exercise positive and negative cases. All commands are read-only. Hash and corpus checks are performed locally in Ubuntu Actions, not declared PASS based on test labels.

## Scientific limitations and next required checkpoints

- **Exact imported file SHA ≠ verified published edition**; SHA checks establish byte identity against a frozen known snapshot, not that the source has no scribal, conversion, morphological or parsing errors.
- **Source morphology codes ≠ independent morphological judgments**. Aramaic is identified by imported OSHB tags. Each contested grammar form still needs external expert review.
- **The NT has one imported verse-level sample book**, not 27 fully imported Greek books. Stable word-token identifiers, morphology and lemma mappings must be imported from verified original Greek source facilities; a whitespace-derived word index is **not** acceptable as canonical identity without a formally reviewed tokenization method.
- **No new target-language translations**; current English master is incomplete and reference-only. All locale profiles remain untranslated.
- **No silent weakening of OLT owner decisions.** English Gen 1:1 [of His Power] plus its note, OLT-022 In/with, OLT-033 God/Elohim — Mighty Governance, Noah — Rest and all other owner locks remain unchanged.
- Next: full 27-book RP2018 text import tied to the original authoritative files, explicit edition/variant validation, exact Greek word/lemma/morphology provenance, and separate independent lexical review.

**Publication remains BLOCKED; no Hebrew, Greek or target-language chapter is philologically certified.**

## Superseding OLT-035B extension (later checkpoint, 2026-10-30)

OLT-035B has now imported the **other 26 canonical Greek book continuous-text CSVs**, resulting in all 27 RP2018 books stored as exact upstream byte-matching Greek verse text. The two additional passage files PA.csv and ACT24.csv were preserved **separately**, not silently overwritten into the ordinary books. The historical first 3 John-only source manifest in OLT-035 remains correct for that earlier milestone but is NOT the active completeness inventory; see `data/engine/olt_035b_rp2018_verse_inventory.json`. **Word-level original Greek token IDs, lemma/morphology, edition collation and translation remain NOT DONE; release BLOCKED.**
