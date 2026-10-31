# DANMEK-014 — Suppress standalone lowercase c markers in OLT English display

**Owner direction (2026-11-01):** The English OLT reading should not show a
standalone lowercase `c` used as an isolated word or apparently useless
source marker. Such letters sometimes occur at the beginning of a verse or
in repeated form. The owner did **not** request changing the original
CHES English/Hebrew source data or the previously approved reader baseline.

## Narrow display-only correction

The existing `hide_isolated_c` operation, enabled **only** in the opt-in
`--olt-owner-approved-candidates` private English reading, now handles
whitespace-separated lowercase c markers **inside a single combined PDF
fragment**, in addition to whole standalone c source fragments:

- An entire fragment `c`, `cc`, ` c c `, etc. is suppressed from
  the derived OLT HTML.
- A fragment beginning `c c and …` displays `and …`.
- A phrase `word c word` displays `word word`, without combining
  or removing the valid surrounding words.
- Each lowercase c letter removed is counted, including duplicates,
  in `olt_standalone_lowercase_c_letters_hidden`.
- The preexisting count `olt_isolated_lowercase_c_fragments_hidden`
  continues to count whole suppressed source fragments only.

The rule deliberately does **not** alter capital `C`, `c.`,
`c,`, `c·`, `c-`, `a·c`, or any embedded letter in
`city`, `clock`, `café`, etc. The matching boundaries must be
the start/end of a source fragment or whitespace; a punctuation-attached
c is not assumed to be an unwanted marker without evidence.

No original CHES private JSON is altered. No text or private local paths
are printed by the CLI, placed in the public repository, or sent to GitHub
Actions. The offline reader generates a **new immutable, versioned private
snapshot**, rather than editing or overwriting the **owner visually verified,
LOCKED DANMEK-013** baseline. The earlier version remains certified **as
presented at the time of that approval**. The owner has also separately
inspected and verified the resulting DANMEK-014 English reading; see the
verification section below.

The original-faithful reader, YLT-only view, `sur faces` processing,
existing sentence order and divine-pronoun capitalization policy are
unchanged. Publication remains **BLOCKED**.

## Subsequently verified and locked by the owner (2026-11-01)

After running the new private English reading on Parrot, the owner confirmed
**“godkänt. verifierat.”** The active DANMEK-014 view is therefore
**OWNER VISUALLY VERIFIED / LOCKED** at protected `main` source-code baseline
`2e56f446b707226c584269c88c50efab37e0ffc2`. This direct human
acceptance supersedes the earlier pre-inspection status sentence above;
it does not identify a public hash for the user's private HTML, certify
Hebrew/Aramaic syntax or approve the final 66-book Bible.
The synthetic DANMEK-015 regression gate safeguards the accepted behavior.
[Canonical owner-verification lock](OLT_PRIVATE_READER_OWNER_VERIFIED_DANMEK014_20261101.md).

## Parrot operation

Update the local `main` checkout after the PR is merged, then generate
an updated private English view with the same existing CLI flags:

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

The CLI prints **only metadata** including a new `snapshot_id`, counts of
suppressed whole fragments and lowercase letters, and chapter count; HTML
is written privately to
`~/.olt-private/ches-direct-reader/<snapshot_id>/index.html`.

If the owner already has a pinned private YLT 1898 source, the optional
`--use-ylt-authority` flag may be added as before. A successful GitHub
Actions run establishes technical integrity of the implemented rule using
**synthetic** text only, not whether every candidate c in the private corpus
is a source extraction artifact.

This is a targeted OLT **presentation cleanup**, not a change to source,
translation, Hebrew morphology or English subject/verb ordering.
