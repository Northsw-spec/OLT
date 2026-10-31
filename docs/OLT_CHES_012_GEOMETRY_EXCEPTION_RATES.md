# CHES-012 — Source-pinned geometry exception and QA rates for the private fourteen-chapter OT pilot

**Engine direction:** OLT-SIMPLE-ENGINE-001, the compact CHES-source-first English engine with genuine original Hebrew/Aramaic OSHB source evidence. No large replacement lexicon, automatic PDF-to-Hebrew word matching or publication approval is introduced.

## Purpose and precise interpretation

Before expanding from fourteen privately source-verified Old Testament PDF chapters, quantify the existing **structural** exception and geometry warning rates. The new script **scripts/ches_012_exception_metrics.py** opens the exact fourteen SHA-256-pinned original PDF files from a private directory, calls the existing original-language-aware PDF geometry verifier and compares **every chapter** against the technical source provenance manifest. Mismatched source hash, bytes, pages, original verse count, original Hebrew token count, extracted green PDF source typography spans, unequal-span warning counts, page-crossing warnings or min/max source spans is fatal.

A PDF green typography span is **not** a proven one-to-one Hebrew word or morpheme. An unequal number of green source spans and Hebrew words is an **observation about text/PDF segmentation**, not a mistranslation. A page-crossing verse is a geometry review candidate; neither of these observations claims any particular English word, grammar or Hebrew meaning is wrong.

## Source-baseline measurements

| Original-source engineering measurement | Fourteen-chapter baseline |
|---|---:|
| Authentic source chapter PDFs | 14 |
| Genuine Hebrew original verse references | 359 |
| Genuine Hebrew OSHB source word tokens | 4,913 |
| Original green interlinear PDF typography spans | 6,146 |
| Verses with unequal CHES-span vs Hebrew-token counts (not translation errors) | 286 |
| Verses with green fragments across multiple PDF pages | 11 |
| Original green spans lost/unassigned after verse reconstruction | 0 |
| Chapters needing a PDF page-boundary/ink-loss review | 9 |

The deterministic **unequal-span versus source-word count observation rate** is 286/359, rounded to **79.67%**. This high value reflects typography segmentation and the absence of verified original word-to-English span alignment, **not a 79.67% translation error rate**. The **page-crossing verse rate** is 11/359, or **3.06%**. Exactly **9 of the fourteen** original chapter PDF layouts contain at least one page-crossing verse. Both percentages are computed as integer basis points to avoid floating-point changes. Zero lost source green spans is a parsing/completeness assertion, not evidence of completed English translation quality.

The exact source metadata and rights flags are maintained in the [technical source manifest](../data/engine/olt_ches_source_manifest.json). Real source PDF bytes remain private; no original verses, CHES glosses, intermediate English text or editable notes are committed or emitted in CI logs.

## Run locally on the exact private original files

Use the already established private PDF source cache for all fourteen chapter filenames, with permission for the original machine-readable source use.

~~~bash
python -m pip install PyMuPDF==1.26.5

python -m scripts.ches_012_exception_metrics \
  --pdf-directory .olt-private/ches/source-pdfs \
  --confirm-machine-readable-use-permission
~~~

The command prints **allowlisted metadata only**: source IDs, source PDF SHA-256 values, pages, genuine source Hebrew token counts, green PDF span/printed verse counts, per-chapter warning tallies, percentage rates expressed in **basis points**, and explicit FALSE translation/approval flags. It never prints copyrighted CHES English passage text.

The underlying source files are still subject to exact PDF SHA-256 verification, real printed verse anchor checks, authentic Hebrew OSHB token integrity and recorded immutable source geometry. The code rejects malformed, missing, duplicate, falsely approved, unpinned or geometrically changed chapters instead of silently introducing new baselines.

## CI and interpretation boundaries

GitHub Actions runs hostile/synthetic **metadata-only** regression tests (false approval/word links, shifted warning counts, digest/page/word/verse changes, duplicate source IDs and possible source-text injection), followed by independent rechecking of **all fourteen genuine original PDF files in ephemeral runner memory**. It prints no licensed English source content. This verifies software/data integrity; it does NOT certify that the CHES English language is grammatical OLT English, that wayyiqtol simple-past rules have all been applied, or that the owner has approved the translation.

**Next CHES-013:** use this verified numerical quality baseline to prioritize bounded new source-index-selected OT PDF batches and exception-based English grammar/lexical reviews, without mandatory manual alignment of every original PDF source span. The complete 929-chapter OT archive is NOT imported, Greek NT English production is separate, the full 66-book English Bible is NOT approved, and Scripture publication remains **BLOCKED**.

Keep public README.md exactly zero bytes, preserve Git history, the original provider identity and exact permission metadata in the technical manifest.
