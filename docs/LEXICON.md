# OLT-LEX-001 — source-locked lexical ledger

Separate **source lemma identity**, **the user's translation choice**, and **English tense**. Two Hebrew words sharing consonants can have different lemma IDs and meanings; English equivalents must not blur distinct roots inadvertently.

Each canonical lemma record: ID, pointed form, consonants, POS/gender, standard dictionary senses, owner-approved English base and inflections, evidence sources, confidence/status, modern-English intelligibility, homonym links, owner decision history, and source token IDs.

Every actual occurrence: exact Masoretic verse/word ID, source edition SHA, compound segment/lemma, morphology stem/person/gender/number/form, aligned English span, tense classification, bracketed supplements, independently checked state, and reviewer.

Statuses: OWNER_LOCKED, PROVISIONAL, RESEARCH_REQUIRED, REJECTED. A missing original source cannot be “independently reviewed”.

**Compulsory form:** independently identified Hebrew wayyiqtol always English SIMPLE PAST, including the prophetic books. This is editorial English formatting even where reference is a prophetic future. Detect morphological forms in original source, not from the English words “and saw”.

Foundation CI must verify locked entries and deliberately fail corrupted sample variants. Release validation must fail when an independent token source or full aligned manuscript is missing.

## OLT-033 — proper-name and meaningful-title lexicon layer

The Bible-wide names/titles/places policy is `data/policy/olt_name_underword_policy.json`. Its initial source-cited research registry is `lexicon/name_underwords.json`, linked from `lexicon/hebrew.json`. This dedicated name register is **not** an owner-approved expansion of ordinary word-family entries.

Every name-meaning record must identify: exact English display name, original script and source language, name/category/referent, actual source lemma ID(s) where verified, verse/token alignment, owner-requested underword text, evidence type (explicit biblical explanation, lexical etymology, narrative wordplay, traditional toponym or canonical theological interpretation), source citations, competing scholarly analyses, contextual-sense gate, editorial decision state, and disclosure footnote.

Do **not** identify OT and NT occurrences by English spelling alone. Moses and Greek Mōysēs, Hebrew El and the distinct preposition el, place Shiloh and interpretive-title Shiloh, and Siloam must be aligned **individually**. An unpinned original Greek RP2018 source is not a valid invented NT token anchor.

Some owner-proposed meanings (especially Elohim/Mighty Governance and El Shaddai/My Mighty Strength) are NOT plain lexical glosses. Store them truthfully as owner-requested, interpretation-based or unsupported-as-literal research, never a certified original-language homonym or translation. A missing etymology means REVIEW_REQUIRED; do not fabricate English to fill an underword.

Source coverage is **BIBLE-WIDE POLICY, INITIAL 10 CANDIDATE RECORDS**; independent source/lexical approvals and publication still BLOCKED.
- **Noah → Rest:** source association with Hebrew נוח, not the Genesis 5:29 comfort-root נחם. Source occurrence IDs for Genesis 5:29 are pending crosswalk; do not invent them.

## OLT-034 — English master reference versus source and locale lexica

The **English master reference** is defined by lexicon/english_master_manifest.json, referencing existing lexical seeds, OT source research, literal verse proposals and name-underword records. It is NOT yet a complete English OT+NT master lexicon. Original Hebrew/Aramaic/Greek lexical analyses, edition IDs, actual token and lemma references, and optional competing senses are the authoritative INPUTS to every locale.

Separate repos/locale contracts own per-lemma, per-sense and per-occurrence choices for English, Amharic, Japanese, Icelandic, Chinese and further languages. A locale MUST NOT copy the master English string as its translation merely because of English text identity. The source-first package olt_core and six empty locale profiles under locales/ carry this distinction in machine-checked form. OLT-033 name-underwords (e.g. Elohim/Mighty Governance, Noah/Rest) remain explicitly labeled research interpretations or associations; an independently translated target-script underword is needed for another locale. The entire OT+NT lexical approval and publication remain BLOCKED.

## OLT-035 — original-language provenance precedes lexical selection

The source-first lexical ledger starts at immutable **original** token ID, original script, raw morphology, EXACT source lemma component (retaining suffixes e.g. `1254 a` vs `1254 b` and explicit unresolved plus marks), named source edition and hashed import. `olt_core/sources.py` exposes this per-token evidence from the pinned OT book JSON snapshots. Source-tagged Aramaic must use `arc`, Hebrew `hbo`; neither is converted from the English master lexicon.

The imported RP2018 3 John material is Greek **VERSE TEXT only**. It does not have verified Greek original word IDs, lemma or morphology, so no per-word Greek lexicon approval can be imported from it yet. The English master reference and owner name-underword records remain research layers independent of source identity; no new source-linked target word families are approved. Details: `docs/OLT-035_SOURCE_PROVENANCE.md`.

## OLT-035B — full Greek verse-text source is NOT a Greek lexical ledger

Every one of the 27 RP2018 NT books is now present as original Greek verse source text in `data/imported/nt/rp2018/`; the upstream-derived Unicode CSVs contain only `chapter`, `verse`, `text`. **No source-verified Greek token IDs, lemma identities or morphological analyses are provided by these files**; those fields MUST remain empty/unreviewed instead of guessed from tokenized whitespace. Keep the ancillary PA/Acts24 passages separate and record explicit textual decision status. Do not treat this import as the finished English NT master lexicon, any additional English word family approval, an actual Greek word alignment, or a non-English translation. Exact source/byte manifest and reader: `data/engine/olt_035b_rp2018_verse_inventory.json` and `olt_core/nt_corpus.py`.

## OLT-035D — Greek editor-annotated words are not approved lexical senses

The original RP2018 word-sources in data/imported/nt/rp2018/strongs/ now provide 140,149 authentic Beta Code word-form/Strong-number/morphology triplets from the official editor's 27 files. Their 28 optional morphological alternatives must be preserved at the **same word**, and Greek native word token IDs are NOT provided. The OLT-derived position locators must identify the pinned file/verse/ordinal, and original morphology is imported/editor-annotated, not independently reviewed. Strong numbers are not guaranteed lemma FORMS, homonym identities or English meanings. The accented Greek Unicode verse sources have not been aligned word-by-word; source-level verse reference checks have four strictly empty BP5 structural placeholders. English master lexicon and each locale dictionary still need reviewed Greek lexical forms/senses, script equivalences and independent editorial decisions. Biblical-name underwords cannot be auto-matched from English.
