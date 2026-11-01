# DANMEK-035 — Corpus-wide English clause-structure stage (not a name-specific patch)

**Date:** 2026-11-01  
**Implementation:** `scripts.danmek_035_structural_english_order`  
**Latest owner directive:** The word-order defects are **systemic**. Do **not** respond to each new named example with a new proper-name regex and claim the problem is solved.

## Root cause and target

The older DANMEK-011, 027/028, 029/030 and 034 flow is organized around direct adjacency and small hand-selected patterns. That architecture can fail in many verses where English gloss order follows a Hebrew-style verb–subject–object arrangement, especially when the English verb is split across fragments: `and·he-is- generating`. It can also fail when a subject is not adjacent to its predicate. The owner requires **correct and understandable English grammatical order, but still very literal English**; CHES decides lexical choices and must **not** be re-verified against Hebrew/OSHB/WLC.

**A known, concrete failure structure:** an English **finite subject-pronoun gloss + whitespace-split relationship verb + named agent + explicitly marked `»` object**. The owner states that the agent noun must precede the pronoun–verb while the marked object remains after it. The correction must work for the **structure with any suitable name**, not be hardcoded to Abraham, Isaac or a particular verse.

Example **invented synthetic names**:

| Prior CHES-influenced English display | New independently versioned v5 |
|---|---|
| `and·he-is- generating Rowan » Micah` | `and Rowan ·he-is- generating » Micah` |
| `and·she-is- generating Mira » Talia` | `and Mira ·she-is- generating » Talia` |

The code preserves the user's exact **space, middle dot and hyphen typography** and keeps the marked object, other glosses, and all remaining English unchanged. Multiple disjoint clauses in a verse may be corrected independently.

## Why this is only stage one of a general grammar solution

The presence of a capitalized noun after a transitive verb **never by itself establishes subjecthood**; moving all postverbal names would misclassify direct objects. A `»` glyph is used **only as a bounded English structural cue in this owner-confirmed generating-relation pattern**, not a universal grammatical classifier. For example, `he-is- seeing Rowan » Micah` is still ambiguous and is preserved unchanged. Similarly, `he-is- generating Rowan` without a marked object, and a subject farther away through an unknown clause, are **not** silently corrected.

The new English-only analysis performs a **whole-local-corpus audit of split finite verb forms** and reports separate counts for:

- All detected split finite pronoun–verb glosses.
- Those followed by a proper-name-shaped token.
- Those also containing an immediate marked `»` object.
- The bounded owner-supported generating-relation cases that the new rule can reorder.
- Split verb + name structures still requiring grammatical-role review.
- Split finite glosses without an adjacent proper-name-shaped token.

These values identify **syntax shapes**, not proved errors or complete grammatical subject mapping. This is a first infrastructure step toward a genuinely wider clause-role analysis, rather than falsely claiming a single regex repaired 23,144 private verses.

## Immutable English reading v5

- Start from the existing v2 guarded reader in memory, then retain the two already owner-identified v4 David/Yahweh context corrections, then apply the **generic named-agent / marked-object relationship structure**.
- Scan **all locally available private CHES-derived English chapters and verses**, verify baseline counts and optionally enforce the previously observed 311 historical ambiguities.
- Print aggregate-only CLI JSON by default, without producing files. Optional `--render-private-v5` writes a **separately versioned, immutable** 0700/0600 HTML reading under `~/.olt-private/ches-structural-english-reading/snapshot-<hash>/`. Escaped HTML with no scripts, forms or network; no overwrites.
- The original CHES source, owner-approved previous HTML, private DANMEK-030 approvals, and 031–033 review queues must not be modified.
- Real corpus diagnostic counts and the number of actual generating-pattern corrections **cannot be known from public GitHub Actions**: these are determined only on the operator's private Parrot source. Synthetic English fixtures test arbitrary person names, a split verb, object guard, multiple clauses, earlier v4 coexistence, immutable output, HTML escaping and metadata-only stdout.
- No new publication rights or independent complete 66-book grammatical certification. Publication BLOCKED.

## Parrot commands after all GitHub Actions PASS

```bash
cd "$HOME/OLT-CHES-tools"
git switch main
git pull --ff-only origin main

PYTHON="$HOME/.local/share/olt-ches-venv/bin/python"
ROOT="$HOME/.olt-private/ches"

"$PYTHON" -m scripts.danmek_035_structural_english_order \
  --private-root "$ROOT" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only

"$PYTHON" -m scripts.danmek_035_structural_english_order \
  --private-root "$ROOT" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --render-private-v5
```

The first command does no writing, and the second creates a new immutable private English reading. Share **only the aggregate terminal JSON**, never the private licensed English or HTML. The first real-corpus result will guide the next generalized clause types.

## Next engineering waves

1. Preserve stable token/verb slots: distinguish `subject_pronoun_gloss`, `predicate`, `candidate_nominal`, `marked_object`, `intervening_clause`, and `unresolved` as structured evidence, rather than hardcode personal names. Validate that each proposed relocation is an actual grammatical-subject role, not object/complement.
2. Expand the local corpus-wide **unresolved structure inventory** to cover non-split verbs, compound noun subjects, delayed/distant agents and multiple linked clauses, with negative counterexamples for each candidate rule. Avoid claims of universal English grammatical correctness until tested against real source contexts.
3. Add separately versioned, proven-bounded English transformations and reviewed exceptions without altering the original CHES or old reader snapshots. Any broader auto-rule needs controlled evidence, not just one example.
4. Treat 311 historical P1 verses and 4,142 earlier potential noun-phrase pairs as distinct review inventory categories that require actual grammatical assessment, not merely passage through regex.

**No source-English retranslation, no Hebrew comparison, no automated publication.**
