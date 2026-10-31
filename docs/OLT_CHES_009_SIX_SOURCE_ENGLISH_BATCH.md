# CHES-009 — Six-source private English pilot, backwards compatible

**Architecture:** OLT-SIMPLE-ENGINE-001. Extend the existing compact, source-verified and English-first CHES workflow. Do not restart the old original-Hebrew-to-English lexicon engine or require exhaustive manual word mappings.

## Genuine source discovery and exact PDF pins

The original index and two real source PDFs were independently checked in PR #60. All original text stays private, while exact SHA-256/byte-size/page-count and source measurements remain in the [technical source manifest](../data/engine/olt_ches_source_manifest.json).

| Chapter | Verses | Authentic Hebrew word tokens | Original green CHES PDF spans | PDF pages | Unassigned source green spans |
|---|---:|---:|---:|---:|---:|
| Genesis 4 | 26 | 341 | 418 | 3 | 0 |
| Exodus 2 | 25 | 340 | 432 | 3 | 0 |
| **New** | **51** | **681** | **850** | **6** | **0** |
| **All six chapters** | **153** | **2,030** | **2,518** | — | **0** |

Exact original Genesis 4 PDF SHA-256: f49997abce33ee2ca766e403dfce52e1ad08d6af99ff41707a69641cca0de274, 42,070 bytes.
Exact original Exodus 2 PDF SHA-256: 72ea917f884e1366c495054982f2e95f09781c1ddfafb91d2f85cc4ee4b5896b, 42,908 bytes.

A green typography span is NOT necessarily a Hebrew word or morpheme. **20 Genesis 4 and 19 Exodus 2 verses have unequal green-span vs source-word counts**; that does not imply 39 translation errors or completed Hebrew-English alignment. English gloss streams remain mechanical, UNREVIEWED and not approved OLT translation.

## Minimal extension without state migration

- The existing CHES-006 layout auditor accepts the additional **exact SHA-pinned originals** with real Hebrew OSHB source verse/token inventories.
- The existing CHES-007 private English source-gloss builder now accepts Genesis 4 and Exodus 2, carrying genuine original Hebrew token IDs and Hebrew wayyiqtol English simple-past obligations, but NEVER guessing which PDF span matches a Hebrew word.
- The existing CHES-008 private batch retains its original four-chapter default, same state filename and checkpoint schema. An explicit extended mode opt-in adds the two new chapters to an existing private checkpoint. Original four chapter output digests are preserved.

## Original private input filenames

Place the actual files inside your own authorized, private PDF directory with the following exact names: ches-gen1.pdf, ches-gen2.pdf, ches-gen3.pdf, ches-ex1.pdf, ches-gen4.pdf, ches-ex2.pdf.

To reproduce the original four-chapter mode:

~~~bash
python -m scripts.ches_008_private_batch \
  --pdf-directory /path/to/private-pdfs \
  --output-private-directory .olt-private/ches/batch \
  --confirm-machine-readable-use-permission
~~~

To opt into the six-chapter mode, reuse the private four-source state and resume without overwriting prior English drafts:

~~~bash
python -m scripts.ches_008_private_batch \
  --pdf-directory /path/to/private-pdfs \
  --output-private-directory .olt-private/ches/batch \
  --confirm-machine-readable-use-permission --extended --limit 6
~~~

Run that last command again and all six verified chapters should be skipped with their source and output SHA-256 integrity intact. A missing source or changed private draft is rejected per chapter without erasing previous successful files.

**Private outputs:** only within the ignored .olt-private/ directory, mode 0600, metadata-only stdout; copyrighted CHES source data, English source glosses and editorial notes must never be committed to public Git, emitted in CI logs or uploaded as artifacts. Source terms and original URLs stay in the technical provenance manifest.

## Verification and next stage

GitHub Actions uses the exact two new source PDF hashes, plus the original four, to verify actual original source verse inventories, private English gloss stream generation, and the old-four-to-new-six staged batch migration. The new tests reject false owner approval, false word alignment and unknown Hebrew source IDs. The pre-existing four-chapter tests must remain unchanged and passing.

**Next CHES-010:** gradually extend the source-pinned private English-first importer to additional genuine chapter layouts and measure remaining exceptional cases without building a new full lexicon engine. Full OT 929-chapter source import, Greek NT English, owner approval for the complete 66-book English Bible and Scripture publication are all NOT DONE / BLOCKED. Public README.md remains exactly zero bytes and original Git history is preserved.
