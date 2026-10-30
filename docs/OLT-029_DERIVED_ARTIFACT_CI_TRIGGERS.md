# OLT-029 — Ensure output-only PRs trigger source audits

Date: 2026-10-30. Engineering integrity gate; NOT philological or publication approval.

## Issue

The OLT-025 and OLT-026 CI migrations switched six source-research generators to read-only regeneration with Git diff verification. Their workflow path filters covered the generator source/configuration, but not the generated research artifacts. A Pull Request altering only such an artifact could therefore skip that specific generator's source audit. The always-running foundation suite does not replace an individual source reproducibility check.

## Scope

Add exact derived-output paths to both push and pull_request triggers for:
- OLT-015: Genesis 1 consolidated alignment JSON and its research-preview Markdown
- OLT-011, OLT-012, OLT-013, OLT-014: each relevant verse-range research JSON
- OLT-016: the 97-lemma editorial research-queue JSON

Include the OLT-029 security test in the PR trigger filter and the foundation unittest suite. Keep all generators, Hebrew source files, original English, doctrinal notes, source evidence and BLOCKED release gates unchanged. Do not add write permission.

## Verification

Before merge, confirm the foundation run and six path-scoped workflow runs have actually executed and succeeded on the same PR commit, with reproducible artifacts and original negative test cases.

## Branch protection remains external

The GitHub branch API still exposes no required status checks for main despite it being protected. The repository owner must enable and select the always-running foundation check under the main protection rule. Workflow code cannot substitute for GitHub's merge enforcement.
