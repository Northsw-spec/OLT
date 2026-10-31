# DANMEK-009 — Reviewed, source-pinned subject-first OLT English

**Status:** An **opt-in, limited** implementation for individually reviewed English
subject/verb order rules. **This is not automatic restructuring of the OT.**
CHES's original Hebrew-order interlinear is correct as source data and remains
immutable. Only the separate, private OLT HTML reading can change.

## Why no blanket reorder

The 929 local JSON files contain extracted English PDF *green text fragments*,
not certified word-level Hebrew syntactic roles. A rule such as “always swap the
two fragments after `and·he-...`” would silently misidentify subjects,
objects, captions and page extraction artifacts. Our current code therefore
requires a reviewer to verify the individual relationship and to pin the exact
CHES source chapter SHA-256 plus its verse and text; unverifiable verses are
left in faithful order.

## Minimal private reviewed rule file

Create `~/.olt-private/olt-english-order/` with mode `0700` and put
`approved.json` there with mode `0600`. The file stays PRIVATE and must
never be committed to Git. This is **only a synthetic format example** (the
fragment strings are invented, not CHES verse text):

```json
{
  "schema": "DANMEK-009-private-reviewed-order-v1",
  "rules": [
    {
      "reference": "gen.1.1",
      "chapter_json_sha256": "<actual 64-hex SHA256 of private gen.1.json>",
      "mode": "adjacent",
      "source_syntax_reviewed": true,
      "review_note": "Original-language subject and verb checked privately",
      "verb_fragment_index": 1,
      "subject_fragment_index": 2,
      "original_verb": "and·he-shaped",
      "original_subject": "Leader"
    }
  ]
}
```

The above is a *schema illustration*, NOT a deployable reviewed rule. Use
**actual, privately reviewed** source values and file SHA only, never the
example. Indices are **one-based** and the subject must immediately follow
the predicate. Each rule can affect only one verse.

When a verb and an explicit subject occur within **one** source fragment,
use `mode: "inline"`, the same required fields except
`subject_fragment_index`, and add `original_fragment` containing the exact
full original text; `original_verb` followed by optional whitespace and
`original_subject` must occur **exactly once** inside it.

The engine preserves the initial `and·` / `And·` / `and ` / `And `
as a normal separated conjunction, places the explicit subject before the
verbal expression with an em dash, and keeps the existing pronoun casing.
No divine-referent capitalization is added (DANMEK-007).

## Private reader invocation

```bash
cd ~/OLT-CHES-tools
git pull --ff-only origin main

~/.local/share/olt-ches-venv/bin/python -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader \
  --use-ylt-authority \
  --olt-display-faces \
  --olt-subject-first
```

The final option **requires an actual approved private manifest**. Omitting
`--olt-subject-first` retains the old exact snapshot behavior. The reader
refuses outdated source SHA, non-adjacent fragment pairs, ambiguous inline
pairs, YLT edits to the affected span, duplicate rules, missing target verses,
symlinks, unsafe permissions and malformed manifests. It prevalidates **all**
rules before creating any new HTML snapshot. The rules file hash and
DANMEK-009 revision are included in the new immutable snapshot digest.
No English source text is emitted to stdout; only counts
`olt_subject_first_reviewed_rules_applied` and
`olt_subject_first_other_verses_left_unchanged` are shown.

## Proof and remaining work

GitHub Actions uses invented English fragments and checks a separate snapshot,
source bytes unchanged, fragment and SHA mismatch rejection, permission
boundaries, no text leakage and the permanent no-special-capitalization rule.
It **does not** validate any real CHES subject–verb relationship or produce a
fully reordered private OT from the 929 source chapters.

**Next:** use real private source examples, original Hebrew syntax evidence and
local review to produce genuinely pinned entries, then expand measurable
coverage by chapter. Do not represent a green CI run as 929-chapter completion,
original-language alignment certification, owner approval or permission to
publish. `publication_status=BLOCKED`.
