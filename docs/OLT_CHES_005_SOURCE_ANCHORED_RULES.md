# CHES-005 — Lightweight English rule exceptions and Genesis 2 layout QA

**Scope:** Continue the small private CHES-to-English draft engine. Do not rebuild the old extensive lexicon or institute compulsory manual review of hundreds of thousands of word links.

## Controlled English exception previews

The new script **scripts/ches_005_safe_exceptions.py** extends the actual private Genesis 1 English CHES gloss stream from CHES-004. It applies a *bounded explicit operator-provided exception preview* only when all source checks agree:

- Pin the original Genesis 1 PDF SHA-256, 31 printed verse references, 526 genuine green CHES text fragments and 434 authentic OSHB Hebrew word tokens.
- Check a specific original Hebrew **word source ID, lemma annotation, morphology and verse reference** against the authentic pinned text, not a guessed lexical link.
- Require one *explicit original PDF green span ordinal within that verse*, including its unchanged private English source text. Only that source span is replaced in the working draft; other identical English words are untouched.
- Require an explicit assertion that the operator inspected the original Hebrew PDF and an evidence note, stored only privately. This is **not independent linguistic verification**.
- For source-tagged wayyiqtol, allow only the specific existing OLT Genesis 1 research simple-past fragment linked to **that exact Hebrew verb**, never a different past verb or an English perfect tense.
- For lexical alternatives, accept only OLT's small owner-choice candidates: **bara → shaped**, **asah → make**, **raqia → firmament**, and reject lexical-only replacements that would bypass a wayyiqtol tense requirement.
- Reject stale or nonexistent source IDs, altered morphology/lemma, wrong chapter/verse, changed original PDF English fragment, overlapping edits, unsupported words, invalid cardinality, attempts to claim approval or publication.

The result is still an **unapproved private English working draft**. Original PDF word alignment and linguistic equivalence are NOT independently certified merely because the operator identifies an apparent correspondence. **Zero exception rules** is a valid safe default that leaves every English gloss stream unchanged.

## Local usage

All private source text and editorial notes stay under the ignored **.olt-private/** directory and are never emitted to CI stdout.

~~~bash
python -m pip install PyMuPDF==1.26.5

# Metadata-only source and English-rule audit
python -m scripts.ches_005_safe_exceptions \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission --audit

# Private source-backed working English gloss/draft output
python -m scripts.ches_005_safe_exceptions \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission \
  --output-private .olt-private/ches/gen1-english-exceptions.json
~~~

One manually selected private rule can be stored at **.olt-private/ches/exception-rules.json**. Example below is a *schema illustration only*. The source ID, morphology, lemma, exact original private CHES PDF English text and ordinal **must come from the real locally inspected source**, not from this illustration:

~~~json
{
  "source_pdf_sha256": "<PINNED_GENESIS_1_PDF_SHA256>",
  "chapter_reference": "Gen.1",
  "unapproved_exception_rules": [
    {
      "reference": "Gen.1.3",
      "original_oshb_source_token_id": "<EXACT_VERIFIED_SOURCE_TOKEN_ID>",
      "expected_original_morphology": "<EXACT_SOURCE_MORPHOLOGY>",
      "expected_original_lemma": "<EXACT_SOURCE_LEMMA>",
      "kind": "WAYYIQTOL_SIMPLE_PAST",
      "green_span_ordinal": 1,
      "expected_green_span_text_private": "<EXACT_PRIVATE_PDF_GREEN_TEXT>",
      "replacement_english_private": "and he said",
      "operator_checked_original_pdf_hebrew": true,
      "evidence_note_private": "Original Hebrew verb and English source fragment were inspected; independent linguistic review is pending.",
      "approved": false
    }
  ]
}
~~~

~~~bash
python -m scripts.ches_005_safe_exceptions \
  --pdf /path/to/gen1.pdf \
  --confirm-machine-readable-use-permission \
  --rules-private .olt-private/ches/exception-rules.json \
  --output-private .olt-private/ches/gen1-english-preview.json
~~~

The user-provided rule is only accepted if it matches the exact original source token's previously constrained OLT English research verb choice and the specified original English PDF fragment. This previews an editor-selected change **without claiming a certified word alignment**.

## Real additional Genesis 2 PDF engineering audit

The independent **scripts/ches_005_chapter_layout_qa.py** checks the actual original Genesis 2 source PDF as a second chapter-layout sample, with:

- All **25 printed original source verse labels** present and in order.
- Original Hebrew source verse/token identity cross-check for all 25 Genesis 2 verses against the pinned OSHB/WLC corpus.
- Separate original source PDF page count, file size, SHA-256 and green PDF span counts.
- No third-party copyrighted CHES glyph text in public source files, test outputs, GitHub Actions logs or artifacts.
- No automatic PDF span-to-Hebrew word or morpheme mapping or claim that the filename prefix has independently certified original-language identity.

The GitHub Actions job fetches the second chapter from the pre-existing approved host over **TLS-verified HTTPS**, with no insecure bypass, and deletes the temporary files with the runner.

## Tests and status

~~~bash
python -m unittest discover -s tests -p 'test_ches_005_safe_exceptions.py' -v
python -m unittest discover -s tests -p 'test_ches_005_chapter_layout.py' -v
~~~

The ordinary GitHub Actions foundation job and the dedicated CHES source-PDF integration must pass before merge. Copyright permissions beyond reported private machine-readable use, independent lexical/grammatical verification, original-word correspondence, owner approval and Bible publication all remain **unestablished or BLOCKED**.

**Next:** After a successful original Genesis 2 layout audit, pin the actual second-source PDF metadata and use representative error/exception measurements before extending any bulk import. Keep English as sole active target; preserve README.md exactly zero bytes, the accurate technical source manifest and Git history.
