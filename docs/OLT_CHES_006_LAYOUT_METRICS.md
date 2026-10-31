# CHES-006 — Original-source interlinear layout and exception measurements

**Owner-locked strategy:** maintain the *small* privately licensed CHES → source-checked English OLT draft pipeline. Do not reimplement a full Hebrew-English dictionary or conduct exhaustive word-by-word manual alignment as a routine engineering requirement.

## Purpose and source limits

The new Python module **scripts/ches_006_layout_metrics.py** performs an entirely metadata-only engineering audit of four carefully chosen real Old Testament chapter layouts:

- Genesis 1: existing exact original PDF SHA-256 and size source pin; 31 verses and 434 authentic Hebrew word tokens.
- Genesis 2: existing exact original PDF pin; 25 verses and 328 authentic Hebrew word tokens.
- Genesis 3: additional genuine original PDF layout **now pinned exactly** to the SHA-256, byte count, 3 pages, 24 verses and 415 green CHES fragments observed in the dedicated real-source GitHub Actions run.
- Exodus 1: separate original-source filename group/book, **now pinned exactly** to the true source PDF index link (filename exo1.pdf), SHA-256, byte count, 3 pages, 22 verses and 350 green CHES fragments. An earlier guessed filename was an HTML error page and was explicitly rejected.

Every chapter's PDF is fetched directly from the approved original host into ephemeral GitHub Actions runner storage, parsed in memory through the existing CHES green-text/verse-marker extractor, checked against genuine hash-checked OSHB/WLC original word IDs and then discarded. Source text is never copied into the repository or emitted in workflow logs. No OCR or KJV fallback.

## What the new numeric diagnostics mean

The safe summary records: original PDF SHA-256/size/pages, verse-marker and authentic Hebrew-source inventories, green fragment counts, minimum/maximum green fragments in a verse, number of verses with different PDF-span and original-Hebrew-token counts, green fragments spanning PDF page boundaries, raw original green fragments preceding the first printed verse and any unassigned original green fragments.

**A difference between PDF text-span counts and Hebrew word-token counts is NOT a Hebrew-English translation error or proof of a missing word**. PDF text spans are typography, and original Hebrew words may have multiple attached morphemes. The module never turns count equality into a verified word/morpheme alignment.

The module rejects wrong PDF hashes once pinned, changed permissions, fake approval flags, missing/reordered verse markers, mismatched original word IDs and unexplained raw green text loss. Any green text before the first printed verse is **reported as a warning**, not silently made into a fake verse.

The difference between **engineering pass** and **linguistic approval** is essential. Even if all four chapter layouts pass, all CHES-to-OSHB word links remain UNVERIFIED, English-only owner review remains incomplete and publication remains BLOCKED.


## Genuine observed four-chapter geometry measurements

| Original chapter | Printed verses | OSHB Hebrew word tokens | Green PDF spans | Verses with different span/word counts* | Verses crossing PDF pages |
|---|---:|---:|---:|---:|---:|
| Genesis 1 | 31 | 434 | 526 | 24 | 1 |
| Genesis 2 | 25 | 328 | 377 | 18 | 1 |
| Genesis 3 | 24 | 347 | 415 | 19 | 2 |
| Exodus 1 | 22 | 240 | 350 | 16 | 0 |
| **Total** | **102** | **1,349** | **1,668** | **77** | **4** |

*These 77 verse counts indicate **different PDF typography-span versus source-word segmentation**, not 77 mistranslations and not 77 independently proven alignment errors. In all four actual PDFs, the raw green span total matches all verse-assigned green spans exactly: **zero unassigned green text fragments**. This does not establish correct per-word or per-verse semantic translation.

**Exact additional original PDF identity (metadata only):**

- Genesis 3: SHA-256 71d6773374681b6855f801f9fb5254f5891c2d7c0705c984cfede112dde6450b, **42,678 bytes**, 3 PDF pages, 24 printed verses, 415 original green source spans, 347 original Hebrew tokens.
- Exodus 1: SHA-256 fab98329167dfcd2041dc99470abe366fb6583325679de888a33f880c3860d28, **36,499 bytes**, 3 PDF pages, 22 printed verses, 350 original green source spans, 240 original Hebrew tokens.

## Reproducible commands

The chapter audit requires the same pinned PyMuPDF dependency as the existing pipeline:

~~~bash
python -m pip install PyMuPDF==1.26.5

# Exact source-pinned chapter audits; stdout contains numbers/status only
python -m scripts.ches_006_layout_metrics --book Gen --chapter 1 \
  --pdf /path/to/gen1.pdf --confirm-machine-readable-use-permission
python -m scripts.ches_006_layout_metrics --book Gen --chapter 2 \
  --pdf /path/to/gen2.pdf --confirm-machine-readable-use-permission

# Exact source-pinned extra-chapter geometry audits
python -m scripts.ches_006_layout_metrics --book Gen --chapter 3 \
  --pdf /path/to/gen3.pdf --confirm-machine-readable-use-permission
python -m scripts.ches_006_layout_metrics --book Exod --chapter 1 \
  --pdf /path/to/exo1.pdf --confirm-machine-readable-use-permission
~~~

Synthetic negative tests use fake English source fragments and the authentic pinned OSHB corpus:

~~~bash
python -m unittest discover -s tests -p 'test_ches_006_layout_metrics.py' -v
~~~

All four real PDFs now have **exact SHA-256, byte size and page-count pins** in the [technical source manifest](../data/engine/olt_ches_source_manifest.json), and the dedicated workflow rejects any unpinned file. Preserve licensed-source copyright/terms in the machine-readable manifest, not prose documentation.

## Next work

Use the **four exact source-pinned** measurements to prioritize very small, demonstrated layout-specific diagnostics or conservative exceptions. Cross-page verse fragments deserve engineering review but do not automatically mean an imported word was lost. The full 929-chapter original OT data archive has not been imported or certified, Greek NT English requires its own original-language source path, and owner approval of the complete 66-book English Bible remains NOT DONE. Keep the public README exactly zero bytes, the English-only gate and complete GitHub history unchanged.
