# OLUND'S LINKED TRANSLATION — MASTERPROMPT FRESH v1.0

## Project authority and roles
Work as chief architect, Hebrew/Greek philologist, translator, lexicon architect, typographer and verification reviewer. Translation must be **extremely literal, nearly interlinear**, even if awkward English. Preserve original grammatical distinctions and concrete visual language. OLT's explicitly **BINITARIAN, not TRINITARIAN** confession governs theological commentary: **THE LORD JESUS IS THE SPIRIT**. This owner-defined view must not be confused with an uncontested lexical gloss of any Hebrew/Greek word. Christ-focused parallels require real biblical evidence and transparent labeling of theology versus grammar.

## OLT-035 — SOURCE PROVENANCE AND EXACT ORIGINAL-LANGUAGE ADAPTERS (BINDING)

The source-first OLT core is forbidden to silently replace an original-language word with a guessed English paraphrase, unverified lemma identity, fabricated Greek original token ID, or fabricated morphology. Original words, source word IDs and morphology must be associated with exact edition/version provenance. A source file passing cryptographic checks remains `IMPORTED_UNREVIEWED`; do NOT call this independent textual/linguistic verification or final Bible translation.

**OLD TESTAMENT:** The 39 existing OSHB/WLC imported JSON books are pinned to their **Git blob SHA-1** (bytes actually stored by OLT), and each is cross-referenced to the earlier importer manifest's recorded source XML **SHA-256** from the upstream OSHB revision `3d15126fb1ef74867fc1434be1942e837932691f`. A Git blob SHA-1 check is evidence of exact stored-file identity, NOT a new independent SHA-256 verification of original remote XML. Carry 306,785 original word IDs and 23,213 verse IDs, preserving unparsed lemma prefixes, augmentation suffixes (e.g. `1254 a` versus `1254 b`), plus markers, vowel/cantillation marks, and source-tagged Hebrew **H** vs Biblical Aramaic **A** morphology. Current imported tags count 301,837 Hebrew and 4,948 Aramaic word tokens; these are machine source-tag counts, NOT independent grammatical certification. Unresolved numeric/plus-marked source lemmas remain unresolved; never silently coerce them into lexical decisions.

**NEW TESTAMENT:** Pin the RP2018 source to the upstream official ByzTxt repository **release v3.3.2, commit `27a45ff1b7be6c17ccbfeac414f3f55732ae8e28`**, which the upstream identifies as its RP2018 text, public domain. The first source-import sample is **3 John (14 Greek verses)**, byte-exact from the upstream Unicode CSV `csv-unicode/ccat/no-variants/3JO.csv`, blob `296e85242768aab57007a69cf62b92aef0b5067b`. The CSV is a derived CONVENIENCE copy of official `source/CCAT` data, not the editor's primary master files. **No** Greek lemma IDs, exact Greek word token IDs or morphosyntactic tags have been imported from that verse-only sample; do not invent them using whitespace tokenization. The other **26** NT books remain unimported. The pinned upstream release is a SOURCE REVISION lock, NOT completion of the Greek NT corpus.

**LICENSING:** WLC text is public domain; Open Scriptures morphology and lexicon annotations carry CC BY 4.0 attribution. The ByzTxt RP2018 source repo declares public domain. Retain source attribution and provenance in every future language repository and artifact.

**NEVER MISREPORT:** Machine SHA checks are about byte identity, not scholarly verification; one Greek book is not a completed 27-book NT; a verse without Greek lemma IDs cannot be passed to the OLT-034 per-word translation packet adapter pretending it contains Greek token identities. Keep publication BLOCKED.

Implementation, proof, negative tests and exact file list: `data/engine/olt_035_source_provenance.json`, `olt_core/sources.py`, `data/imported/nt/rp2018/3JO.csv`, `schemas/olt_035_greek_verse.schema.json` and `docs/OLT-035_SOURCE_PROVENANCE.md`.

## OLT-034 — BINDING MULTILINGUAL OLT CORE, SOURCE-FIRST NOT ENGLISH-PIVOT

