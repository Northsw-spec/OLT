# OLT-027 — CI read-only migration, wave 3

Five additional research workflows are now source-audit jobs rather than direct writers to main.

Migrated:
- genesis-02-05.yml — 45 Genesis 1:2–5 Hebrew source tokens
- genesis-06-10.yml — 63 Genesis 1:6–10 Hebrew source tokens
- genesis-lexical-proposals.yml — seven Genesis 1:1 source tokens and 97-lemma research queue
- genesis-review-dossier.yml — 434-word Genesis 1 original-source dossier
- study-queue.yml — 267 unresolved corpus lemma identifiers and 97 Genesis research cards

The original generators and their source/research validity assertions are retained. CI requires the tracked output files to match regeneration byte-for-byte and rejects missing/untracked target paths. Required GitHub token permission is reduced to contents: read, checkout does not persist credentials, and the workflows no longer push to the default branch.

Both source-input paths and the generated data outputs are now path-scoped pull_request triggers, so a PR changing only derived source data still invokes the corresponding audit. The workflow-specific test is also in the PR trigger list.

The scope is engineering data integrity, NOT independent Hebrew academic signoff or publication. Owner locked Genesis 1:1 and the OLT-022 under-word remain unchanged.

## Remaining five write-capable workflows

- audit-corpus.yml
- bdb-nested.yml
- import-ot.yml
- lexicon-candidates.yml
- verify-xml-crosswalk.yml

These have larger corpus/dictionary outputs and should be migrated only after their generated paths and untracked/ignored-file handling have been reviewed individually.

## Required validation before merge

- GitHub Actions foundation suite must PASS.
- All five migrated workflows must actually run and PASS.
- No source research or publication flag can change to an unsupported positive status.
- GitHub still reports no required status checks in its branch-protection summary; the repository owner must select the always-running foundation check in GitHub Settings.
