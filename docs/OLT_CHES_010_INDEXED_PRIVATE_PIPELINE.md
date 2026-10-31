# CHES-010 — Private, index-driven and hash-pinned ten-chapter English pilot

**Binding project direction:** OLT-SIMPLE-ENGINE-001. Extend the existing small CHES-informed, original Hebrew/Aramaic-checked English drafting engine; do NOT rebuild a huge independent lexicon or presume one-to-one original Hebrew ↔ English source correspondence.

## Genuine original source additions

The existing **929-chapter/39-prefix source index** is parsed using strict canonical index rules. The first bounded discovery stage ([PR #63](https://github.com/Northsw-spec/OLT/pull/63)) automatically selected and inspected four **actual original PDF chapters** in temporary GitHub Actions memory. The exact source SHA-256/size/page count and original verse/word and PDF span measurements are now pinned in the [technical original-source manifest](../data/engine/olt_ches_source_manifest.json).

| New original chapter | Printed verses | Authentic Hebrew source tokens | Private green PDF typography spans | PDF pages | Unassigned green spans |
|---|---:|---:|---:|---:|---:|
| Genesis 5 | 32 | 365 | 437 | 3 | 0 |
| Genesis 6 | 22 | 305 | 381 | 3 | 0 |
| Exodus 3 | 22 | 395 | 477 | 3 | 0 |
| Exodus 4 | 31 | 455 | 567 | 4 | 0 |
| **New** | **107** | **1,520** | **1,862** | **13** | **0** |
| **Ten-source pilot total** | **260** | **3,550** | **4,380** | — | **0** |

A green PDF typography span is NOT necessarily one authentic Hebrew word/morpheme. Unequal counts alone are not translation errors and do not prove any word-level English correspondence. All English gloss/grammar completion and public redistribution remain UNVERIFIED/BLOCKED.

Original real source PDF hashes:

- Genesis 5: SHA-256 d153a73d04d08044655247a842fcb73b3d05c11e831ff0f63d42ff3a1f395e49, 36,710 bytes.
- Genesis 6: SHA-256 d186d354e18e21dc1eb32fc4b8118d507288fe15b66ee89890f320e2d6b280e7, 39,521 bytes.
- Exodus 3: SHA-256 5d1bc0765897c6f8a90d1551b4240697d16c5f23a4544fb7b5b1fd6f736ddbbc, 45,841 bytes.
- Exodus 4: SHA-256 9046aae88964a9436180b1830abc47271907da76286df660dd23ca262cb2d2ca, 56,384 bytes.

## Reusable engineering architecture

The original source manifest contains a small additional list of authenticated, hash-pinned source records instead of requiring separate hardcoded Python changes for each source chapter. The strict registry validator (scripts/ches_010_pin_registry.py) enforces bounded record counts, original host/URL and PDF hashes, private filenames, source verse/word counts and FALSE/BLOCKED original rights and word alignment claims.

The private source cache (scripts/ches_010_private_source_cache.py) reads the authentic chapter index, fetches exactly the selected original PDFs over TLS-validated HTTPS and checks all their SHA-256 and original verse/geometry metrics BEFORE saving anything. It writes only under an ignored .olt-private/ directory, using mode 0600. It refuses to overwrite changed existing originals.

The CHES-006 original geometry validator and CHES-007 private mechanical English gloss stream generator now learn the new chapter scope from the source pin registry. The CHES-008 batch keeps the **original four-chapter default**, retains the existing six-chapter --extended option, and adds an explicit **--indexed** option for the ten authenticated chapters.

The source-first English output still has authentic Hebrew source token IDs and pending source wayyiqtol → English simple-past requirements. It does not automatically replace a PDF gloss when a word-level link remains unverified. Owner approval, grammar completion, word/morpheme alignment and publication remain FALSE/BLOCKED.

## Reproducible local usage

First put the original six verified PDFs in a private source directory with their established filenames (ches-gen1.pdf, ches-gen2.pdf, ches-gen3.pdf, ches-ex1.pdf, ches-gen4.pdf, ches-ex2.pdf). Obtain the original Hebrew chapter index at the URL recorded in the [technical source manifest](../data/engine/olt_ches_source_manifest.json) and store it privately at .olt-private/ches/ot-source-index.html.

The following commands require the owner's reported machine-readable source-use permission:

~~~bash
python -m pip install PyMuPDF==1.26.5

# Fetch and SHA-check the new four original PDFs into the PRIVATE source directory:
python -m scripts.ches_010_private_source_cache \
  --source-index .olt-private/ches/ot-source-index.html \
  --output-private-directory .olt-private/ches/source-pdfs \
  --confirm-machine-readable-use-permission

# Resume the source-checked private English draft batch to all ten chapters:
python -m scripts.ches_008_private_batch \
  --pdf-directory .olt-private/ches/source-pdfs \
  --output-private-directory .olt-private/ches/english-batch \
  --confirm-machine-readable-use-permission --indexed
~~~

Re-running the cache checks all actual original PDF hashes and skips unchanged files. Re-running the English batch validates all original sources, private English output SHA-256 checksums and canonical original Hebrew token IDs; unchanged draft outputs are skipped. A changed English draft or source is not overwritten.

The original source PDFs and copyright-licensed CHES English passages are neither committed to public Git nor emitted in GitHub Actions logs or artifacts. Only counts, hashes and status appear in CI output.

## Next

**CHES-011:** expand the pinned index-selection policy to more carefully bounded original source groups while recording per-chapter geometry, retry and exception rates. No complete 929 chapter OT import, Greek NT English engine, or owner-approved complete 66-book English Bible has yet been delivered. The published Bible remains BLOCKED.

Keep README.md exactly zero bytes, full Git history and accurate technical original-source attribution and rights evidence.
