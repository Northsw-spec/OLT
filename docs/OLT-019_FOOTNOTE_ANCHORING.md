# OLT-019 — Verified in-text footnote anchoring, source-faithful preview

The first word-linked research footnote now attaches **immediately after** the phrase it explains:

`In the Beginning [of His Power][^gen-1-1-power] God — He shaped the Heavens and the Earth.`

This replaces the older misleading preview placement after the final word *Earth*. The **main English wording itself is unchanged**, and the seven source Hebrew word token identities, source morphology, and the owner's bara/shape decision remain unchanged. This is a link rendering adjustment in Markdown only.

A reusable `scripts/research_footnotes.py` function validates that each footnote:
- Has one unique valid identifier, a correct verse reference, and a unique exact-match English anchor in that verse.
- Has a nonempty single-paragraph English body and explicit evidence references.
- Makes no fabricated claim that an editorial theological supplement was an independently written Hebrew source lexeme.
- Has a strictly research-only status, never *published* or *independently certified*.
- Generates exactly one inline `[^id]` marker immediately after its English anchor and one note definition.

The generated chapter JSON now includes a footnote anchor manifest. Negative regression tests fail on missing anchors, ambiguous text spans, duplicate IDs, missing evidence, mismatched verses, and promoted publication statuses.

**Footnote interpretation:** The external original Hebrew comparison supports that *rēʾšît* and *ʾôn* are SEPARATE source lexemes in Gen 49:3 and Deut 21:17. Their analogy may inform the owner's bracketed theological reading, but the latter is **not** the literal reading of Genesis 1:1.

Primary comparison: [Genesis 49:3](https://biblehub.com/text/genesis/49-3.htm) and [Deuteronomy 21:17](https://openbible.com/text/deuteronomy/21-17.htm). The Genesis 1 `[of His Power]` phrase is not imported into OSHB source word slots.

**Scope limits:** Markdown notes are endnotes in GitHub preview, not demonstrated physical page-bottom footnotes in DOCX/ODT/PDF; typography and independent scholarly approval remain blocked.
