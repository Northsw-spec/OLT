# Fresh editorial decisions — 2026-10-29

Authority: only the current explicit agreements, reconstructed anew.

- Title always **Olund's Linked Translation**.
- OT Masoretic Hebrew; NT Robinson–Pierpont Greek; English publication text and English footnotes, original languages printed alongside; no Swedish in publication.
- Unsmoothed near-interlinear English, awkward constructions deliberately preserved.
- Named finite subject plus inflection visibility: “And God — He said”.
- No neutral “it/its/itself” in the main English translation.
- Exact approved Gen 1:4: “And God — He saw the light, that [he was] — good.”
- Only ONE opening-page explanation of grammatical gender.
- EVERY verified OT wayyiqtol => English SIMPLE PAST even in prophets; no English perfect.
- Owner locks: bara=shape, asah=make, raqia=firmament, conjunctional waw=and.
- KJV-like Early Modern English where intelligible and grammatically correct.
- Visually concrete, occasionally creative root-based language only where evidence supports it.
- Christological links when warranted, not by forced Hebrew redefinitions.
- Separate lexical identities for homonyms; beneath-word **vertical** blue gloss, never “word/word” inline.
- References: Noah/Rest, serpent/divination, pitch/atonement, dove rest/foot, Noah/Christ typology.
- Distinguish source literalism, linguistic wordplay, editorial supplements and theological notes.
- 5 gates: research, lexical lock, token alignment, automatic fail-closed checks, independent print/linguistic review.
- Source morphology must be independently checked. Do not call an unreviewed draft complete.
- Canonical repository is Northsw-spec/OLT; old files are not imported.

**Open blockers:** full word-level Hebrew import and verification; comprehensive lexicon, Genesis 1 aligned translation, full footnotes, real ODT/PDF and sign-off.

## OLT-018 — owner explicitly re-confirms the bracketed Genesis 1:1 text

- **Main research text, not merely optional variant:** “In the Beginning [of His Power] God — He shaped the Heavens and the Earth.”
- Footnote on the exact bracketed phrase must compare Gen 49:3 and Deut 21:17, identifying separate source terms for “beginning” (רֵאשִׁית) and “strength” (אֹון) in those passages.
- Both “of His Power” and its possessive are interpretive English additions, absent from the original seven Hebrew words of Gen 1:1; never pretend they mean the Hebrew root directly.
- Owner approval is of layout/wording for the interpretive supplement, **not independent final publication approval of the verse**.

## OLT-020 — permanent owner theological and grammatical decision

- The framework of **Olund's Linked Translation is BINITARIAN, NOT TRINITARIAN**.
- Exact owner affirmation: **THE LORD JESUS IS THE SPIRIT**.
- Record this as the owner's confessional interpretation, not an undisputed Hebrew/Greek lexical meaning. Never force all `רוּחַ` or `πνεῦμα` occurrences to refer to Jesus regardless of their context.
- Father–Son creation parallels, e.g. John 1:1–3 and 1 Corinthians 8:6, can be interpreted binitarianly, **not** silently inserted into Hebrew source words.
- The Hebrew preposition `בְּ` is translated contextually; do not always display *with* under *in*. Show a contextually justified alternative directly beneath the English anchor, not inline.
- If the context is uncertain, emit `REVIEW_REQUIRED`; don't manufacture a grammatical or homonym PASS.
- All earlier source and owner locks, including Genesis 1:1 `[of His Power]`, Genesis 1:4, *bara/asah/raqia*, and tense rules remain binding.
- This is an **owner-approved editorial doctrine**, not an automatic independent scholarly signoff or permission to publish Genesis 1.

## OLT-021 — superseding, permanent owner correction about the Father and Son

**This clarification is authoritative and overrides every prior assistant inference that the Son was created.** The owner explicitly rejects the reading “Jesus was the first thing God created.”

- **ONE GOD:** FATHER AND SON ARE ONE — one God, **one faith, one Lord Jesus Christ**. OLT is **BINITARIAN, NOT TRINITARIAN**, and continues to affirm **THE LORD JESUS IS THE SPIRIT**.
- **THE SON IS ETERNAL AND UNCREATED.** He existed with the Father **before the world's foundation**; he was not a created being and his existence did not begin at Mary's childbirth.
- **THE FATHER AND SON CREATED THE WORLD TOGETHER**, a joint Father–Son work preceding the Son's incarnation.
- **INCARNATION:** The already eternally existing Son **became human through Mary**. Distinguish the beginning of human life from any supposed beginning of the eternal Son's existence.
- **FIRSTBORN:** The owner's reference to Christ as the **Firstborn Son** and to the Revelation 3:14 “beginning of God's creation” language must never be paraphrased as **first created**. This expresses the owner's interpretive understanding of the eternal Son who later became human; it does not prescribe an automatic Greek dictionary meaning for `ἀρχή`.
- **SOURCE/INTERPRETATION FIREWALL:** Father–Son creative agency and the confession “Jesus is the Spirit” inform explicitly marked `BINITARIAN_CANONICAL_INTERPRETATION` notes. Neither claim is a machine-inferred Hebrew/Greek word meaning or an automatic rule that `בְּ` in Genesis 1:1 is instrumental.
- Preserve OLT-018's exact **[of His Power]** main line and footnote, OLT-020's `בְּ` contextual engine policy, all prior lexical/tense locks, and the BLOCKED publication gate.

