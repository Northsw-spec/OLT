# OLT-003 — Every observed lemma receives a candidate record

This pipeline builds a new `data/quality/lexicon_candidates.jsonl` from the full
OSHB OT corpus. Every exact source lemma ID is represented. Source dictionary links
are *candidates*, never silent assumptions of linguistic identity or an approved
English translation.

Strong IDs are matched only under clear numeric equivalence. An augmented
identifier `1254 a` or `1254 b` cannot be merged just because it shares base
number `1254`. AugIndex exact references are maintained separately from BDB;
a direct BDB crosswalk must NOT be pretended completed while source XML relations
remain unresolved.

`genesis_01_owner_lock_anchors.json` connects known owner-lock families
to exact Genesis 1 OSHB tokens where the imported lemma is unambiguous:
`1254 a` → `shape`, the unique discovered exact Genesis 1 `6213`-family lemma → `make`, and `7549` → `firmament`.
This is a preliminary source-to-style anchor, NOT yet a full verse translation,
and the underlying OSHB morphology is not independently audited.

Any source record with no match stays REVIEW_REQUIRED. No fill-by-guessing.

Source matching for asah must examine the actual OSHB extension and fail if 6213 has multiple variants in Genesis 1; the prior assumed bare identifier is not sufficient.
