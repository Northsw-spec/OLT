# CHES-008 — Resumable PRIVATE four-chapter English source batch

**Binding direction:** OLT-SIMPLE-ENGINE-001. Continue the SMALL CHES-informed English source/draft pipeline, not the old thousands-of-hours Hebrew-English lexicon engine or an exhaustive manual original-word crosswalk.

## Source-pinned pilot

The new **scripts/ches_008_private_batch.py** reuses the existing CHES-004 / CHES-007 private English gloss engines. Exactly four original PDF sources are supported, each verified against the exact source SHA-256 and bytes in the [technical source manifest](../data/engine/olt_ches_source_manifest.json).

| Local original input PDF filename | Chapter | Verses |
|---|---|---:|
| ches-gen1.pdf | Genesis 1 | 31 |
| ches-gen2.pdf | Genesis 2 | 25 |
| ches-gen3.pdf | Genesis 3 | 24 |
| ches-ex1.pdf | Exodus 1 | 22 |
| **Total** | **4 chapters** | **102** |

Each chapter yields a mechanical **private English CHES interlinear gloss stream** and independent authentic Hebrew OSHB source IDs. These are NOT final grammatically verified OLT English verses. PDF typography spans are not validated word-to-word translation links. Wayyiqtol English simple-past obligations, owner lexical candidates and all unresolved mappings remain governed by existing source-first controls.

## Local commands (only with machine-readable source-use permission)

Prerequisite: PyMuPDF==1.26.5.

~~~bash
python -m pip install PyMuPDF==1.26.5

# Deliberately build only the first two chapters.
python -m scripts.ches_008_private_batch \
  --pdf-directory /path/to/private-pdfs \
  --output-private-directory .olt-private/ches/batch \
  --confirm-machine-readable-use-permission --limit 2

# Resume with all four: skip verified earlier drafts, build remaining two.
python -m scripts.ches_008_private_batch \
  --pdf-directory /path/to/private-pdfs \
  --output-private-directory .olt-private/ches/batch \
  --confirm-machine-readable-use-permission

# Re-run to verify all four complete, source-preserved private drafts are skipped.
python -m scripts.ches_008_private_batch \
  --pdf-directory /path/to/private-pdfs \
  --output-private-directory .olt-private/ches/batch \
  --confirm-machine-readable-use-permission
~~~

Original PDFs must have exactly the four input filenames shown above. Source inputs are **never downloaded automatically** by this script. The private output directory must reside under the Git-ignored **.olt-private/** directory. Four separate chapter English working files and one **ches-008-state.json** checkpoint are created using atomic writes and 0600 file mode.

The console prints **numbers and safe status codes only**, never CHES English words, original Bible excerpts, private editor comments or paths to source files.

## Error, retry and integrity behavior

- On restart, each previously completed chapter's original PDF is **re-hashed** against its immutable source pin, and the saved private working draft is compared to its exact recorded SHA-256 digest, actual source-word IDs, numeric inventory, rights flags and false owner approval flags. A valid match is skipped.
- If an interruption leaves a private output after the file write but before its checkpoint, the program **rebuilds the chapter from the exact original PDF** and only adopts the orphan if its canonical bytes match. It never quietly adopts changed English.
- Missing, altered or corrupt source PDFs produce chapter failure codes; one failed chapter does not discard successful chapters. A corrected source can be retried simply by rerunning.
- A modified/corrupt saved English output is never silently replaced. The previously saved file is preserved for explicit repair. Incomplete or falsely approving checkpoint data is rejected.
- Processing is bounded to **four pinned chapters**, with optional limit 1–4 to stage progress. No arbitrary chapter downloads, 929-chapter bulk import, dictionary invention or public content export.

These are technical working drafts **unapproved by the owner**, with English grammatical/lexical checks still outstanding. Source rights beyond reported machine-readable use are not presumed.

## Automated GitHub Actions

GitHub Actions processes all four **real pinned original source PDFs** in ephemeral runner storage, intentionally builds two private chapters first, resumes to build the remaining two, and reruns to confirm all four are skipped without changing output. Real licensed text is never written to public Git, CI logs, or downloadable artifacts; only counts/status are output.

Synthetic negative unit tests use invented English source strings and authentic pinned Hebrew source-word IDs to test staged restarts, failure/retry, interruption/orphan recovery, modified private drafts, source PDF corruption, false approval/publication and corrupt state.

## Next: CHES-009

Measure the small batch's failure/skip/recovery rates and gradually expand only to other individually source-pinned OT PDF layouts, with automated source checks and exception-based review. Do not resume the old large lexical engine. The full OT 929-chapter private source import, entire owner-approved 66-book English OLT Bible and publication are **NOT DONE**; the Greek NT needs its own original-language English pipeline.

Keep public README.md exactly zero bytes, correct technical source attribution and the original Git history.
