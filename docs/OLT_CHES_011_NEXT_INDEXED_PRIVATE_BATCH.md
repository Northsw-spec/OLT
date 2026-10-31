# CHES-011 — Second indexed source group, preserving earlier private output

**Binding design: OLT-SIMPLE-ENGINE-001.** Continue the small English-first CHES source-gloss pipeline with original Hebrew OSHB/WLC source verification; no giant new lexicon engine, unsupported per-word alignment or premature translation approval.

## New genuine original PDF evidence

The real original indexed PDF files were inspected in [CHES-011A PR #66](https://github.com/Northsw-spec/OLT/pull/66), then individually pinned to authentic SHA-256, byte length, page count, original verse/Hebrew word inventories and green PDF typography geometry in the [technical manifest](../data/engine/olt_ches_source_manifest.json).

| New original chapter | Printed verses | Authentic Hebrew word tokens | Private green PDF typography spans | Unassigned source spans |
|---|---:|---:|---:|---:|
| Genesis 7 | 24 | 332 | 406 | 0 |
| Genesis 8 | 22 | 309 | 419 | 0 |
| Exodus 5 | 23 | 318 | 459 | 0 |
| Exodus 6 | 30 | 404 | 482 | 0 |
| **New four** | **99** | **1,363** | **1,766** | **0** |
| **All fourteen** | **359** | **4,913** | **6,146** | **0** |

These are original source-layout engineering measurements, NOT validated CHES typography-span ↔ Hebrew original word/morpheme alignments or final grammatical OLT English verse counts. All original English CHES text stays private; original publisher attribution and rights remain in technical manifest.

## Backwards-compatible implementation

- The old four and six source modes remain unchanged. The ten-source mode continues to use the original first indexed group, with the same private checkpoint and filename conventions.
- The new group is stored in its own second technical source pin list. A single strict validator rejects duplicate original books/chapters across groups, untrusted source hashes, false public redistribution/translation approval, and incorrect original source URLs.
- The source layout verifier and compact CHES English pilot use the genuine pin registry to accept new chapters without inventing word-level Hebrew-to-PDF links.
- The source index-driven private cache has explicit next-group mode; the default still fetches/checks only the previously verified four index-added originals. The new mode requires four SHA-256 and geometry matches before saving any private PDF.
- The English chapter batch accepts an explicit fourteen-source mode. All ten prior private drafts are checked and skipped, four new authenticated source-backed working chapters are generated, then all fourteen can be verified/skipped on a repeat invocation.

## Private operator commands

The original OT source index and first ten original PDF files must already be in an authorized, ignored private working directory. PyMuPDF==1.26.5 is required.

~~~bash
python -m scripts.ches_010_private_source_cache \
  --source-index .olt-private/ches/ot-source-index.html \
  --output-private-directory .olt-private/ches/source-pdfs \
  --confirm-machine-readable-use-permission --next-group

python -m scripts.ches_008_private_batch \
  --pdf-directory .olt-private/ches/source-pdfs \
  --output-private-directory .olt-private/ches/english-batch \
  --confirm-machine-readable-use-permission --all-indexed
~~~

The original source PDFs are stored mode 0600 only within ignored .olt-private. A corrupt or edited source is never replaced silently. The English output is still mechanical private CHES interlinear gloss evidence with authentic original Hebrew word IDs, untranslated grammar candidates, owner approval FALSE, public publication BLOCKED and no public English Bible approval.

## CI and next step

GitHub Actions verifies synthetic negative source-rights and bad-byte cases, real original PDFs, private cache creation and skip, unchanged older four/six/ten modes, old ten-to-fourteen source English batch migration and final all-fourteen-skip. No original third-party CHES English source text is committed, printed or uploaded.

**Next CHES-012:** expand source-index-selected chapter batches with genuine original PDF QA, compact aggregate quality/geometry exception tracking and strictly evidence-based English lexical/tense correction review. The full 929 OT chapter archive, Greek NT English path, complete owner-approved 66-book OLT English Bible and Scripture publication remain unfinished/BLOCKED. Public README.md remains exactly zero bytes and Git history is preserved.
