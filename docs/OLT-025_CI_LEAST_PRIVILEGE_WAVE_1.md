# OLT-025 — GitHub Actions least-privilege migration, wave 1

Date: 2026-10-30. Status: engineering security checkpoint, not Bible publication.

## Observed branch-protection and CI status

The OLT repository is now PUBLIC. GitHub's branch API reports main.protected=true, but the exposed main.protection.required_status_checks.checks and contexts arrays are empty. The connected app cannot read the complete classic branch-protection policy (403 Resource not accessible by integration), so review enforcement and bypass rules were NOT independently verified. Requiring a named CI check must still be configured in the GitHub web UI.

GitHub-hosted Ubuntu jobs now actually execute, including the 187/187 foundation suite and 8/8 OLT-023 suite before merging OLT-023. Earlier jobs without runner assignment were not reliable code-test evidence; the cause of those older failures remains unproven.

## Measured write-capable workflow inventory

Review of all 22 workflow files on main found **16** that request contents: write and contain a direct git push origin HEAD:main command. These were legacy generation-oriented workflows, created before main was protected.

The first migration is **OLT-015**, with these guarantees:
- permissions: contents: read.
- actions/checkout with persist-credentials: false.
- No workflow commits or git push to main.
- The generator still runs and verifies 434 source tokens, 50 source-tagged wayyiqtol, 97 distinct source lemmas, and publication_status: BLOCKED.
- Generated files must already be tracked and **identically regenerated**; otherwise CI fails and asks for the generated files to be submitted in a normal Pull Request.
- A path-scoped pull_request trigger verifies the change before merge. It is not sufficient alone to enforce protection; GitHub branch settings must require a completed successful check.

## Remaining read/write migration backlog — 15 workflows

1. audit-corpus.yml
2. bdb-nested.yml
3. genesis-02-05.yml
4. genesis-06-10.yml
5. genesis-lexical-proposals.yml
6. genesis-review-dossier.yml
7. import-ot.yml
8. lexicon-candidates.yml
9. olt-011.yml
10. olt-012.yml
11. olt-013.yml
12. olt-014.yml
13. olt-016.yml
14. study-queue.yml
15. verify-xml-crosswalk.yml

These are **known residual direct-write risks**, not silently claimed resolved by OLT-025. They should be migrated in small, tested batches. Avoid regex-based mass edits without checking each workflow's generated file ownership, Git LFS/gzip outputs, and reproducibility. A workflow that regenerates absent/untracked artifacts needs an explicit artifact-management path rather than a blanket git diff assumption.

## Separation of verification and publication

A green CI means tests ran and passed on the checked commit. It does **not** establish independent Hebrew philology, final lexical choices, true page-bottom footnotes, visually checked ODT/PDF or authorization to publish Genesis. All source-policy gates remain BLOCKED.

## Follow-up branch protection action

After the foundation job has demonstrated successful execution on a PR, use GitHub Settings > Branches > the main protection rule > Require status checks to pass before merging, and choose the exact foundation job/check from the recent successful PR. Also require PR-based changes and block force pushes/deletions. Those repository settings are NOT edited by OLT-025.