**Authoritative detail:** [OLT-021 creed clarification](OLT-021_BINITARIAN_CREED_CLARIFICATION.md).

## OLT-022 — only Gen 1:1 receives owner-selected In / with vertical link

- **In Genesis 1:1**, visually place lowercase **with** DIRECTLY UNDER capitalized **In**; the primary text **In the Beginning [of His Power] God — He shaped the Heavens and the Earth.** is unchanged.
- Owner's explicitly **binitarian reading:** temporal *In the Beginning* and canonical interpretive *With the Beginning* (Beginning interpreted as the **eternal uncreated Son**, joining the Father in creation). The latter is not treated as independent, undisputed Hebrew syntax.
- Although Hebrew `בְּ` has demonstrable instrumental functions in other settings, its normal contextual reading in Gen 1:1 is temporal. Strawn (2022) offers an exegetical “With Wisdom” proposal; this is not a verdict that the Hebrew lexically requires *with the Son*.
- The extra `with` is an owner-chosen theological **under-word link** (`BINITARIAN_CANONICAL_INTERPRETATION`), not a source-word addition, false homonym, or global `in → with` policy. Its source anchor is OSHB `01xeN`, prefix `בְּ`; retain source IDs and raw morphology.
- Maintain the `[of His Power]` footnote and Gen 1:1's **exact** English primary sentence. Under-word colors in eventual typesetting are purple/blue; the GitHub Markdown edition shows the words stacked and notes uncertainties.
- Code/policy: `data/policy/olt_underword_overrides.json`; documentation: `docs/OLT-022_GENESIS_1_1_IN_WITH_UNDERWORD.md`. No new English or Hebrew philological publication approval is inferred.

## OLT-033 — owner-binding Bible-wide name/meaning underword rule (2026-10-30)

- Apply to every relevant occurrence throughout **both Testaments**: names of people, places, cities, villages, divine names/titles and distinctive meaning-bearing scriptural terms, where semantic or theological secondary English content is actually supportable.
- Keep original Hebrew/Greek and primary English name unchanged; show an English word/phrase directly **BELOW** the name (purple top, blue bottom), source-linked and annotated. No inline slashes.
- Preserve exactly the owner's requests in the **provisional name lexicon**: Moses/Draw, God-Elohim/Mighty Governance, El/Mighty, El Shaddai/My Mighty Strength, Jerusalem/City of Peace, David/The Beloved. Exact proposed spelling is normalized to **Strength**, not misspelled **Strenght**.
- Explicit **linguistic distinctions**: Moses/Draw is biblical naming wordplay with debated historical origin; Elohim/Mighty Governance is an owner-selected association concerning divine rule, NOT a literal Hebrew meaning or indication of multiple gods; El/Mighty is an uncertain root-strength association; El Shaddai/My Mighty Strength is **not supported as literal Hebrew**, especially because no first-person possessive exists in the source; Jerusalem/City of Peace is a traditional and disputed toponym meaning; David/The Beloved is a supported but not fully certain etymological association.
- Shiloh in Genesis 49:10 is a textually and semantically disputed reading, distinct from the city Shiloh (Joshua 18:1). NT Siloam/“Sent” is explicitly explained in John 9:7 and is **not automatically the same word or derivation**. NT data must await independently pinned RP2018 Greek source IDs.
- Owner-approved **policy scope** does NOT mean the requested phrases were independently certified. There are NO new verified homonym links or finalized translation decisions. Names with unknown/disputed meanings require a research record and REVIEW_REQUIRED, not invented glosses.
- The old Genesis 1:1 In/with exception remains separate and unique. The new God/Mighty Governance proposal may coexist in its own name-meaning namespace once the source occurrence is verified and layout QA passes.
- Machine policy: `data/policy/olt_name_underword_policy.json`; candidate lexicon: `lexicon/name_underwords.json`. OLT research/publication still BLOCKED.
- **Additional binding name-underword decision:** Noah → **Rest**, from the Hebrew nuach/rest association. Genesis 5:29 uses the separate root nacham/comfort as name wordplay. Noah/Rest is not automatically the same lexical meaning as the separate verb comfort.

