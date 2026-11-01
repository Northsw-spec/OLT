# DANMEK-027 — Owner-directed multi-clause postverbal subjects

**Decision date:** 2026-11-01  
**Implementation:** \`scripts.danmek_027_multiclause_subject_first\`  
**Priority:** Supersedes DANMEK-025's "only grammatical defects permit a reorder"
where the owner now expressly requests subject-first editorial word order.
This is **not** permission to make other English wording more idiomatic.

## Owner rule and its linguistic boundary

When a clause has an identifiable **noun subject after the attached
pronoun-verb expression**, DANMEK's newly derived English reading should move
that noun subject before the pronoun-verb. Preserve the original English words,
pronouns, tense, and all other order. Apply the transformation to **every
separately identified pair within a verse**, rather than rejecting the entire
verse because it contains two or more candidate pairs.

The owner demonstrated a construction containing a plural group who are
hearing a report, followed by a clause that a named individual was anointed.
The two intended subjects must both be brought before their verbs. Public
synthetic tests use entirely invented names and words, rather than storing
private CHES material. The test of the same structural shape yields:

- Input (synthetic): \`and·they-are-hearing Sailors that he-was-anointed Rowan\`
- New derived display: \`and Sailors -·they-are-hearing that Rowan - he-was-anointed\`

This respects the owner's requested hyphen/dot typography.

**Essential distinction:** A noun next to a verb is not always its
subject. In \`he-saw Sailors\`, Sailors may be the direct object, so the engine
must **not** automatically make Sailors the subject. It would be false to
call a regex-recognized English noun a verified grammatical subject. For
example, unqualified \`they-are-hearing Sailors\` remains unchanged unless
the context or an approved exception justifies a subject role.

## Latest successor — DANMEK-028 (2026-11-01)

DANMEK-027 v1 remains historical. The current **v2** opt-in private reader
adds bounded article/title/compound subjects and suppresses inheritance
of certain legacy transitive-object reorders in the **new** reading.
The previously approved reader and any v1 snapshot remain untouched.
See [DANMEK-028](DANMEK_028_GUARDED_EXPANDED_SUBJECT_FIRST.md).
This successor does not independently certify all English clauses.

## Implementation and limitations

DANMEK-027 recognizes these bounded patterns initially:

1. The owner-specified *hearing + named plural hearers + subordinate
   anointing report* structure.
2. Explicit English passive predicate patterns such as \`he-was-anointed Rowan\`.
3. A small set of English intransitive predicate forms with an adjacent
   capitalized subject, e.g. \`and·he-came Rowan\`.

Every disjoint recognized match is reordered in the **same verse**. Other
verb-plus-name shapes remain unresolved and unchanged; the tool reports
their number, **not** a count of proven errors. It does not silently alter
objects or guess Hebrew alignment. The recognized patterns are not a
universal subject classifier. Additional English constructions can be
added in tested increments; no claim is made that all postverbal subjects
across the Bible are already detected.

**Legacy caution revealed by CI:** DANMEK-011 already contains previously
owner-approved, typography-based single-candidate reorders. For example,
a bare English `he-saw Sailors` pattern can be transformed by that
earlier layer even though Sailors could be its **object**. This is a
pre-existing limitation of the locked reader, not evidence of a new
DANMEK-027 safe grammatical identification. DANMEK-027 inherits that
older, owner-accepted display as its baseline but adds **no new**
unqualified transitive verb/object movements. Any audit or later editorial
review must evaluate the inherited order independently; passing CI does
not certify the old candidates. No silent mutation of the locked reader.

The owner's CHES-first trust policy remains intact. There is **no**
comparison to independently imported Hebrew or Aramaic editions. This rule
is an English presentation decision, not a claim that Hebrew syntax was
independently validated.

## Safe versioning and use

The owner-verified DANMEK-013/014 English reader source, output files,
snapshots and source CHES JSON remain immutable. DANMEK-027 creates a
**completely separate opt-in private reading**, not a changed version of the
locked reader. Existing English display transforms (owner-approved prior
candidate order, \`faces\`, isolated \`c\` hiding) run first.

After GitHub Actions has verified the implementation, run on the local
Parrot archive:

\`\`\`bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main

"$HOME/.local/share/olt-ches-venv/bin/python" \
  -m scripts.danmek_027_multiclause_subject_first \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only
\`\`\`

This creates **no files** and prints only aggregate, non-sensitive metadata.

For a new private HTML English reading, replace \`--audit-only\` with
\`--build-private-reader\`. Output appears below
\`~/.olt-private/ches-subject-reading/snapshot-<hash>/index.html\`.

All output folders use 0700 permissions and HTML pages use 0600. Existing
files are never overwritten, source HTML is escaped, and CSP disallows
scripts and external network resources. Only aggregate counts are printed
to terminal; no private English or local source path is uploaded to GitHub.

GitHub CI uses invented synthetic English only. It can test matching,
multiple clauses, negative object cases, output immutability and isolation,
but **cannot inspect the owner's private 311 cases**. A local run is needed
to learn how many actual cases match.

**Release and publication remain BLOCKED.**
