# DANMEK-030 — Exact, privately reviewed English subject-order corrections

**Decision and implementation date:** 2026-11-01  
**Implementation:** `scripts/danmek_030_reviewed_english_subject_order.py`  
**Status:** Private, optional English editorial correction workflow; not a new certified Bible text.

## Why this is the next engineering step

DANMEK-029 identified **candidate** noun subjects and **possible direct objects** using the existing English glosses. Its regex categories are not sufficient to determine that a particular noun really is the subject. The real private CHES archive and the historical **311** cases are not in public GitHub Actions. Therefore an automatic expansion from those 311 *unseen* cases would be conjecture.

DANMEK-030 makes those cases **actionable** through an exact, reviewable correction pipeline, without guessing their grammatical roles.

The user-approved editorial requirement remains: **when an identifiable post-verbal noun is the true subject, place that noun before its associated pronoun–verb expression, including multiple clauses in one verse.** Do not make the English generally more idiomatic. CHES original English word choices remain accepted without re-checking against a separate Hebrew/Aramaic source.

## Three modes

| Mode | What happens |
|---|---|
| `--audit-only` | Scan every private English verse and count unresolved subject-role candidates; terminal shows **aggregated metadata only** and does not write files |
| `--build-private-review` | In `~/.olt-private/ches-subject-review/`, write immutable `queue-<hash>.json` and escaped static `queue-<hash>.html`, listing currently unresolved pairs. The private HTML shows each candidate’s *full verse context*. It also includes historical ambiguous English verses, even when the English parser did not identify a suitable pair |
| `--build-approved-reader` | Read the **private, operator-reviewed** `~/.olt-private/ches-subject-review/approved.json` and apply **only** exact source-pinned entries explicitly set to true, yielding a new, independently versioned private HTML reader under `~/.olt-private/ches-reviewed-subject-reading/snapshot-<hash>/` |

The review JSON is **not automatically approved**. All generated entries have `english_subject_role_reviewed: false` and an empty `review_note`. The operator may copy the generated queue JSON to the fixed **private** `approved.json`, inspect each English clause in context, set only genuinely identified subjects to `true`, and supply a specific note of at least 24 characters. Leaving entries `false` means **NO_CHANGE**, not “grammatically verified.” It is valid to approve multiple distinct subject–verb pairs in the same verse.

Never upload the source, queue, manifest, HTML or any private English verse to public GitHub.

## Data contract and tamper checks

Every optional approval is bound to the exact:

- Verse reference and CHES source chapter’s SHA-256.
- Versioned DANMEK-013/014 owner-reading snapshot ID for the entire imported private archive.
- Full **DANMEK-028 v2 English verse content SHA-256**, not an approximation.
- Candidate ordinal, original English pronoun–verb string and adjacent noun phrase, and its previously recorded 029 English role category.
- Explicit Boolean `english_subject_role_reviewed: true` and substantive `review_note`.

An approved item is applied **only if all these still match**, including its exact English match coordinates. Two entries cannot modify the same candidate. Unapproved candidates remain unchanged. A changed CHES file, a changed accepted-reader snapshot, a different verse, stale candidate ordinal or an ambiguous/altered phrase blocks application rather than guessing.

Manifest decoding rejects duplicate JSON keys, unsafe permissions and symlinks, malformed fields, missing independent reviewer attestations, excessively large files, and duplicated verse+ordinal entries.

**The tool does not independently prove the subject role or authenticate the reviewer’s identity.** The explicitly recorded English review is the editorial authority. English original lexical content remains untouched; the separately derived display moves only the specifically approved adjacent English pair.

## Security / immutability

All original CHES JSON and previously generated or owner-accepted DANMEK-013/014, 027/028 reader HTML and snapshots remain untouched. The new reader lives under a **separate directory and revision hash**. All private output directories require 0700 permissions, private JSON/HTML files 0600; an existing nonidentical file is never overwritten. HTML escapes untrusted English and uses a restrictive CSP without scripts, network or forms. **No private English, verse references, or filesystem paths in CLI stdout or public CI artifacts.**

Only invented English names/verses occur in GitHub CI. CI PASS is technical evidence, not proof that the 311 historical cases have been reviewed or that all English grammar is correct.

## Private execution on Parrot

Use the checked-out repository and local private Python environment:

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main

PYTHON="$HOME/.local/share/olt-ches-venv/bin/python"
ROOT="$HOME/.olt-private/ches"

"$PYTHON" -m scripts.danmek_030_reviewed_english_subject_order \
  --private-root "$ROOT" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only
```

After confirming the metadata, replace `--audit-only` with `--build-private-review` to generate the private queue. To authorize corrections, copy the generated private `queue-<hash>.json` to the same private directory as `approved.json` with secure permissions (0600), review English cases **one by one** and approve only the specific subject roles supported by the English context. Then replace the mode with `--build-approved-reader`. This requires at least one actually approved move; otherwise it fails closed.

**The command above has not run against the owner's actual private CHES corpus in GitHub Actions.** The 311 count is enforced only when `--require-311` is present; an intentionally incomplete test archive may omit the flag.

## Follow-on work

DANMEK-031 should use actual **privacy-preserving aggregated evidence** from the local 029/030 review to prioritize additional bounded *automatic* rules where justified, and write synthetic positive and negative regression tests for each rule. It should not generalize from a small guessed example to the entire corpus. Keep the direct-object guard, unusual but defensible Hebraic English and private owner-approved reader boundary.

**Original Hebrew verification NOT requested. Publication BLOCKED.**