## OLT-034 — binding common core and separate language repositories (2026-10-30)

The owner has explicitly agreed that Northsw-spec/OLT is the shared source-first Hebrew/Greek/Aramaic Bible analysis and future translation engine. Every real target language has its own repository, rather than its own duplicated original-language motor. The English master lexicon is a **source-linked editorial reference**, NOT an English-pivot translation source. A future Japanese, Amharic, Chinese or Icelandic choice must always trace back to the actual original-language token, lemma, morphology and context and be independently verified for that target language.

Source facts and evidence, OLT owner theological/English editorial decisions, and independently reviewed target-language decisions are three distinct authority layers. The existing OLT binitarian owner framework remains an explicit theological interpretation layer; source lexemes are not altered. Preserve all Gen 1:1 and Gen 1:4 wording, owner wayyiqtol English tense locks and name/underword candidates, including God/Elohim/Mighty Governance and Noah/Rest, as **English** editorial data rather than automatic foreign-language glosses.

First reusable deliverable is the source-first research-packet library olt_core (version 0.1.0, contract 1.0) with six unpopulated locale profiles and negative CI tests; none are Bible translations. RP2018 NT Greek is unpinned and must not be fabricated. The release remains BLOCKED. Details: docs/OLT-034_MULTILINGUAL_ARCHITECTURE.md.

## OLT-035 — Source revisions, original-language identity and release restrictions

**Binding implementation:** Keep exact immutable OT source snapshots (39 JSON book Git blob SHA-1 hashes and pre-recorded upstream OSHB XML SHA-256 digests) before any locale research. Original OSHB word IDs remain unchanged. The imported morphology provides Hebrew (H/hbo) vs Biblical Aramaic (A/arc): currently 301,837 / 4,948 source-tagged word tokens, not independently verified philology. Never coerce augmented `1254 a` vs `1254 b` or unresolved plus-marked lemmas into a shared lexical meaning.

Pin the *chosen* Greek RP2018 to official ByzTxt `v3.3.2`, commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`. Its Third John 14-verse original Greek CSV is imported byte-identically, blob `296e85242768aab57007a69cf62b92aef0b5067b`. The CSV is a derived convenience copy; editor's original `source/CCAT` files remain primary. Do NOT fabricate word token IDs, lemma identities or Greek morphology from these 14 verses. The other 26 NT books and all word-level Greek identity links are not imported. No source, English lexical or language publication approval.

Canonical registry: `data/engine/olt_035_source_provenance.json`; reader `olt_core/sources.py`; details `docs/OLT-035_SOURCE_PROVENANCE.md`. OLT-034 English master remains a reference, not a translation pivot. OLT-033 underwords and all existing owner-approved renderings remain unchanged.

## OLT-035B — All 27 RP2018 Greek NT source books imported as verse text

Binding source decision: preserve the official ByzTxt **RP2018** edition at immutable v3.3.2 / `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`. Its 27 ordinary NT Unicode Greek CSV book files were copied bit-for-bit with matching upstream Git blobs, and two extra Greek passage files (`PA.csv`, John 7:53–8:11; `ACT24.csv`, Acts 24:6–8) are kept in a separate ancillary folder, **NOT automatically merged into the 27 continuous texts**. Greek source word IDs, Greek lemma/morphological tags, source-text collation with authoritative CCAT originals, English lexical completion and all target language releases are NOT complete. The earlier OLT-035 3 John-only register is now historical; the live 27-book source inventory is `data/engine/olt_035b_rp2018_verse_inventory.json`. Maintain all prior owner wording and source/publication boundaries.

## OLT-035D — editor-original Greek word morphology and preservation of alternatives

The owner-mandated Greek NT source is RP2018, pinned ByzTxt v3.3.2 commit 27a45ff1b7be6c17ccbfeac414f3f55732ae8e. Import **all 27 official source/Strongs BP5 editor files** byte-identically, with **140,149 primary Greek Beta Code forms and Strong/morphological tags**; **28 additional alternative parse records attach to existing words**, not additional Greek words. There are **7,957 verse slots but four are EMPTY**, Luke 17:36 and Acts 8:37, 15:34, 24:7, leaving **7,953 word-containing verses**; never invent words for the empty lines. Do not auto-splice the separate PA/ACT24 passages into ordinary text. Original BP5 does NOT supply native token IDs; OLT's derived word-position locators must always say they are invented reproducible positions, not native source IDs. Strong is a lexical REFERENCE, not verified lemma FORM or semantic etymology. Accented Unicode Greek word alignment, scholarly approval, other-language translation and publication remain NOT DONE / BLOCKED. Contracts: data/engine/olt_035d_greek_word_source_manifest.json; olt_core/greek_words.py.
