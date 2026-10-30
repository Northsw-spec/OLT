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
