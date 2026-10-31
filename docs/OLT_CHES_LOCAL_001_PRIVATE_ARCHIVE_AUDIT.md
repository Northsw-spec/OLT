# CHES-LOCAL-001 — Offline private archive integrity audit

**Purpose:** Allow the OLT owner to check the CHES JSON files produced by the
existing `scripts/ches_private_batch.py --import-all` command *after the local
download finishes*, without uploading the licensed source text, downloading
anything else, modifying the JSON files, or trusting the contents as a finished
English OLT translation.

## Scope of this small, non-invasive milestone

The audit is completely **offline and read-only**. It inspects only the files
under the operator-supplied `.olt-private/ches` folder. It does not change the
original importer or the currently running download, and it does not execute
inside GitHub Actions against the owner's real private corpus.

For each `<original-source-prefix>.<chapter>.json`, it checks:

- restricted directory permissions and no symlinked paths or chapter files;
- strict JSON parsing (no duplicate keys, NaN, unexpected non-JSON files);
- private/publication rights flags; no invented word alignment or English owner approval;
- exact file name, internal source prefix/chapter, original PDF URL shape and SHA-256
  metadata shape, with one shared original chapter-index SHA-256 across the archive;
- complete ascending, distinct local verse references within each chapter;
- valid green-source fragment records/geometry and exact stored fragment totals;
- contiguous chapter numbering within each observed source prefix;
- aggregate counts of original PDF verse anchors and CHES PDF typography spans.

Even when the count reaches **929 files across 39 source filename-prefix groups**,
the result is only **count-level coverage**. The audit does **not** re-fetch or
re-hash original PDF bytes, verify the exact 929 identities against the live
original index, independently validate all Hebrew/Aramaic verse counts, align a
single Hebrew word to an English gloss, decide grammar, or approve publication.

The returned JSON contains only numeric counts, safety booleans and the fixed
checkpoint name. It contains **no licensed CHES words, private file paths,
authored English drafts or individual PDF passages**. Errors are fixed diagnostic
codes, never the content of an offending source field.

## Run after the private download

From the OLT checkout on the owner's Parrot OS machine:

```bash
python -m scripts.ches_local_archive_audit \
  --private-root "$HOME/.olt-private/ches"
```

To reject a partial download (instead of reporting the partial count):

```bash
python -m scripts.ches_local_archive_audit \
  --private-root "$HOME/.olt-private/ches" \
  --require-929
```

This command uses only the Python standard library and the already-present
OLT source-index parser. It does not require PyMuPDF or network access.
Run it **after** the download has stopped, not concurrently while the importer
might still be writing its temporary `.tmp` chapter files.

A nonzero exit is an integrity/permission or coverage **stop**, not permission
to discard data and not an English translation failure. Preserve the files,
identify the diagnosed condition, and investigate before changing any data.
Do not silently change original hashes, verse numbers or protection flags to
make a failed audit pass.

## Operational boundaries

The currently active lightweight CHES-first English engine remains
`OLT-SIMPLE-ENGINE-001`. This audit is supporting infrastructure, **not**
CHES-013's future bounded real-source chapter expansion and **not** a replacement
for the independent original Hebrew/Aramaic correspondence and editorial gates.

The CHES source corpus remains private; all output is publication **BLOCKED**.
The NT Greek RP2018 path remains independent and English is the sole current
target language. GitHub Actions tests this auditor with **invented synthetic
JSON only**, not the owner's private source text.

If the upstream HTTPS certificate chain is broken, neither this tool nor the
existing import process should bypass certificate validation. This offline
auditor intentionally performs no network operation.
