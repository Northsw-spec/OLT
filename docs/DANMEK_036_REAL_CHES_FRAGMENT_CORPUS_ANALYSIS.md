# DANMEK-036 — First direct, private, source-fragment corpus analysis

**Date:** 2026-11-01  
**Implemented:** `scripts.danmek_036_fragment_role_grammar`  
**Priority:** Systemic English subject/predicate/object arrangement, not isolated biblical personal names.

## Direct examination of private source

The owner supplied a **5.1 MB `ches.zip`** containing **929 valid chapter JSON files**, **23,144 verses** and **401,460 ordered English source fragments** (roughly **65.7 MB** uncompressed). The archive was analyzed locally in the assistant's private execution environment; no original CHES verse was committed to public GitHub. The source metadata explicitly marks publication **BLOCKED** and public full-source distribution as disallowed.

Unlike earlier DANMEK stages, these are **results of actual direct analysis** rather than inference from an owner-reported summary. The source CHES English was accepted as authoritative: **no Hebrew/OSHB/WLC content re-verification** was performed.

## Structural findings

- A large share of finite English predicate glosses is distributed across **several CHES source fragments**, for example a grammatical pronoun + tense prefix and a subsequent lexical predicate fragment. A regex applied only to a flattened English string loses meaningful fragment boundaries.
- The archive uses a standalone `»` fragment **7,053 times**, `and·»` **2,197 times**, and other inflected forms such as `»·him` and `»·them`. These are **text-fragment occurrences**, not unique grammatical object roles or proof of subjecthood.
- A bounded source-fragment grammar found **493 plausible post-finite named nominal + standalone `»` object frames**, covering **486 verses** and **24 source book identifiers**:
  - **325** with complete finite verb gloss;
  - **149** with one intervening continuation fragment for a split predicate;
  - **19** with two intervening predicate fragments.
- An earlier loose nominal matcher returned **496** candidates, but **three were first-person verb glosses `I-saw`**, falsely mistaken for proper names. The corrected fragment parser explicitly excludes such tokens.
- **Crucial interpretation:** 493 is a count of structurally supported **candidate locations in raw CHES JSON**, NOT 493 already corrected verses, independently certified subject roles or approved edits. Some source sequences may have been altered by earlier separately versioned display rules. They may not be applied twice.

## Engineering response

The active codebase has historically used adjacent text and some name-specific regexes. DANMEK-036 adds a real **source-fragment parser** that:

1. Traverses each verse's original ordered `source_ches_spans_NOT_OLT_TRANSLATION` list.
2. Recognizes an explicit finite English pronoun–verb token and optional one- or two-fragment lexical continuation (including broken English gerunds).
3. Finds a single bounded proper-name-shaped nominal **followed immediately by a standalone `»` object marker**. It does not interpret a capitalized name alone as a subject.
4. Excludes first-person verb forms like `I-saw`, unknown multiword subjects, prepositional complements, non-standalone object markers, and unresolved clause structures.
5. Runs the existing guarded v2, approved example-bound v4 and bounded v5 display in memory, then only applies a new fragment role reorder **if the complete original source sequence still appears exactly once** in the derived English. Changed, missing or repeated sequences are counted and left alone.
6. In a **separate immutable private v6 English reading**, moves the source nominal before its finite pronoun–verb gloss. The explicit object marker and following object remain exactly in place. The exact owner's `and PERSON ·he-is- generating » OBJECT` typography is retained; other supported finite clauses use the established `and PERSON -·he-verb » OBJECT` pattern. No movement is made on conflicting or uncertain evidence.
7. Makes aggregated audit metrics distinct: raw `source_structural_candidates`, actually applied `new_v6_fragment_moves`, source sequences already changed/not unique, and conflicting spans. No plain CHES English appears on CLI stdout or GitHub.

The script produces a **new versioned opt-in private HTML snapshot** under `~/.olt-private/ches-english-fragment-roles/` using 0700 folders, 0600 write-once files, escaped text and strict CSP. It never modifies original source JSON, v2–v5 or prior approved output, review queues, or `approved.json`. Public GitHub Actions tests invented English examples only.

## What remains unresolved

The 493 raw candidates are only **one well-supported grammatical frame**. The source also contains nonmarked subject cases, subject phrases split over two or more fragments, subordinate clauses, verb forms separated from subjects by adjuncts, coordinated clauses, speech, and direct objects adjacent to transitive verbs.

Even for the 493 frames, a local real-source audit is necessary to find the **actual v6 change count** after the older protected display operations have run. A total corpus-correctness percentage or complete grammatical certification cannot be derived from these counts alone.

**Next engineering work:** systematically inventory all remaining finite + nominal structures by clause slot, object marker and predicate type; add negative proof for each generalized class; continue real-corpus grammatical checks without any blanket capitalize-and-move rule.

## Private operator command (after GitHub CI success)

```bash
cd "$HOME/OLT-CHES-tools"
git switch main
git pull --ff-only origin main

PYTHON="$HOME/.local/share/olt-ches-venv/bin/python"
SOURCE="$HOME/.olt-private/ches"

"$PYTHON" -m scripts.danmek_036_fragment_role_grammar \
  --private-root "$SOURCE" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only

"$PYTHON" -m scripts.danmek_036_fragment_role_grammar \
  --private-root "$SOURCE" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --render-private-v6
```

**No public CHES data, no Hebrew revalidation, no automatic publishing. Publication BLOCKED.**