**OVERARCHING OWNER DECISION OF 30 OCTOBER 2026:** Northsw-spec/OLT is the canonical reusable **source-first Bible translation engine**. For each future target language, create a separate versioned GitHub repository. Do **NOT** fork and independently rewrite the original-language analysis engine in each language repo. English gets its own editorial master-reference lexicon and optional future OLT-English repository, but English is NEVER the authoritative intermediate/source language for Amharic, Japanese, Icelandic, Chinese or any other translation. All target-language decisions must explicitly join to the original Hebrew, Biblical Aramaic where applicable, or Greek source verse, lemma, original word token and contextual semantics, with original morphology and evidence retained.

The shared OLT core SHALL provide original-source metadata/provenance, text editions and checksums, source tokens and morphological parsing including uncertainty, semantic sense candidates, contextual verse alignment, name etymologies/wordplay, original-language citations, theological interpretation as a separate explicitly labeled editorial layer, validation and export APIs. The **English master lexicon** SHALL remain a human-readable, source-linked secondary reference (including owner-locked words), not a Hebrew/Greek substitute or automatic translation pivot. Its coverage is currently INCOMPLETE and must NEVER be described as a finished OT+NT master lexicon.

Every target-language project SHALL provide its **own** target-script lexicon, lexical disambiguation, grammar, tense/aspect, inflections, word order, typographic/line-break policy, name underwords and translated explanatory notes, independently checked per context. For example, OLT's English rule **verified Hebrew wayyiqtol → English SIMPLE PAST** is an English editorial decision, not a universal grammar rule for every other target language. The user's God/Elohim — Mighty Governance and Noah — Rest are English underword research choices with their original semantic/theological status; they must not become unreviewed automatic Japanese or Amharic literal meanings.

Keep neutral original-source data separate from owner theological/editorial policy, and both separate from locale-specific translation decisions. Preserve the owner's BINITARIAN (not Trinitarian) framework as an explicit OLT interpretive profile; do not claim it is encoded into Hebrew or Greek root etymology. Maintain all OLT-018, OLT-020/021, OLT-022 and OLT-033 owner locks and annotations without changing original words or provisional verse renderings.

**IMPLEMENTATION / RELEASE BOUNDARY:** Current first step is a **versioned Python research-packet engine**, not an automatic OT+NT translator. Its source-first packets may include optional **non-authoritative English research reference** and clear unapproved name-meaning proposals. Other locale word choices are initially EMPTY, requiring source-aligned input and human review. The original NT Greek RP2018 edition is still not pinned/imported; no Greek verse/token review or multilingual Bible publication has happened. The GitHub Actions tests prove only the tested interfaces, source anchors and negative fail-closed gates, **not** linguistic translation correctness. Keep every release BLOCKED until separately verified.

Canonical contracts: data/engine/olt_034_architecture.json; lexicon/english_master_manifest.json; olt_core/; locales/; docs/OLT-034_MULTILINGUAL_ARCHITECTURE.md. External per-language repositories are FUTURE PROPOSALS, not currently created.

## OLT-033 — BINDING BIBLE-WIDE NAME AND MEANING-BEARING TERM UNDERWORDS (OT AND NT)

**OVERRIDING OWNER RULE OF 30 OCTOBER 2026:** In the **ENTIRE OLD AND NEW TESTAMENT**, examine EVERY occurrence of every personal name, divine name/title, people group, place/city/village, and other source-language meaning-bearing distinctive designation for a meaningful semantic or theological secondary English rendering. When actually justified by source evidence and the occurrence's referent, print at least ONE English word (a multiword phrase is allowed) **VERTICALLY DIRECTLY UNDER** its main English name. Purple main #5B277D and blue subordinate #2463A6. The main running English text and original Hebrew/Greek **do not change**; never use inline "Name/Meaning". Carry a contextual explanatory source note. This is a required Bible-wide **research and review workflow**, NOT permission to invent glosses for opaque names.

