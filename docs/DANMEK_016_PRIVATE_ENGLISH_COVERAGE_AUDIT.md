# DANMEK-016 — Private OT English-reading coverage and exception audit

**Purpose:** Quantify the coverage and observable display operations of the
already **owner-visually-verified, LOCKED DANMEK-014 English reader** without
changing that reader, any CHES original file, or any private HTML snapshot.

The user has approved the *reading presentation*. This stage **does not**
reinfer Biblical Hebrew grammar or assert that the full 929 chapters have been
independently verified and translated.

## Audited behaviors and report

A new **read-only, offline, metadata-only** Python module
`scripts.danmek_016_private_english_coverage` reuses CHES-015's existing
privacy and source-schema validation, then independently recomputes **the same
owner-approved display mode**: bounded subject-before-verb candidates,
exact `sur faces` simplification, lowercase c-marker suppression, and
optional pinned YLT edits.

For **each observed source *filename prefix***, the output includes:

- Number of chapters, verses and original English PDF-source fragments observed.
- First and last chapter filename number and chapter-number gaps between 1
  and the highest observed file; this is **not a proof of the true final
  chapter** of that book or of the original index's complete inventory.
- Verses with a single applied *English editorial* word-order candidate.
- Ambiguous verses not reordered, YLT-overlap verses not reordered and verses
  with no detected word-order candidate. **No candidate is not automatically
  an English error**, and English typography does not prove Hebrew syntax.
- The number of exact `sur faces` display simplifications, removed lowercase
  c-letters and entirely hidden c-only source fragments.
- Verses with at least one display/YLT edit versus verses with none. YLT
  noun/tense counters are included only if its optional source is supplied.

All per-prefix counters are checked against the **existing validated reader's
aggregate counters**. A second complete read of the archive compares its
immutable reader snapshot ID and counters to the first, refusing a report
when the source changes during the scan. Counts refer to *observed local
files*, not expected canonical Biblical text. A source prefix is never
asserted to be independently mapped to the corresponding Hebrew book.

The report contains **no verse references, raw Bible words, local file
paths, original CHES or YLT lines, mutable review manifests, HTML or
original-source metadata**. It does not create private directories,
write files, call network APIs, publish results or upload source to GitHub.
All exceptions printed by the CLI use a fixed sanitized message.

## Run on Parrot OS (no manual reader retest required)

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" \
  -m scripts.danmek_016_private_english_coverage \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission
```

The output is aggregate JSON on stdout. No changes are made to the
owner-approved HTML. The returned `reader_snapshot_id` corresponds to
the exact current source and same combination of
`--olt-display-faces --olt-owner-approved-candidates`.

Optional controls:

- `--use-ylt-authority` includes exactly the owner's locally installed,
  pinned YLT overlay and distinguishes conflicts from nonmatching
  grammar patterns. Omit if YLT is not installed.
- `--require-929` makes the audit fail closed unless all **929 source
  chapter JSONs and 39 filename prefixes are present by count**. Even with
  those numbers, original index membership or book-specific chapter
  inventory remains **unverified**.

**Private data policy:** If the user wants help interpreting the report,
only the report's numerical counters and booleans need to be shared,
not any CHES content, source JSON, HTML or original PDF.

## Quality gates

CI tests invented English lines and safe synthetic chapter metadata only,
including: source count and per-prefix aggregation, original and YLT modes,
ambiguous/overlap counts, local chapter gaps, idempotence, zero private
output files, JSON stdout privacy, malformed data failure and continued
publication block. GitHub's test runner cannot access the owner's
private archive; it must not claim all 929 chapters were audited.

**Owner locks:** DANMEK-013 and DANMEK-014 code/HTML presentation remain
unchanged. Further features can evolve in separate private snapshots after
fresh owner visual approval. This quality audit itself neither changes the
translation nor overrides the user's verified presentation.

**Binding release gate:** complete 66-book English Bible **NOT DONE**;
final entire-English-Bible owner approval **NOT DONE**; public
distribution **BLOCKED**.
