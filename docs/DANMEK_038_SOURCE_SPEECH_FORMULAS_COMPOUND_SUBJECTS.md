# DANMEK-038 — Systemic English reporting formula and compound subject phrases

**2026-11-01.** Based on direct inspection of the user's PRIVATE original CHES ZIP (929 JSON chapters, 23,144 verse records and 401,460 ordered English fragments). Public GitHub contains **no source CHES English verses**, only invented synthetic tests and aggregate research counts.

## Owner review checkpoint and its limits

The owner explicitly stated **“jag har granskat, och allt är korrekt och bra”** about the work and review outputs presented so far. Treat this as **positive owner feedback on the work reviewed**, and preserve earlier approved reading versions and their presentation conventions. It does **not** independently prove that the complete 23,144-verse English corpus, Greek NT, or all possible future grammar rewrites were individually approved. Do not retroactively alter DANMEK-013/014, 027/028, 030–037 snapshots or overwrite original CHES.

## The next actual source-language structure study

Earlier DANMEK-036/037 inventory identified 493 standalone object-marker structures and 3,869 other finite-verb–nominal positions, with the more restricted DANMEK-037 speech/recipient and intransitive subsets. Those counts are **candidate locations**, not verified bad grammar.

A further **direct source-fragment study** found two repeatable English grammar classes which previously remained unresolved:

1. **278 `thus he-says` / `thus he-said` reporting-formula frames**, including **172** simple subjects and **106** complete compound-subject phrases. These are source English formulas where the name-shaped subject comes immediately after the finite reporting verb and the literal preceding standalone token is `thus`. This count is the raw-frame census of the new detector. The earlier restricted survey counted 274 formula positions without an immediate recipient; **four additional formula shapes overlap earlier recipient-related structures**, so don't count every raw frame as a new edit.
2. **18 additional speech verb + multi-fragment subject + recipient** frames (six title phrases, five kinship/role phrases, three `-of` complements, two compound appellations, two compound appellation-of constructions).

**Total source frames found:** **296 across 294 verses**. A raw source frame is not an applied text edit: the current derived v7 reading may already have rewritten the identical source sequence or a phrase may appear nonuniquely. The new reader reports candidate positions, actual edits, unchanged/already-transformed candidates and conflicts separately.

These are **subject-phrase structures**, not a hardcoded list of biblical individuals. Names are not sufficient to prove their own subjecthood: the source must present a complete bounded nominal phrase and either a complete English reporting formula or an independent recipient marker.

## New implementation

- `scripts.danmek_038_speech_subject_frames` parses the **original ordered CHES English fragments**. It can recognize a finite reporting verb in one source fragment or a finite auxiliary plus one/two lexical continuation fragments.
- Nominal groups may contain a title, a `son-of` / `daughter-of` / other kinship or role complement followed by a named relation, a bounded compound appellation `Elohim`, or a head ending `-of` with a well-defined complement. Incomplete or unsupported nominal groups remain unchanged; no rule moves just the first word of a longer subject.
- The independent **`thus` + `he-says/he-said` + full subject** frame is a separate bounded speaker formula. It never creates a general license to move direct objects after arbitrary speech or transitive predicates.
- For any candidate, the exact original source-fragment string must occur **uniquely** within the previously derived in-memory English reading. A potentially duplicated source sequence, or a changed/overlapping earlier reading, is skipped.
- The following recipient/continuation token is used as a **read-only** context anchor, never consumed in the move. Multiple independent clauses in a verse can be handled without clobbering the next clause.
- Original subject and verb morphology, function words, object markers, punctuation and typography remain preserved except for moving the *complete* subject phrase. The result is subject-first and still intentionally interlinear-like, never idiomatic smoothing.
- `scripts.danmek_037_unmarked_clause_roles.build_private_unmarked_clause_reader` now has a strictly opt-in `include_speech_frames_v8=True` option. Its **default v7 mode and snapshot ID are unchanged**; the optional v8 uses a distinct revision hash and writes only to `~/.olt-private/ches-english-speech-formula-v8/snapshot-<hash>/`. Previously accepted reading folders are never overwritten.
- The v8 module offers `--audit-only` or `--render-private-v8` and optional `--require-311`. The only terminal output is aggregate JSON. The files are local-only, static, HTML-escaped, restricted 0700/0600, with no network/script execution or owner-approval manifest changes.
- Public GitHub Actions sees only invented English fixtures and verifies no source or prior reader mutation, exact match/nonunique rejection, multiple clauses, malformed predicates and infinitival/compound guard cases. **GitHub CI is not a proof that all real English sentences are grammatical.**

## Further work required

Most other unmarked finite–nominal configurations, objects indistinguishable from subjects in the English alone, distant and coordinated subject groups and embedded clauses remain outside this bounded grammar stage. Keep a source-pinned unresolved-review inventory rather than inventing relationships, and continue using the actual private corpus for systematic research instead of person-name-specific patches.

CHES is the authoritative English lexical baseline for this project; no Hebrew/OSHB/WLC cross-validation. No third-party text is uploaded to the public repo or Actions.

**Original CHES, earlier approved readers and explicit `approved.json` manifests unchanged. Publication remains BLOCKED.**
