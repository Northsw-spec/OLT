# OLT-004 — Original XML crosswalk audit

**Purpose:** correct incomplete candidate joins using the actual pinned source
`HebrewLexicon` commit `21c9add13bc727d3a951361778e97e3ff7afd1ce`.
The original schema `LiSchema.xsd` confirms that lexical index entries carry
`xref` attributes including `bdb`, `strong`, `aug` and `twot`.

## Verified linkage path
1. Read exact lexical component identity in
   `data/quality/observed_exact_lemmas.json` (e.g. `1254 a`).
2. Convert **only its spacing**, e.g. `1254 a` → AugIndex lookup `1254a`,
   while retaining `1254 a` as the authoritative source key.
3. Use exact `<w aug="1254a">entryID</w>` in original `AugIndex.xml`.
4. Confirm `entryID` exists as an `<entry id="entryID">` in original
   `LexicalIndex.xml`; refuse dangling and ambiguous targets.
5. Read this entry's `<xref ...>` references, validating target IDs against
   BDB and Strong XML dictionary `<entry id>` values.
6. Do **not** interpret missing matches as absent from biblical Hebrew, nor
   merge separate homonyms based on shared base Strong's number or consonants.
7. Do **not** collapse a `+` marker to an unmarked lemma. Classify unresolved
   markers for further independent research.

## Produced data
- `data/quality/verified_id_crosswalk.jsonl`: a source-ID-to-dictionary-reference
  table with exact keys, classified unresolved status and explicit xref validation.
- `data/quality/verified_id_crosswalk_report.json`: provenance and counts,
  unresolved/dangling xrefs, and a conspicuous editorial release blocker.

**Validation boundaries:** even a perfect XML identifier link does not certify
that the linked dictionary meaning is correct in a passage, or an owner-approved
English word. Every OLT English meaning remains a separate editorial decision.

## Identifier-format correction (OLT-004B)
LexicalIndex `xref strong="1254"` can refer to Strong dictionary `entry id="H1254"`. The validator now accepts only an unambiguous numeric-ID prefix transformation and records its method. The original raw attribute is preserved. A suffix `xref aug="a"` is an *augmentation letter*, not necessarily a full `122a` identifier; it is checked as such. Outstanding records are categorized by plus markers versus genuinely absent identifiers, with examples.
