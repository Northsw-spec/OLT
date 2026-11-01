# DANMEK-028 — Expand safe subjects and isolate inherited unsafe transitive moves

**Date:** 2026-11-01  
**Implementation:** upgraded \`scripts/danmek_027_multiclause_subject_first.py\`,
revision \`DANMEK-028-GUARDED-MULTICLAUSE-SUBJECT-ORDER-v2\`.  
**Scope:** Private CHES-derived English reader only; CHES is authoritative.
No new Hebrew/OSHB/WLC correspondence checks.

## Why this successor exists

DANMEK-027 already moves **multiple** identified noun subjects before their
corresponding pronoun-verb expressions. DANMEK-011, however, was approved
earlier with a typography heuristic that can also move a **transitive
object** in the opposite direction: for instance, invented \`he-saw
Sailors\` might mean that Sailors were seen, **not** that Sailors saw
someone. CI exposed this risk. A raw uppercase-noun regex does not prove
the grammatical role of that noun.

DANMEK-028 deliberately changes **only the new, optional private reading**,
not the older owner-accepted DANMEK-013/014 HTML, and never rewrites original
CHES JSON. The prior reader can still be opened exactly as it was.

The new reader applies a separate **legacy guard**:

1. Re-evaluate the legacy candidate based only on private CHES English.
2. Keep explicitly authorized earlier constructions (including the
   historical \`and·he-shaped\` + \`God\` example) and safely bounded
   passive/intransitive shapes.
3. Do not *inherit* other automatic legacy movements that could treat an
   object as a subject. Preserve their original CHES English instead in the
   **new optional reading**. Count these as
   \`legacy_unverified_subject_moves_not_inherited\`, not proven errors.
4. Search that guarded English for the new multi-clause subject-first
   patterns. Never move an unidentified noun merely because it follows a
   verb.

The old reader is never silently revoked or retroactively edited.
This narrower new output may differ from it for cases requiring review.

## Expansion of bounded grammar patterns

This update supports extra identified subject shapes beyond v1:

- Several postposed subjects in one English verse, including when words
  are stored in different CHES fragments.
- A definite article joined with \`·\` or a space, such as a synthetic
  \`the·Sailors\`.
- Up to three proper-name/title components, such as synthetic
  \`King Rowan\` or \`the·King Rowan\`.
- Selected additional \`is/was/were\` passive forms and intransitive
  finite predicates; the plural hearer/report pattern recognizes \`are\`
  and \`were\` while still requiring an explicit subordinate clause.
- Guard against absorbing capitalized English conjunctions and pronouns
  into a multiword proper name.

**Still excluded:** \`he-returned Rowan\` (returned can be transitive);
\`he-saw Sailors\`, \`he-loved Rowan\`, and unqualified
\`they-are-hearing Sailors\`. These can contain direct objects. A failure
to reorder does **not** certify that no move is needed. The engine is not
a full English parser or a universal subject-identification system.

## Technical and privacy gates

The **revision ID is bumped** so the new optional reader creates a
*different immutable snapshot* under the existing private
\`~/.olt-private/ches-subject-reading/\` parent. Previously generated
v1 and owner-accepted 013/014 snapshots are never overwritten.
No direct writes to CHES source, source repo, original-language corpus,
licensed material on public GitHub or CI artifacts.

The reader's CLI remains the same (see the DANMEK-027 documentation):

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

Use \`--build-private-reader\` in place of \`--audit-only\` to generate the
new HTML view. CLI reports aggregate metadata only. A real corpus run
against the owner's private CHES archive has **not** occurred in GitHub
Actions; it cannot be inferred from synthetic CI passing.

Only invented names and words appear in CI regressions. Tests check
correct double reorders, article/title subjects, clause-boundary
protection, skipping inherited transitive-object risks, keeping explicit
earlier owner orders, no source edits, no overwrite of owner-modified
HTML, secure 0700/0600 permissions and metadata-only stdout.

**Publication BLOCKED.**
