# CHES-007 — Lightweight private multi-chapter English gloss/draft generation

**Current engine direction:** OLT-SIMPLE-ENGINE-001. Continue the small CHES-informed English-first engine; do not rebuild the old thousands-of-hours full lexicon/semantic engine or require manual alignment of every word.

## Delivered scope

The existing Genesis 1 CHES-004 English pilot stays unchanged. The new module **scripts/ches_007_multichapter_english.py** extends its private, original-source-checked verse workflow to **Genesis 2, Genesis 3 and Exodus 1**, using the four exact source-PDF pins established in CHES-006.

| Chapter | Verses | Authentic OSHB Hebrew tokens | Private green PDF typography spans |
|---|---:|---:|---:|
| Genesis 2 | 25 | 328 | 377 |
| Genesis 3 | 24 | 347 | 415 |
| Exodus 1 | 22 | 240 | 350 |
| **New CHES-007 scope** | **71** | **915** | **1,142** |
| Genesis 1, existing CHES-004 | 31 | 434 | 526 |
| **Four-chapter pilot total** | **102** | **1,349** | **1,668** |

These are PRIVATE **mechanically assembled English interlinear gloss streams** from the licensed source, NOT complete literal/grammatical OLT translations or owner-approved verses. Green PDF text spans are not inherently English words or Hebrew morphemes; counts do not prove translation quality.

The default byte-level entry point reads the real original PDF, validates the exact SHA-256, byte size, verse markers, typography counts and authentic original Hebrew word IDs against the [pinned manifest](../data/engine/olt_ches_source_manifest.json), then assembles the private English source text in verse order.

Each private verse contains authentic original-source token IDs; a separate English CHES gloss stream and current English working text; the original-word-tagged **wayyiqtol English simple-past requirements**; limited owner lexical choice *candidates* such as bara → shaped, asah → make and raqia → firmament; and unequivocal **UNREVIEWED**, unaligned, untranslated-grammar and **publication BLOCKED** flags. The program does not guess CHES word correspondence or silently change tenses/glosses.

## Private running instructions

Use only with the owner's reported source-use permission and the pinned PDF parser dependency.

~~~bash
python -m pip install PyMuPDF==1.26.5

# Source counts/status only: original Genesis 2 PDF, no copyrighted excerpts
python -m scripts.ches_007_multichapter_english \
  --book Gen --chapter 2 --pdf /path/to/gen2.pdf \
  --confirm-machine-readable-use-permission --audit

# Create an actual private English working draft under the ignored folder
python -m scripts.ches_007_multichapter_english \
  --book Gen --chapter 3 --pdf /path/to/gen3.pdf \
  --confirm-machine-readable-use-permission \
  --output-private .olt-private/ches/gen3-english-working.json

python -m scripts.ches_007_multichapter_english \
  --book Exod --chapter 1 --pdf /path/to/exo1.pdf \
  --confirm-machine-readable-use-permission \
  --output-private .olt-private/ches/exo1-english-working.json
~~~

Only the local Git-ignored **.olt-private/** tree may receive private source text/drafts (0600 file permissions). No CHES original prose, private editable English verse or copyrighted text is emitted in CI logs, stdout or public artifacts. All other output is counts/status only.

### Optional, private and unapproved editor change

Create **.olt-private/ches/gen2-edits.json**, replacing the example PDF hash with the exact original Genesis 2 SHA-256 from the technical source manifest.

~~~json
{
  "original_source_pdf_sha256": "<EXACT_PINNED_GENESIS_2_PDF_SHA256>",
  "chapter_reference": "Gen.2",
  "unapproved_verse_edits": [
    {
      "reference": "Gen.2.2",
      "english_text_unapproved": "Example privately edited English verse, unapproved.",
      "editor_note_private": "Inspected original Hebrew verse and private interlinear; grammatical review remains pending.",
      "approved": false
    }
  ]
}
~~~

~~~bash
python -m scripts.ches_007_multichapter_english \
  --book Gen --chapter 2 --pdf /path/to/gen2.pdf \
  --confirm-machine-readable-use-permission \
  --editorial-private .olt-private/ches/gen2-edits.json \
  --output-private .olt-private/ches/gen2-english-edited.json
~~~

The original CHES source gloss remains separate from the editor's proposed English wording. A wrong original hash, false approval, duplicate/out-of-chapter edit, empty evidence note or non-private input/output path fails closed. These are editor-supplied words, NOT automatic approval of a verse, its grammar, Hebrew lexical correctness, further derivative rights or the Bible.

## Continuous integration and next scope

The dedicated CHES GitHub Actions workflow uses **synthetic invented green English source fragments** for unit and negative tests with genuine pinned Hebrew OSHB IDs, and executes the **real three additional original PDFs in runner memory** for a metadata-only audit. The pre-existing Genesis 1 pipeline remains separately tested.

**Next CHES-008:** build a small, resumable four-chapter PRIVATE English draft batch workflow, bounded error reporting and safe persistent outputs. Expand incrementally from exact authenticated originals, measure omissions and only review exceptions rather than starting the old full lexical engine. The Greek NT remains a separate source-checked English design problem. Full OT PDF import is NOT done. The English Bible is NOT finished and owner approval/publication remain BLOCKED.

The public README remains exactly zero bytes. Preserve original technical source identity and rights information in the machine-readable provenance manifest, and retain the full Git history.
