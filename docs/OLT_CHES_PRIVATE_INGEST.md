# OLT-CHES-001 — Private machine-readable CHES source importer (English only)

**Scope:** import **CHES v2.0**, the green sublinear English text in Scripture4All's **Old Testament** PDF interlinears, with PDF source hash and original printed verse locator. CHES is **a third-party lexicographic rendering**, not an approved OLT Hebrew/Aramaic → English verse translation.

## Rights boundary

On 2026-10-31 the OLT owner stated that they have obtained permission to **use CHES text as machine-readable source data**. We record that as the owner's **reported private machine-readable use permission**, not as documentary proof that copyright holders granted public redistribution, changed PDFs, AI model training, commercial distribution, sublicense, or derivative publishing in **Amharic**.

The site's [general public terms](https://scripture4all.org/about/termsofuse/index.html) otherwise prohibit distributing modified / merged PDFs and restrict use. Specific separate permission can grant an exception; only its actual wording and rightsholders define that exception. CHES text copyright and PDF layout/textual layers may have separate rightsholders; do not treat machine-readable *internal use* permission as automatically covering every layer. Preserve attribution and source edition information.

**No source CHES word corpus, copied PDF or complete copyrighted interlinear is checked into the public OLT GitHub repository.** The importer requires a local chapter PDF already obtained by the operator, writes an export only to a path containing `.olt-private/`, and never prints CHES text to CI logs.

## Original source identity

- Original chapter index: <https://www.scripture4all.org/OnlineInterlinear/Hebrew_Index.htm>.
- Representative original **Genesis 1**: <https://www.scripture4all.org/OnlineInterlinear/OTpdf/gen1.pdf>.
- Green original line: **CHES v2.0** (not the neighboring Hebrew original, Hebrew transliteration, nor Authorized Version/KJV black column).
- CHES original word-level notations, articles and bound morpheme markers must be preserved exactly. Different source versions may vary in segmentation and copyright status.
- The OLT primary OT corpus remains the separately pinned **Open Scriptures Hebrew Bible/WLC** imported corpus. CHES is not permitted to silently replace original Hebrew or its source/morphology record.
- The OLT NT primary corpus remains **Robinson–Pierpont 2018 Greek**. This OT CHES importer does not provide a Greek New Testament translation.
- Initial design: PyMuPDF extracts **original green PDF text spans**, not OCR. It groups them using explicit printed chapter:verse markers and original PDF geometry, keeping page/x/y and the chapter PDF SHA-256. Wrong markers, unknown colors, missing green text, duplicate references and mismatched verse counts fail closed. The Authorized Version column is explicitly excluded.

## Reproducible private pilot (no public export)

Install PDF text extraction dependency locally:

```sh
python -m pip install PyMuPDF==1.26.5
```

Run from the OLT checkout against a chapter PDF that you are entitled to process:

```sh
python scripts/ches_pdf_probe.py --pdf /path/to/gen1.pdf
python scripts/ches_import.py \
  --pdf /path/to/gen1.pdf --book Gen --chapter 1 \
  --expected-verses 31 --audit
```

Only after verifying original verse/green-text grouping, privately save an extract:

```sh
python scripts/ches_import.py \
  --pdf /path/to/gen1.pdf --book Gen --chapter 1 \
  --expected-verses 31 \
  --output-private .olt-private/ches/Gen.1.json
```

Outputs are restricted to `.olt-private`, excluded by Git and assigned restrictive local file permissions. **Never** attach, publish, make an Actions artifact, upload to public GitHub, or forward the entire CHES text without a separately established permission covering that act.

GitHub Actions runs 7 negative/control tests plus a full original-Genesis-1 PDF integration test in an ephemeral runner, with source data and full green-text output omitted from logs and Git history. GitHub's test PASS means only that the source parser operates according to its engineering assumptions.

## What still must be established before whole-OT import

1. Inspect actual original green text spans and verse-label geometry in Genesis 1, including wrapped verses and page breaks; confirm every verse is uniquely assigned. Any exact parser mismatch is a blocker, never permission to guess.
2. Determine the **entire OT index URL inventory** (39 books), verify chapter coverage and original per-book chapter/verse counts. Do not guess file names or scrape unrelated domains.
3. Import one chapter at a time privately, store PDF source digests + reader checks, and keep parse failures separate. Limit fetch volume to polite request rates with retries and verification.
4. Establish a separately verified correspondence between each original CHES sublinear token span and OSHB original Hebrew or Aramaic word/morpheme. Position-only guessed alignment is explicitly forbidden.
5. Preserve owner English editorial differences: `bara` → `shaped`, `asah` → `make`, `raqia` → `firmament`, Hebrew **verified wayyiqtol** → English **simple past**. The CHES's own forms and translation philosophy do not override owner OLT rules.
6. Build a generator that uses this third-party **reference** plus original tokens to produce an explicitly `UNREVIEWED_ENGLISH_DRAFT`, with provenance and uncertainty flags. GitHub CI cannot certify semantics.
7. Only when the **complete 66-book English** translation has been personally reviewed and approved by the owner may development begin for other target languages.

## Future Amharic: potential acceleration, not an English-pivot guarantee

CHES can give original Hebrew phrase-to-English gloss clues, reusable semantic candidates, source alignment targets, and established contrastive examples for later **Hebrew/Aramaic → Amharic** translation. This may save dictionary research. It does **not** remove Amharic language-specific work (verb morphology, word order, syntax, honorifics, orthography, names, idioms). The correct future pipeline remains **original Hebrew/Aramaic word/context + disambiguated sense evidence (including CHES) → approved Amharic wording**, not blind word substitution from English.

**Legal and project stop gates:** The original CHES permission's precise terms must cover any intended downstream derivative use and later distribution. Independent English source licensing for the NT must be addressed separately. No Amharic or other non-English engine or translation work is currently authorized; the single-target English-first policy remains in force.

**Current state at introduction:** PDF importer prototype for private source material; **whole GT not yet ingested**, original CHES-to-OSHB token correspondence **not verified**, independent English translation **not approved**, English Bible publication **BLOCKED**.