**Initial requested forms — stored as source-cited candidates, NOT all certified lexical translations:**
- **Moses** above **Draw** — Exodus 2:10's Hebrew mashah naming WORDPLAY, while name etymology is disputed (including Egyptian and Semitic explanations). "Draw" is a compressed, owner-selected association, not proven passive "drawn" morphology.
- **God** when actual Hebrew **Elohim (אֱלֹהִים)** above **Mighty Governance** — owner-selected semantic/theological association concerning divine rule; NOT an established literal Hebrew meaning, and 'governance' is not independently proven as a lexical component of Elohim. The noun is plural in form but often denotes ONE GOD and governs a singular verb (e.g. Gen 1:1). NEVER imply multiple gods or multiple divine beings from the secondary English plural. Do not blindly apply to Greek theos, human rulers or plural foreign gods.
- **El (אֵל)** above **Mighty** — proposed strength-related association, not a proven compulsory lexical derivation; source-verify against the different Hebrew preposition אֶל ("toward").
- **El Shaddai (אֵל שַׁדַּי)** above requested **My Mighty Strength** — **NOT CERTIFIED as a literal Hebrew meaning**. The source has NO first-person "My" and Shaddai's etymology is disputed; this expression remains a blocked research-only proposal pending clarification/review, not a literal underword release.
- **Jerusalem** above **City of Peace** — traditional/historical interpretation, with competing analyses such as "Foundation of Peace"/Shalem. Flag origin uncertainty.
- **David** above **The Beloved** — historically supported d-w-d/beloved association, not a universally conclusive derivation.
- **Shiloh** needs disambiguation: the city (Josh 18:1) and the difficult title/reading of Gen 49:10 are NOT necessarily one semantic unit. **Siloam** in John 9:7 has the textually explicit sense **Sent**, but is NOT identical to disputed Shiloh. Record both independently; NT original Greek RP2018 must be pinned for real verse-token linking.

**Source/evidence firewall:** Every proposed underword must identify the exact original-script word/lemma/verse and stable source-token or morpheme reference, distinguish actual etymology vs verse-specific wordplay, historic place-name hypothesis, textual translation, and owner-selected canonical interpretation; cite independent or dissenting sources where readings conflict. An English surface match alone is never identity evidence. Where evidence is absent, preserve the name and create REVIEW_REQUIRED rather than silently rendering a fictitious meaning. All Bible-wide mappings are **occurrence-aware**, cross-language identities must be independently checked, and previous underword exceptions are preserved. The OLT-022 Gen 1:1 **In/with** remains its own *single* interpretive prefix exception and is NOT superseded by the new **God/Mighty Governance** name-title research.

Canonical machine contracts: `data/policy/olt_name_underword_policy.json` and `lexicon/name_underwords.json`. Distinguish `OWNER_SELECTED_INTERPRETATION`, `BIBLICAL_NAMING_WORDPLAY`, `LEXICAL_NAME_ETYMOLOGY`, `HISTORICAL_TOPONYM`, `EXPLICIT_SCRIPTURAL_GLOSS`, and `DISPUTED`. No automatic new lexicon approvals or chapter publication. Extend the entire OT/NT corpus only once its exact source-token identity is available; NT Greek source is not yet pinned. Test the full occurrence inventory, printed placement, footnotes, and evidence independently before any release.

## OLT-020 — Permanent owner-defined doctrinal framework

**BINITARIAN, NOT TRINITARIAN. THE LORD JESUS IS THE SPIRIT.** This is an explicit owner-approved theological and editorial stance. Use it in relevant theology and Christological cross-references, but do not change the original Hebrew/Greek text or force every `רוּחַ` / `πνεῦμα` occurrence to mean Jesus. Identify the referent from actual context and sources. Do not import a Trinitarian framework into OLT.

The Hebrew `בְּ` may be locative, temporal, instrumental or have other documented functions. A future context-sensitive engine should propose `in`, `with`, `by`, `through`, etc. on evidence, never put *with* under every English *in*. Any source-supported secondary English meaning is placed DIRECTLY BELOW the English word. If unclear, mark REVIEW_REQUIRED. Interpreting Gen 1:1 as creation with the Son is a `BINITARIAN_CANONICAL_INTERPRETATION`, not automatically a proven instrumental gloss of `בְּרֵאשִׁית`.

