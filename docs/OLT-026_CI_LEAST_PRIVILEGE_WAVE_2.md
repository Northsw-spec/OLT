# OLT-026 — CI least-privilege migration, wave 2

Date: 2026-10-30. Scope: existing source-derived research generators only.

## Migration

Five additional legacy GitHub Actions workflows are switched from write-capable auto-commit jobs to **read-only verification**:
- OLT-011 Genesis 1:11–15, 69 source tokens
- OLT-012 Genesis 1:16–20, 59 source tokens
- OLT-013 Genesis 1:21–25, 74 source tokens
- OLT-014 Genesis 1:26–31, 117 source tokens
- OLT-016 Genesis 1 lexical editorial queue, 97 lemma identifiers

Each retains its real source validation and negative tests, runs its original deterministic generator, confirms that the expected output is tracked, and fails if generated content differs from the checked-in output. Each is also testable as a scoped Pull Request; none stores GitHub push credentials or attempts to push to main.

## Review gates

- Run GitHub Actions for all five workflows on this PR and verify that the actual jobs and tests PASS.
- Run the full foundation test suite with the new OLT-026 regression file; verify no semantic/token data changed.
- Keep Genesis chapter publication BLOCKED and reject any attempted automatic philological approval.

## Outstanding security migration backlog

Originally 16 of 22 workflows could commit/push directly to main. OLT-025 converted OLT-015; OLT-026 converts five more, reducing the known legacy-write set to **10**:

- audit-corpus.yml
- bdb-nested.yml
- genesis-02-05.yml
- genesis-06-10.yml
- genesis-lexical-proposals.yml
- genesis-review-dossier.yml
- import-ot.yml
- lexicon-candidates.yml
- study-queue.yml
- verify-xml-crosswalk.yml

These remaining 10 jobs have different generated outputs, potentially large import/dictionary artifacts or other provenance requirements. They must be inspected and migrated without pretending a standard diff check covers absent or untracked data.

## Branch protection

GitHub reports main as protected but its visible list of required status checks remains empty as of this checkpoint. The connected GitHub integration cannot modify/retrieve the complete branch protection rule. The owner must require the always-running foundation CI check in GitHub settings. This is distinct from OLT research publication approval.
