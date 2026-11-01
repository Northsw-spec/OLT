# DANMEK-037 — Real private CHES analysis of unmarked English subject clauses

**2026-11-01 — following the owner's direct private corpus upload.**  
**New code:** `scripts.danmek_037_unmarked_clause_roles`.

## Why this stage is necessary

DANMEK-036 directly examined **929 private JSON chapters, 23,144 verses and 401,460 ordered CHES English fragments**, identifying **493** finite + named nominal + standalone `»` marked-object frames. That was a major advance on fixed proper-name regexes but could not explain subject placement in the many clauses **without an immediate standalone object marker**.

A second direct source-level classifier found **3,869 additional non-marked finite + named-nominal positions**, distinct from the 493 earlier marked frames:

| Source-English predicate class | Unmarked possible nominal positions |
|---|---:|
| Speech/report verbs (said, says, saying, speaking etc.) | **1,403** |
| Commonly intransitive verbs (coming, dying, reigning, living etc.) | **440** |
| Other predicates, including uncertain object-bearing verbs | **2,026** |
| **Total** | **3,869** |

The sum of those 3,869 and the 493 marked structures is **4,362** English *candidate positions in this particular source-fragment parser*. **Do not equate** 4,362 to the earlier DANMEK-031 **4,142 role candidates**: those were counted by a different detector applied to a different derived English display, and the overlap is unknown. Neither count is a proven grammatical error count.

## Restricted source-grammatical subclasses

Within the 1,403 speech-shaped unmarked positions, **675** include a following `to` or `to·...` fragment. **13** of those are `to·to-` infinitival constructions, which must NOT be interpreted as an independent recipient. That leaves **662 speech + named nominal + recipient-shaped cues** for the new bounded rule.

Within the 440 intransitive-shaped unmarked positions, **139** have a strong next clause or separate prepositional boundary immediately after the nominal. The remaining **301** are not automatically approved because the English may contain coordinated subjects, titles, longer nominal compounds or ambiguous adjuncts.

Together, **801 raw source candidate positions** form the new, independently identified, better-supported grammatical frames. This figure is BEFORE versioned reader transformations, deduplication, exact-display alignment or individual semantic review, so it is **NOT** the number of new actual fixes.

## DANMEK-037 source-fragment parser and private v7 reader

- Accept the private CHES English source's lexical choices without Hebrew/OSHB/WLC re-verification.
- Recognize a finite English pronoun–verb expression, including one or two split predicate fragments; determine the next name-shaped nominal based on **original ordered source spans**, never merely proximity in a flattened string.
- Apply a new private subject-before-predicate proposal only when the precise next fragment is a bounded speech-recipient cue, excluding `to·to-` infinitive, or a carefully selected intransitive clause boundary.
- **Never** move a name merely because the preceding verb is transitive (e.g. a seeing/taking predicate), or because a speaker/subject is presumed by capitalization. Do not move compound names, indefinite clauses, vocatives, or unmarked object relations without additional grammatical support. Cases with the same source sequence appearing twice are skipped.
- Compose guarded English v2, owner-corrected v4, marked-generative v5 and source-fragment v6 **in memory**, then independently apply v7's exact source-backed nonmarked transformations.
- Create a new optional **immutable private v7 HTML** reading under `~/.olt-private/ches-english-clause-roles/snapshot-<hash>/`, strict 0700/0600, offline static escaped HTML with CSP, no scripts and no overwrites.
- Neither CHES JSON, earlier accepted English readers, nor any active `approved.json` is updated. The default `--audit-only` prints only aggregate diagnostics, without verse words, references or file paths.
- All GitHub regression examples use **invented names, phrases and contexts**; the real copyrighted CHES English remains private and never enters GitHub Actions.

## Further work required

Despite this source-informed step, the full English needs a genuine clause structure and grammatical correctness review. The 2,026 other unmarked nominal positions, 301 less-bounded intransitives, 741 less-bounded speech configurations, multi-fragment subjects, dependent clauses and pronoun resolution all remain outside these new automatic rules. The owner has expressly requested a **systemic English grammar solution**, NOT repeated name-specific code patches. The next wave must use actual source corpus statistics, negative examples, exact alignments and grammatical role evidence before expanding rule scope.

## Parrot operator invocation, when needed

```bash
cd "$HOME/OLT-CHES-tools"
git switch main
git pull --ff-only origin main

PYTHON="$HOME/.local/share/olt-ches-venv/bin/python"
CHES="$HOME/.olt-private/ches"

"$PYTHON" -m scripts.danmek_037_unmarked_clause_roles \
  --private-root "$CHES" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only

"$PYTHON" -m scripts.danmek_037_unmarked_clause_roles \
  --private-root "$CHES" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --render-private-v7
```

**Important:** GitHub Actions validates synthetic behavior but does not prove the number of actual changes on the owner's full private archive. No grammar certification or publication approval is implied. Publication **BLOCKED**.
