# OLT-035B — All 27 RP2018 Greek New Testament books (continuous verse text)

**Date:** 2026-10-30. **State:** complete 27-book continuous **verse-text source collection** imported and byte-pinned; NOT a Greek word-ID, lemma, morphology or final critical edition approval. **Publication BLOCKED.**

## Actual completed source import

The chosen Robinson–Pierpont Byzantine Greek Textform **2018** is pinned to the ByzTxt repository [release v3.3.2](https://github.com/byztxt/byzantine-majority-text/tree/v3.3.2), at immutable Git commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`. This is an RP2018 textual edition delivered through a December 2024 Git tag, **not** a silent replacement with any RP2026 text.

The **27 ordinary NT books** were copied from the exact upstream `csv-unicode/ccat/no-variants/*.csv` files into `data/imported/nt/rp2018/`. All 27 copied files have exact original Git blob SHA-1 identity to upstream; combined source file size is about 1.74 MB. The Unicode CSV is a **derivative convenient conversion** of editor Robinson's authoritative `source/CCAT` data; it is not the editors' primary text file. No independent word-by-word collation against the original CCAT masters has yet been completed. Upstream states these files/text and code are public domain (LICENSE.txt).

For every imported main text file, `data/engine/olt_035b_rp2018_verse_inventory.json` records: canonical book order, original filename, OLT OSIS-like book ID, immutable upstream path/commit, exact Git blob SHA-1, byte length, source language `grc` and review status.

## Preserved but not silently merged ancillary verse texts

The RP2018 upstream tree has **29** source CSVs in the selected folder: **27** ordinary book CSVs and **two** separately supplied passage CSVs:

- `PA.csv`: John **7:53–8:11** (the *pericope adulterae*), retained at `data/imported/nt/rp2018/ancillary/PA.csv`.
- `ACT24.csv`: Acts **24:6–8** additional/alternative passage material, retained at `data/imported/nt/rp2018/ancillary/ACT24.csv`.

These files are separately byte-verified. They are **not automatically concatenated, substituted or silently overwriting** existing chapter/verse text from the main source. Their precise canonical placement, included/excluded portions and textual comparisons require independent study of Robinson's original apparatus and chosen owner editorial policy. An ancillary reading may overlap a book's verse reference; overlap is not proof of identical content.

## Strict source-versus-lexicon boundary

At this milestone OLT now has **the main 27-book RP2018 Greek verse-text corpus**, but the convenience CSVs contain `chapter`, `verse` and `text` only. The imported source records therefore explicitly report:

- `original_source_token_ids: null`
- `original_lemma_ids: null`
- `original_morphology: null`
- `owner_translation: null`
- `source_review: NOT_DONE`
- `publication_status: BLOCKED`

**No whitespace-based Greek word IDs are fabricated or published as genuine original text IDs.** In particular, this does **NOT** create a complete source-aligned NT Greek lexical ledger or OLT English NT translation. The OLT-034 core's per-word adapter must wait for a correctly sourced/verifiable Greek tokenization and morphological/lexical model.

The earlier OLT-035 source registry retains the historical 3 John-only initial import as that checkpoint's immutable record; the **current 27-book source inventory is the separate OLT-035B registry** and supersedes the earlier provisional statement that 26 books remain absent. Both are truthful for their recorded phases.

## Executable read-only verification

The Python standard-library module `olt_core/nt_corpus.py` implements `read_nt_inventory`, `read_nt_book`, `read_nt_ancillary` and `verify_nt_corpus`. It verifies exact Unicode CSV bytes against the pinned upstream blobs; parses CSV strictly, checks unique/monotonic verse references and authentic Greek script, and refuses to merge auxiliary readings into ordinary books. It produces research-only structured original-language verse objects, not translations.

```sh
python -m olt_core.nt_corpus --audit
python -m olt_core.nt_corpus --verse MAT Matt.1.1
python -m olt_core.nt_corpus --verse 3JO 3John.1.1
python -m olt_core.nt_corpus --ancillary PA
python -m olt_core.nt_corpus --ancillary ACT24
python -m unittest discover -s tests -p 'test_olt_035b_full_nt_verses.py' -v
```

The required unfiltered GitHub Actions `foundation` and new read-only `olt-035b.yml` run these checks in Ubuntu. Green checks certify only the assertions exercised, particularly file integrity and safe text staging—not correct etymology, Greek morphology, final editorial placement, translation quality or philological publication approval.

## Next independent work

1. Compare selected verse CSVs against the authoritative ByzTxt `source/CCAT` originals and clarify all special passage/variant placement cases without altering originals silently.
2. Build a source-provenance-locked, licensed Greek original word/lemma/morphology dataset with stable token IDs; do not invent permanent IDs by casual string splitting.
3. Join the Greek source correctly to the English master research lexicon and to independent language-specific lexical/grammar choices.
4. Review each contested name/title/wordplay and the Bible-wide OLT-033 underword rules on **real Greek source words**.
5. Retain independent linguistic reviews, full locale QA, proper reference and notes, accessible printing and explicit publication authorization as separate barriers.

**Owner doctrine and all existing Genesis 1:1/1:4 text/notes remain untouched. No Greek target translation or Hebrew/Greek word-family approval is inferred.**

## GitHub merge and independently executed test evidence (engineering only)

Merged through [OLT-035B PR #22](https://github.com/Northsw-spec/OLT/pull/22) at `274279701a52aae5c82727cd71420f65531a5789`. Post-merge GitHub Actions on this exact main SHA actually executed and passed:

- **Required foundation:** run `41127319379`, **290/290 Python tests PASS**, expected Bible release BLOCKED.
- **Greek full-source verifier:** run `41127319395`, **15/15 regression tests PASS**, verifying all **27** source-book UTF-8 CSV blobs, **7,953** original Greek verse records, and **2** separate supplemental Greek passage files.
- **OLT-035 original source verifier:** run `41127319396`, **16/16 tests PASS**, preserving all 39 imported original OT books, H/A tag distinction and previous 3 John source anchor.
- **OLT-034 multilingual core:** run `41127319453`, **20/20 + 5/5 tests PASS**.

These are executable source-record/byte-check claims, not final editorial or historical/text-critical approval and not a finished Greek lexicon or non-English translation.
