# Five research waves and falsification procedure

1. **Textual:** lock edition and immutable hash. Compare actual Masoretic pointed words, and identify readings variant between editions; for Greek lock RP2018 before any NT chapters.
2. **Morphological:** verse by verse detect prefixes, roots, homographs, noun gender, verb stem, person/number/gender, qatal/yiqtol/wayyiqtol, and clause syntax. Never infer form from “waw + yiqtol” alone.
3. **Lexical:** compare primary dictionary definitions with ancient usage, wordplay and proposed visual root imagery. Record confidence, contrary evidence, KJV-English readability, and one chosen English word family.
4. **Canonical:** inspect explicit references, same-lemma parallels, associations with Christ, and alternative exegeses. Distinguish direct lexical proof from a Christian reading; document why the link is useful.
5. **Independent QA:** search for omitted words, inconsistent roots, wrong tense, missing notes, unsupported homonyms, oversized notes, poor printed layout, and unjustified PASS claims.

Document Hebrew/Greek literal quotation, English translation, original book/chapter/verse, precise source edition, decision history, and reviewer.

Examples: Noah's name and rest are associated; Genesis 5:29's comfort uses a different root. Dove's lack of resting place (Gen 8:9) has comparable wording in Deut 28:65, while Sinai resonance is theological. Pitch in Gen 6:14 and Levitical atonement share consonants and disputed etymology. The ark dimensions in Gen 6:15 do not describe cross-shaped carpentry; 1 Pet 3:20–21 is a genuine Noah/baptism textual basis for typological exploration.

## OLT-033 — expanded name-etymology research requirements

In every original-language verse, inventory all potentially meaningful person/place/city/village names, divine names and titles, and distinctive Hebrew, Aramaic or Greek scriptural designations. Prioritize explicitly explained biblical names, documented historical etymologies, and actual source-text wordplays. For every occurrence, separately verify the **original word/lemma/morpheme, textual edition, grammatical identity, referent, and context**, then determine whether a meaningful English underword is warranted.

Etymology is not the same as a biblical pun; morphologically plural Elohim does not automatically mean multiple gods; reconstructed Hebrew root imagery is not a compulsory translation; uncertain El Shaddai and Genesis 49:10 Shiloh must not be assigned invented definitive meanings. For NT names borrowed from Hebrew/Aramaic, compare source traditions and use exact RP2018 Greek words **only after that NT edition is pinned and imported**.

Compare BDB and other independent lexicographical/historical sources, as well as contrasting positions. Each proposed secondary English word must have a clearly marked evidence category, uncertainty flags, original/English context and explanatory note. An unknown meaning remains REVIEW_REQUIRED without forced underword. Full-OT/NT coverage verification and print QA are new release dependencies.
- **Noah (Gen 5:29):** examine נֹחַ / נוח (rest) and the separate נחם (comfort) wordplay; never equate their Hebrew root identities even when both participate in the naming narrative.

## OLT-034 — independent source-first multilingual research

Always research the Hebrew or Biblical Aramaic original for OT, and the pinned Robinson–Pierpont 2018 Greek original for NT once legitimately imported. Original verse/source-token ID, morphology, exact lexeme/homonym identity, edition provenance and semantic candidates take precedence over any English gloss. The English master lexicon is a reference/contrast, never a required pivot language.

For each target locale, independently investigate source semantics, equivalent target-language concepts, inflection, syntax, tense/aspect, writing system, name transliteration, contextual person/place identity, and readability. Create source-aligned locale decision records, distinguish source-evidenced etymology from OLT owner theological interpretation, and record dissenting/uncertain readings. No fake Greek tokens and no presumed target translations from English alone. Maintain separate locale linguistic signoff and publishing QA.

## OLT-035 — reproducible source-level provenance waves

Before analyzing any Hebrew/Aramaic/Greek original, pin an immutable revision, inspect textual license and attribution, and record byte-level digests of the **actually imported data**. The 39 OT imported JSON books have Git blob SHA-1 fingerprints; their upstream XML SHA-256 values are earlier imported **recorded digests**, not freshly recomputed remote signatures. Run all-OT exact token/verse/morphology-language uniqueness checks separately from independent morphological review. Detect source Aramaic from original `A` morphology tags, not from a book label or English gloss.

For RP2018 use official ByzTxt tag `v3.3.2` (commit `27a45ff...`), not a mutable HEAD or a later 2026 edition. Its 3 John Unicode CSV sample must be byte-identical to upstream. Since its Greek text is verse-level and lacks a stable token ID/morphology map, leave these entries null while designing a verified word-level alignment pipeline. Only after original authoritative files and token methodology are vetted may target-language translation choose a Greek source token. Edition/byte equality does NOT certify disputed meanings or published source accuracy.

## OLT-035B — first full 27-book Greek original verse-source research boundary

Review all authentic Greek NT source verse strings from pinned official ByzTxt RP2018 v3.3.2 **27 primary book CSVs**. Every one is byte-identical to the upstream convenience Unicode CSV, which the upstream says is generated from authoritative `source/CCAT` files. Compare selected/all files with the editor's original `source/CCAT` apparatus before asserting independent textual fidelity. Do not invent Greek word-level IDs or morphology from whitespace/punctuation. Keep the original extra passage files **John 7:53–8:11 (PA)** and **Acts 24:6–8 (ACT24)** as separately retained evidence; their interaction with continuous verse text is an actual textual decision and cannot silently overwrite verses. Next wave: verified Greek original lemma/morphology/token source, source-traced English reference lexicon, independently reviewed multilingual translation.

## OLT-035D — source-internal alternative analyses and empty verse slots

Use upstream official RP2018 editor-owned source/Strongs/*.BP5 (not reverse-engineered Unicode text) for original word forms, Strong references and morphological analysis. The 27 exact upstream Git blobs contain 140,149 primary editor-word forms and 28 extra parse pairs attached to existing forms. Read all original tag alternatives in context, without pretending two morphology tags mean two original Greek words. The editor explicitly acknowledges that Strong mappings and parsings can contain errors. BP5 provides 7,957 reference positions, **four of which are empty placeholders**, not additional Greek Scripture: Luke 17:36; Acts 8:37, 15:34, 24:7. The 7,953 nonempty references match the 7,953 Unicode verse references; word-level Greek Beta Code versus accented Unicode CCAT conversion is NOT independently aligned. Research disputed word forms/Greek name etymologies only with source-linked evidence, never from English pivot; explicit source-critical and onomastic review remains required.
