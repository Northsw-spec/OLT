# CHES-006 — Original-source interlinear layout and exception measurements

**Owner-locked strategy:** maintain the *small* privately licensed CHES → source-checked English OLT draft pipeline. Do not reimplement a full Hebrew-English dictionary or conduct exhaustive word-by-word manual alignment as a routine engineering requirement.

## Purpose and source limits

The new Python module **scripts/ches_006_layout_metrics.py** performs an entirely metadata-only engineering audit of four carefully chosen real Old Testament chapter layouts:

- Genesis 1: existing exact original PDF SHA-256 and size source pin; 31 verses and 434 authentic Hebrew word tokens.
- Genesis 2: existing exact original PDF pin; 25 verses and 328 authentic Hebrew word tokens.
- Genesis 3: additional genuine layout, **discovery only** until real source hash, byte count, pages and spans are measured and committed as source pins.
- Exodus 1: separate source filename group/book, **discovery only** until exact source evidence is measured and pinned.

Every chapter's PDF is fetched directly from the approved original host into ephemeral GitHub Actions runner storage, parsed in memory through the existing CHES green-text/verse-marker extractor, checked against genuine hash-checked OSHB/WLC original word IDs and then discarded. Source text is never copied into the repository or emitted in workflow logs. No OCR or KJV fallback.

## What the new numeric diagnostics mean

The safe summary records: original PDF SHA-256/size/pages, verse-marker and authentic Hebrew-source inventories, green fragment counts, minimum/maximum green fragments in a verse, number of verses with different PDF-span and original-Hebrew-token counts, green fragments spanning PDF page boundaries, raw original green fragments preceding the first printed verse and any unassigned original green fragments.

**A difference between PDF text-span counts and Hebrew word-token counts is NOT a Hebrew-English translation error or proof of a missing word**. PDF text spans are typography, and original Hebrew words may have multiple attached morphemes. The module never turns count equality into a verified word/morpheme alignment.

The module rejects wrong PDF hashes once pinned, changed permissions, fake approval flags, missing/reordered verse markers, mismatched original word IDs and unexplained raw green text loss. Any green text before the first printed verse is **reported as a warning**, not silently made into a fake verse.

The difference between **engineering pass** and **linguistic approval** is essential. Even if all four chapter layouts pass, all CHES-to-OSHB word links remain UNVERIFIED, English-only owner review remains incomplete and publication remains BLOCKED.

## Reproducible commands

The chapter audit requires the same pinned PyMuPDF dependency as the existing pipeline:

~~~bash
python -m pip install PyMuPDF==1.26.5

# Exact source-pinned chapter audits; stdout contains numbers/status only
python -m scripts.ches_006_layout_metrics --book Gen --chapter 1 \
  --pdf /path/to/gen1.pdf --confirm-machine-readable-use-permission
python -m scripts.ches_006_layout_metrics --book Gen --chapter 2 \
  --pdf /path/to/gen2.pdf --confirm-machine-readable-use-permission

# Preliminary extra-chapter discovery (NOT source-pinned or English-engine-ready)
python -m scripts.ches_006_layout_metrics --book Gen --chapter 3 \
  --pdf /path/to/gen3.pdf --confirm-machine-readable-use-permission \
  --discovery-only-unpinned
python -m scripts.ches_006_layout_metrics --book Exod --chapter 1 \
  --pdf /path/to/ex1.pdf --confirm-machine-readable-use-permission \
  --discovery-only-unpinned
~~~

Synthetic negative tests use fake English source fragments and the authentic pinned OSHB corpus:

~~~bash
python -m unittest discover -s tests -p 'test_ches_006_layout_metrics.py' -v
~~~

After the additional original PDFs have been independently observed in GitHub Actions, **pin exact source hashes/metadata and remove discovery mode from the dedicated workflow**. Only then label each added chapter as an exact, repeatable source geometry check. Preserve licensed-source copyright/terms in the machine-readable technical provenance manifest, not prose documentation.

## Next work

Use the observed failure/warning rates to choose a *few* layout-specific adjustments or conservative exceptions with bounded tests. The full 929-chapter original OT data archive has not been imported or certified, Greek NT English requires its own original-language source path, and owner approval of the complete 66-book English Bible remains NOT DONE. Keep the public README exactly zero bytes, the English-only gate and complete GitHub history unchanged.