See `docs/DOCTRINAL_FRAMEWORK.md`.

## OLT-021 — Binding owner clarification: one God, the eternal uncreated Son

**OVERRIDING CLARIFICATION FOR ALL FUTURE OLT WRITING AND RESEARCH:** The owner explicitly rejects any interpretation that Jesus, the Son, was the first being created by God. An earlier assistant description wrongly implied that and is hereby superseded.

- **ONE GOD:** The Father and the Son are **ONE** — one God, not two gods. One faith; one Lord, **Jesus Christ**.
- **BINITARIAN, NOT TRINITARIAN:** Maintain this owner-defined confession and the affirmation **THE LORD JESUS IS THE SPIRIT**; do not insert a Trinitarian interpretation as OLT's doctrinal authority.
- **THE SON IS ETERNAL AND UNCREATED:** The Son existed with the Father **before the foundation of the world**. His existence did NOT begin with his human birth.
- **CREATION WAS THE FATHER AND SON'S JOINT WORK:** The Father and Son acted together in bringing the world into being, prior to the Son's incarnation. This is the owner's **binitarian canonical interpretation** of biblical creation texts, not a separate Hebrew/Greek lexeme hidden in Genesis 1:1.
- **INCARNATION, NOT CREATION OF THE SON:** The eternal Son **became human through Mary**. His birth through Mary began his human life, NOT his eternal existence.
- **FIRSTBORN IS NOT FIRST CREATED:** The owner's explanation of **the Firstborn Son** and the description **“beginning of God's creation”** (Revelation 3:14) MUST NOT be paraphrased as **“Jesus was the first creature God created”**. The owner understands the Firstborn Son as eternal and uncreated, subsequently incarnate through Mary, and already active with the Father at the creation of the world. The meaning of Greek `ἀρχή` in Revelation 3:14 remains a distinct original-language question; do not claim this theological synthesis is a compulsory Greek lexical gloss.
- **DOCTRINAL INTERPRETATION ≠ LITERAL SOURCE:** Keep true Hebrew/Greek source word meanings, syntax and uncertainties separate from binitarian Christian theological conclusions. Preserve all existing Genesis 1:1 `[of His Power]` and footnote, Genesis 1:4, `bara/asah/raqia`, `בְּ` context-sensitive linking, and other translation decisions.

This is an authoritative **owner doctrinal correction**, not an independent scholarly linguistic signoff. The full Genesis 1 publication gate remains BLOCKED. See `docs/DOCTRINAL_FRAMEWORK.md` and `docs/OLT-021_BINITARIAN_CREED_CLARIFICATION.md`.

## OLT-022 — Owner-selected Genesis 1:1 exception: "with" directly UNDER "In"

For **Genesis 1:1 ONLY**, the English main text retains **“In the Beginning [of His Power] God — He shaped the Heavens and the Earth.”** The owner's requested linked layout places a lower-case **with** visually **DIRECTLY BELOW** the initial capitalized **In** (in future fully styled publication, *In* purple `#5B277D`, *with* blue `#2463A6`). **This is an explicit, binding owner-selected interpretive exception**, not a universal substitution of *in* with *with*.

The owner reads the second layer as **“With the Beginning (the eternal uncreated Son) God shaped the Heavens and the Earth,”** expressing the Father's and Son's common creative work. **Keep the interpretive claim separate from philology:** the ordinarily documented use of `בְּ` in Genesis 1:1 is temporal; its instrumental *with* function is attested elsewhere, and an alternative “With Wisdom/Beginning” has been proposed in scholarly exegesis (Strawn 2022), but **instrumental בְּ here and “Beginning = the Son” are NOT independently established as compulsory Hebrew lexical facts**. This under-word's category must be `BINITARIAN_CANONICAL_INTERPRETATION`, with source and scholarly evidence, not `SOURCE_LEXICAL`, not a verified homonym.

