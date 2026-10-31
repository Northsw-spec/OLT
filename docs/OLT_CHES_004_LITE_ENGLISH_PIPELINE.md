# CHES-004 — Lightweight private CHES → English Genesis 1 draft pilot

**Status:** engineering proof of a **working private CHES-backed interlinear gloss stream** and optional explicit verse-level editorial edits. This implements the small architecture in [OLT-SIMPLE-ENGINE-001](OLT_SIMPLE_ENGINE_001.md), not a from-scratch Hebrew-English lexicon.

## What the pipeline actually does

1. Parses the licensed **original Genesis chapter 1 PDF locally** using the original green-text and printed-verse-marker extractor, **without OCR** or copying the KJV column.
2. Requires exact original PDF SHA-256, size and pages, 31 printed source verse references and 526 original green PDF spans. Cross-checks the 31 authentic OSHB/WLC Hebrew verse identities and 434 pinned source word IDs.
3. Produces a **private English gloss stream per verse**, using original green fragments in PDF order. This is a mechanical interlinear reading, **not** verified English grammar or a final OLT translation. Copyrighted text stays under the private directory.
4. Detects all 50 source-tagged Hebrew **wayyiqtol** forms and records original-token-ID-keyed requirements for **English simple past**. It does not silently replace unaligned CHES English fragments. A tiny rule layer also records owner lexical review candidates for authentic source lemma annotations (bara, asah, raqia), **not applied** without verified lexical mapping.
5. Optionally accepts **explicit private verse-level editorial English edits**, producing an adjusted English-only working draft without the old expensive translation engine. No English owner signoff or original-language grammatical approval is inferred.
6. Prints **counts and statuses only**; no licensed source words, private draft, editorial notes or original PDFs go to public Git, CI logs or CI artifacts.

## Run locally (requires reported source-use permission)

Install the same pinned PDF text extractor dependency used by the existing import scripts:

~~~bash
python -m pip install PyMuPDF==1.26.5

# Counts-only audit, does NOT print any copyrighted CHES text:
python -m scripts.ches_lite_english \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission --audit

# Real private English gloss/draft output:
python -m scripts.ches_lite_english \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission \
  --output-private .olt-private/ches/genesis_1_lite_english.json
~~~

The output file is restricted to the owner (0600). The fields **ches_raw_gloss_stream_private_unapproved** and **english_text_private_unapproved** initially contain the same mechanical CHES English gloss stream per verse. It is NOT a grammatically reconstructed OLT verse and not safe for public publication.

## Optional private verse-level editorial edits

Use the actual pinned original Genesis PDF SHA-256 from the [source manifest](../data/engine/olt_ches_source_manifest.json); all editorial input/output must remain under the private directory.

~~~json
{
  "original_source_pdf_sha256": "<PINNED_PDF_SHA256>",
  "chapter_reference": "Gen.1",
  "unapproved_verse_edits": [
    {
      "reference": "Gen.1.1",
      "english_text_unapproved": "Example owner-edited English verse, still unapproved.",
      "editor_note_private": "Reviewed this verse against the original Hebrew and English source.",
      "approved": false
    }
  ]
}
~~~

~~~bash
python -m scripts.ches_lite_english \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission \
  --editorial-private .olt-private/ches/verse_edits.json \
  --output-private .olt-private/ches/genesis_1_lite_english_edited.json
~~~

This is an **unapproved verse-level edit**, not a verified CHES↔OSHB word mapping. The source-tagged wayyiqtol English simple-past requirement remains pending until a real English source fragment can be safely located and reviewed. Do not interpret the edited file as automatically verified English.

## CI

- Unit test: python -m unittest discover -s tests -p 'test_ches_004_lite_pipeline.py' -v
- Public unit tests use **invented green English text** but the **genuine pinned OSHB Hebrew source**, including all 434 original tokens and 50 source-tagged wayyiqtol forms.
- Dedicated CHES GitHub Actions executes the real PDF importer and private draft builder in memory with **metadata-only output** and no licensed source-text artifact.

## Nonclaims and next work

This milestone does NOT establish one-to-one or many-to-one word/morpheme equivalence from mere PDF spans, does NOT automate English tense inflection for unknown source fragments, does NOT import all 929 OT chapters or translate the Greek NT, and does NOT establish rights to publish adapted copyrighted CHES text. English-only and owner signoff/publication-BLOCKED rules remain binding.

Next: develop the smallest justifiable original-Hebrew-anchored English tense/lexical transforms for selected verified spans, avoiding large human alignment queues; test a representative *additional* original PDF layout before scaling. The pre-existing 31 OLT research verse proposals are separate and not misrepresented as generated by this new CHES-backed pipeline.

Keep README.md exactly zero bytes and source-provider identifiers in the technical source manifest, not narrative documentation.
