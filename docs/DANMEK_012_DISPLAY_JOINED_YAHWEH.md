# DANMEK-012 — Joined Yahweh subject and isolated lowercase c in the private English view

**Owner-provided defect:** A CHES-derived English line can join the verb and the
name into the same PDF-extracted fragment, then join the name and the
following prepositional phrase. In a separate OLT English view, a narrow
source form like the invented pattern `and·he-shall-cut-offYahwehfrom·Town…`
should begin `And Yahweh — he shall cut off from·Town…`.

The owner also reports a spurious isolated lowercase letter `c`, which
should not appear in OLT's English reading.

## Bounded implementation

With the existing `--olt-owner-approved-candidates` option:

- One additional owner-approved candidate can be detected when an individual
  English source fragment **begins** `and·he-shall-cut-offYahwehfrom·`
  (or `And·` / space in place of the middle dot). Crucially, the name
  directly follows the verb and `from` directly follows the name.
- The **separate HTML view** renders its beginning as
  `And Yahweh — he shall cut off from·...`. The remaining unverified
  extracted English tail stays unmodified. The word `And` is capitalized
  because it begins this displayed sentence; `he` remains lowercase,
  consistent with the permanent DANMEK-007 decision.
- It does **not** move `Yahweh` merely because the words `And` and
  `Yahweh` appear somewhere in one verse. A name could also be an
  **object**. For example, `and·he-shall-seeYahwehfrom·Town` is not
  automatically recognized as a subject-first case. When two candidate
  pairs coexist in the same verse, **neither is moved**.
- If YLT changed the exact affected English source fragment, leave the
  original ordering unchanged in that verse and report an existing
  `olt_owner_candidate_ylt_conflicts_unchanged` count.
- An entire display fragment is suppressed **only if its stripped text
  equals exactly lowercase `c`**. A `C`, `c.`, `city`, or `a c b`
  is not changed. No source JSON, original PDF text, source-faithful
  snapshot, or earlier immutable English snapshot is edited.

This is a **specific English display rule**, not independent Hebrew syntax
verification, a claim of 100% subject–verb coverage, a new Hebrew tense
analysis, or a general spell-check/spacing algorithm. The source's
`he-shall` is preserved semantically as `he shall` in this special case;
the global OLT-TENSE-001 gate must be enforced separately based on actual
Hebrew morphology. All publication remains BLOCKED.

## Use

After merging the tested PR to main on GitHub, update the local checkout and
regenerate the current, opt-in owner-approved private HTML view:

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader \
  --use-ylt-authority \
  --olt-display-faces \
  --olt-owner-approved-candidates
```

Omit `--use-ylt-authority` only if the pinned local YLT text is not present.
The output metadata includes `snapshot_id`, existing owner-approved candidate
and ambiguity counters, plus `olt_isolated_lowercase_c_fragments_hidden`.
The output HTML path is
`~/.olt-private/ches-direct-reader/<snapshot_id>/index.html`.

GitHub Actions tests the joined-name and boundary cases using **invented**
place names and text; real CHES content is never uploaded, committed or emitted
to public CI output. The actual number of corrections in the private OT can
be measured only by the local metadata-only reader audit, not by public CI.
