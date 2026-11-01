# DANMEK-034 — Two owner-identified English subjects across clauses

**Owner correction:** 2026-11-01  
**Implementation:** `scripts/danmek_034_owner_cross_clause_subjects.py`  
**Target:** a new, private, versioned **v4** reader; existing reader snapshots remain immutable.

## Problem discovered in the real English

The previously implemented DANMEK-027/028 reader can handle some bounded **adjacent** noun–verb arrangements. DANMEK-029/030/031/032/033 can classify adjacent candidates, prepare private review queues and generate hypothetical changes, but these tools do **not** constitute a general dependency parser.

The owner provided two actual corrections showing that a subject may not be an immediately adjacent noun or that a transitive verb may have a following **subject**, not necessarily an object:

**Construction A — one name in two linked clauses.** An introductory pronoun–verb is followed by a subordinate `as·which` clause containing `David - he-sits`, then by `and·he-is-saying David` with an identified prophet recipient. The owner requires the **first** David mention moved before the introductory `and·he-is-becoming` and the **second** before `and·he-is-saying`. The intermediate `he-sits` remains present. No David mention is added or discarded; it is a change of English presentation position, not vocabulary.

**Construction B — the chooser as subject.** In the specifically supplied English context `that in·them` + `he-chose` + `Yahweh` + `to·to-carry-of`, the owner identifies Yahweh as the **agent of choosing**. The new display moves Yahweh before `he-chose` while leaving the other names, participants and words of the sentence untouched.

Neither correction is licensed merely by `he-verb ProperName`. For example, `he-chose AnotherName`, `he-saw Sailors` and `he-loved Rowan` may contain **objects** and must not automatically move. No generic rule that a capitalized English noun is the subject has been added. These two new transformations require the **entire owner-supplied bounded English context**, with matching subject names and clause anchors; they do not claim to fix all distant subjects throughout the corpus.

## Contract: safe independent reading

- The engine begins from the existing guarded **DANMEK-028 v2 English**, generated in memory through `_read_source_text`. It does not change DANMEK-028's implementation, any prior reader HTML, DANMEK-030's individual approval manifests, or the 031/032/033 private review files.
- The new `apply_owner_cross_clause_subjects` function makes only these two tightly constrained, owner-identified English changes. It records rule codes, bounded match positions and number of named subject relocations, and preserves all other text.
- The reader independently scans the locally available private chapters and checks original source SHA/counts, the owner-reading snapshot and historical ambiguity baseline. As elsewhere, the optional `--require-311` enforces the owner's private 311 historic English cases.
- **Audit-only** generates aggregated non-sensitive numbers and writes no files. **Opt-in rendering** creates a distinct immutable `~/.olt-private/ches-cross-clause-reading/snapshot-<id>/` with private 0700 directories and 0600 HTML; previous accepted snapshots are never overwritten.
- No original-language CHES verification, Hebrew/OSHB/WLC comparison or independent grammatical certification is implied. CHES English lexical choices remain authoritative for the source. **No licensed private verse text in public GitHub, tests, CI or CLI stdout.** The test fixtures include invented surrounding English and intentionally altered recipient names, never reproduce entire real source verses.
- The two patterns are **owner-identified examples**, not proof that every occurrence of the same syntax has been independently confirmed. Their aggregate real-corpus incidence remains unknown until the local run; actual output must be inspected for context before wider reuse.
- Public release remains **BLOCKED**.

## Private Parrot execution (after merge and verified GitHub Actions)

```bash
cd "$HOME/OLT-CHES-tools"
git switch main
git pull --ff-only origin main

PYTHON="$HOME/.local/share/olt-ches-venv/bin/python"
ROOT="$HOME/.olt-private/ches"

"$PYTHON" -m scripts.danmek_034_owner_cross_clause_subjects \
  --private-root "$ROOT" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only

"$PYTHON" -m scripts.danmek_034_owner_cross_clause_subjects \
  --private-root "$ROOT" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --render-private-v4
```

The summary includes `owner_cross_clause_rule_counts`, `owner_authorized_individual_subject_moves`, the number of affected verses, and the independently versioned private snapshot ID. Do not conclude that the *whole* English Bible has had its word order fixed. Further unrecognized cross-clause subjects must be added via new, separately tested evidence rather than broad regex inference.

**Publication BLOCKED; old versions and privately stored CHES untouched.**
