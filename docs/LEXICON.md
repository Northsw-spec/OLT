# OLT-LEX-001 — source-locked lexical ledger

Separate **source lemma identity**, **the user's translation choice**, and **English tense**. Two Hebrew words sharing consonants can have different lemma IDs and meanings; English equivalents must not blur distinct roots inadvertently.

Each canonical lemma record: ID, pointed form, consonants, POS/gender, standard dictionary senses, owner-approved English base and inflections, evidence sources, confidence/status, modern-English intelligibility, homonym links, owner decision history, and source token IDs.

Every actual occurrence: exact Masoretic verse/word ID, source edition SHA, compound segment/lemma, morphology stem/person/gender/number/form, aligned English span, tense classification, bracketed supplements, independently checked state, and reviewer.

Statuses: OWNER_LOCKED, PROVISIONAL, RESEARCH_REQUIRED, REJECTED. A missing original source cannot be “independently reviewed”.

**Compulsory form:** independently identified Hebrew wayyiqtol always English SIMPLE PAST, including the prophetic books. This is editorial English formatting even where reference is a prophetic future. Detect morphological forms in original source, not from the English words “and saw”.

Foundation CI must verify locked entries and deliberately fail corrupted sample variants. Release validation must fail when an independent token source or full aligned manuscript is missing.
