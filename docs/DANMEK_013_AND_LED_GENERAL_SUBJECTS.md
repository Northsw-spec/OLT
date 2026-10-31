# DANMEK-013 — And-led subject-first English order for names beyond Yahweh

**Owner direction (2026-11-01):** Extend the owner-approved subject-before-verb
English view beyond the one `Yahweh` exception, using a clause beginning
with `And` as an especially useful detection cue.

## Implemented, bounded English display rules

The existing opt-in `--olt-owner-approved-candidates` mode now also detects
a **single, joined source fragment starting with `and·` or `And·`
(or `and ` / `And `)** followed by a finite English pronoun–verb
gloss, a directly concatenated proper noun or selected `the·<role>`
subject expression, and a directly concatenated prepositional boundary.
The limited verb set covers English **non-direct-object patterns**, such as
`came`, `went`, `returned`, `arose`, `stood`, `rested`,
`lived`, `died`, `spoke`, `said` (including specified inflection
and auxiliary forms). The preposition must be explicitly visible as
`from·`, `to·`, `at·`, `in·`, `upon·`, `before·`,
`after·`, `among·` or `into·`.

Artificial **test-only** examples:

| Source-like English | Separate OLT English output |
| --- | --- |
| `and·he-cameDavidfrom·Town` | `And David — he came from·Town` |
| `and·he-saidMosesto·Council` | `And Moses — he said to·Council` |
| `and·he-returnedthe·kingto·Town` | `And the king — he returned to·Town` |

This enhancement leaves the old bounded, owner-approved
`and·he-shall-cut-offYahwehfrom·…` case intact.

## Why not move every name just because the line starts with And?

`And` only marks a conjunction; it is **not proof** that a noun following
a verb is the grammatical subject. Such a noun can be a direct object
(`And he saw David`), even if a prepositional expression follows.
A blanket global rewrite would silently corrupt the text. Consequently:

- No broad rewrites of `saw`, `met`, `cut off` and other potentially
  object-taking verbs for arbitrary names (the owner-supplied **Yahweh**
  cut-off expression is a separately bounded exception).
- Do not move a name with no confident literal word boundary between the
  subject and a following token in this new detector.
- The additional pattern requires a **clause-initial And** and a bounded
  verb+subject+preposition structure.
- Multiple competing candidates within a verse still cause an
  `AMBIGUOUS` no-change outcome; YLT modifications to the candidate's
  source span cause a `YLT_OVERLAP` no-change outcome.
- No sentence-internal changes via this new matcher. The separately
  existing DANMEK-010 candidate patterns remain unchanged.
- No special capitalization of divine pronouns; ordinary sentence-initial
  `And` is capitalized in the new view.

**Meaning of approval:** The owner has approved proposed *English editorial
word-order changes*. This does NOT amount to machine-proven Hebrew syntax,
original-English word alignment, or a reviewed 929-chapter translation.
All uncertain structures require further evidence before widening automated
changes. The remaining source text, CHES JSON, previous private snapshots,
and original Hebrew-order/source-reader views are untouched.

## Local operation

The same command as DANMEK-011 and DANMEK-012 applies; there are no new
parameters:

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" \
  -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader \
  --olt-display-faces \
  --olt-owner-approved-candidates
```

Add `--use-ylt-authority` only if the pinned, private YLT source is installed.
The source-private output is a distinct versioned
`~/.olt-private/ches-direct-reader/<snapshot_id>/index.html` file.
Only metadata counters are sent to stdout. All new tests use invented
English examples in GitHub Actions; real-source coverage remains unmeasured
until the local program is run.

**Publication rights:** BLOCKED. **Original CHES JSON changes:** none.