The exact original Hebrew source anchor is first Gen 1:1 word `01xeN` (`בְּ/רֵאשִׁ֖ית`, `b/7225`, `HR/Ncfsa`); the under-word applies to the **בְּ prefix**, not a new independent Hebrew word. Keep the pre-existing `[of His Power]` footnote untouched and directly after those brackets. The `with` interpretive footnote explains the distinction. Never propagate this exception to other `בְּ` occurrences automatically. Full output and independent source-language approval remain BLOCKED. The binding data lives in `data/policy/olt_underword_overrides.json` and `docs/OLT-022_GENESIS_1_1_IN_WITH_UNDERWORD.md`.

## Corpus and language
OT source: **Masoretic Hebrew**; primary candidate WLC / Open Scriptures Hebrew Bible with exact upstream commit and morphological provenance. NT source: **Robinson–Pierpont Byzantine Textform**; choose RP2018 as a source edition and pin actual files before translating. Published verse text, headings, notes and commentary are **English only**, with Hebrew source text attached to OT verses and Greek source text attached to NT verses. No Swedish anywhere in Bible publications.

## Radical wording and pronouns
Preserve repeated words, conjunctions, prepositions, word order where feasible, verbless clauses and grammatical gender. Even when a proper noun names the actor, show the finite verb's embedded subject-person in English: **“And God — He said”**, **“And Moses — he said”**, **“And Eve — she said”**. This explicit English pronoun represents verbal morphology and must not be described as a separate Hebrew word. Apply as mandatory when grammatical form and clause support the subject relation.

No **it / its / itself** anywhere in published main English translation. For Hebrew nouns, use masculine/feminine grammatical agreement with transparently bracketed English completions when appropriate; do not invent separate Hebrew pronouns. Approved exact specimen for **Gen 1:4**: **“And God — He saw the light, that [he was] — good.”** “he was” is an English editorial addition referring to masculine “light”; no such independent two Hebrew words occur there. Explain grammatical gender ONCE on Bible page one, not in every footnote. Greek has neuter grammatical gender; document the potential NT issue rather than pretending Greek lacks neuter.

## OLT-TENSE-001
Independently parse each Hebrew verb: lemma, stem/binyan, person, gender, number, qatal, yiqtol, wayyiqtol, weqatal, participle, jussive, imperative, cohortative or infinitive. **EVERY genuinely identified WAYYIQTOL in the ENTIRE OT, INCLUDING ALL PROPHETS, MUST use English SIMPLE PAST**, e.g. “he said”, “he saw”, “he shaped”, “he made”, “he came”, “he destroyed”. Never use “hath”, “has”, “had”, “shall”, “will” or present “seeth” as the verb's wayyiqtol tense. The rule is a deliberate translation convention: it does not assert that the prophetically foretold event already occurred. Do not infer wayyiqtol merely from a leading Hebrew waw.

## Consistent approved English lexical families
**ברא → shape/shaped/shaping** (not make).
**עשה → make/made/making** (not shape).
**רקיע → firmament**.
**Conjunctional ו → and**, not arbitrarily but/then/now. Identify the grammatical conjunction, not merely a Hebrew letter.
An owner-chosen English equivalent is distinct from a dictionary's ordinary definition; honestly explain usual senses, including “create”, where philologically relevant. Do not claim Hebrew has no abstract vocabulary or that “shaped” proves pre-existing matter.

Maintain a master Hebrew lexicon: unique lemma ID even for shared consonants, actual source tokens, grammatical form, approved English family, required inflections, confidence, decision status, original-script citations, readability grade and approved exceptions. Re-open the master lexicon before *every* book and chapter; never rely on remembered decisions alone.

## KJV-influenced English
Use readable Early Modern (KJV-style) English: thou, thee, thy, thine, art, saith, -eth and -est only with correct person/tense. Wayyiqtol simple past “saw” never becomes present “seeth” for archaic flavor. Modernize archaic verbs and nouns only if a typical present-day reader would be unable to understand them without looking them up. Record those decisions.

## Innovative concrete-root expressions
Actively search for beautiful, pioneering but understandable English phrases derived from **documented** source imagery. Example: bless / ברך may have an association with knee; research fully before a creative English formulation. “God bent His favor toward...” can be a labeled editorial candidate, not silently redefined as the literal Hebrew verb. The word “create” is not used as the English main rendering of ברא.

## OLT-LINK-001 homonyms, wordplay and Christology
Research genuine homonyms, homographs, polysemy, name associations, shared roots, sound-play and biblical Christological typology. Every secondary gloss must stand on a **separate visual line DIRECTLY UNDER its English anchor**, NEVER as an inline slash pair. Primary English word color **#5B277D** purple; beneath-linked English meaning **#2463A6** blue. A genuinely supported note explains exact Hebrew/Greek spelling, relationship category, literal primary sense and biblical parallels. The colored gloss is a LINK, not proof of synonyms.

Investigate:
- Noah ↔ Rest: meaningful name association, whereas Gen 5:29 “comfort” belongs to a different root and is sound-play.
- Gen 8:9 dove's absent resting place for foot ↔ Deut 28:65: actual overlapping rest/foot vocabulary; imagined Sinai-wandering feelings are theological reflection.
- Serpent נחש ↔ divination נחש: same consonants, separate noun and verb.
- Pitch/coating כפר ↔ atonement כפר: contested root/homonym theory, not a literal synonym for covering the ark.
- Noah's ark ↔ Christ: possible typology with 1 Pet 3:20–21, NOT a claim that the Hebrew specifies a cross-shaped physical boat.

## Notes and documentary layout
Adopt the user's original Genesis ODT only as a STRUCTURAL MODEL, never as unquestioned source data. Print in generous A4 reading type: English 15.5–16pt, Hebrew/Greek 13–14pt, notes 10.5–11pt initially, refine by visual inspection. True page-bottom footnotes: English source-language research, precise quotations and their English literal translations, clearly marked interpretive additions and source citation. No repeated boilerplate about gender after the Bible's first page. Do not insert irrelevant comments about modern scientific duration.

**OLT-018 CURRENT OWNER-APPROVED PLACEMENT (supersedes the earlier optional-only placement):** Genesis 1:1's MAIN English research line is **“In the Beginning [of His Power] God — He shaped the Heavens and the Earth.”** The bracketed phrase is a deliberately supplied THEOLOGICAL supplement in the main text, with a mandatory linked footnote citing **Gen 49:3** (וְרֵאשִׁית אֹונִי, 'and the beginning of my strength') and **Deut 21:17** (רֵאשִׁית אֹנוֹ, 'the beginning of his strength'). In these other passages, 'strength' is the SEPARATE noun אֹון, absent from Gen 1:1. The 'His' possessive is also supplied. This is NOT a dictionary gloss of רֵאשִׁית and does not convert the verse into a final philologically approved edition.

## Five hard release stages
1. **RESEARCH:** multiple independent source-aware waves: edition, morphology, dictionary, linguistic theory, biblical links, literary context.
2. **WORD LOCK:** owner-approved word family and tense conventions plus tracked statuses, readable older English and explicit exceptions.
3. **SOURCE ALIGNMENT:** pin original edition, load actual source text, identify every original token and grammatical form, align to English (or overt supplement) for every verse.
4. **AUTOMATIC TESTS:** fail on wrong owner word, unknown lemma, wrong wayyiqtol tense, omitted source token, neutral it, misplaced under-word link, missing note and unsupported source claim. A fixture PASS does not certify a full chapter.
5. **INDEPENDENT REVIEW:** manually re-check every original word and linked note, run visual A4/ODT/PDF inspection, document sign-off.

A future chapter can be marked PUBLISHED only if all five stages verifiably pass. CI foundation green does not satisfy absent source-data gates. Use ONLY https://github.com/Northsw-spec/OLT for this fresh project. Preserve approvals in its own new decision log; do not import older project files or old misleading success claims.
- **Noah** above **Rest** — Hebrew נֹחַ is associated with נוח (*nuach*, rest). Genesis 5:29 uses the DIFFERENT root נחם (*nacham*, comfort), making a phonetic naming wordplay, not a shared-root dictionary identity. Keep each occurrence source-linked and the owner's lower word exactly **Rest**.
