# OLT-028 — Source-generation CI migration, final wave

Date: 2026-10-30. Status: source-generation CI security hardening.

## Scope

Originally 16 of the repository's 22 GitHub Actions workflows requested write permission and contained a direct push to the default main branch. Four controlled waves now migrate all 16 from auto-committing jobs to read-only, reproducible provenance checks.

The final five workflows are:

- audit-corpus.yml — original OSHB source morphology and source-lexicon candidate audits
- bdb-nested.yml — loss-preserving, gzip-compressed BDB hierarchical entries
- import-ot.yml — pinned OSHB and HebrewLexicon full Old Testament source import
- lexicon-candidates.yml — whole-OT lexical candidate join
- verify-xml-crosswalk.yml — exact original XML AugIndex/LexicalIndex source-ID crosswalk

## Security and reproducibility contract

Each of the final five has contents: read, does not persist checkout credentials, and has no git commit or git push to main. Each uses the original source generator, its original source-status assertions, and new fail-closed checks for modified or untracked research outputs. The full import checks the data/imported tree, not merely one manifest file. The scoped checks additionally confirm that essential outputs are already version-controlled.

The pinned original-source revisions and existing CC BY 4.0 attribution remain unchanged. The BDB converter already writes gzip data with a fixed mtime=0, enabling deterministic binary comparison. CI never elevates a candidate lexical meaning or external morphology annotation to final academic review.

Changes to code, workflow configuration and generated output files are configured to run through Pull Request checks. A dedicated final test scans all 22 workflows for direct main-push commands and contents-write permissions and validates continued release blocking.

## Evidence required before merge

- GitHub Actions must run and PASS all five final-wave workflows, including pinned upstream clone/import validation.
- The full foundation suite including OLT-028 security regression tests must PASS.
- No generated original word tokens, locked English wording or theological notes may change as a side effect.
- Status remains NOT APPROVED for English lexical research and BLOCKED for Genesis publication.

## External repository setting still to configure

GitHub's main branch is marked protected, but the public branch API currently exposes zero required status checks. The GitHub integration cannot read/update the entire classic branch protection policy (HTTP 403 for full protection endpoint).

To ensure failed CI blocks merges, repository owner must require the consistently available foundation check from a successful Pull Request using GitHub Settings > Branches > main > Require status checks to pass before merging. Also require Pull Requests, and disable force pushes/deletion. This setting is separate from and cannot be substituted by read-only workflow code.

## Remaining non-CI publication work

Independent morphological and lexical signoff for each original word, editorial decisions for the unapproved Genesis 1 families, genuine page-bottom footnotes, visually inspected A4 ODT/PDF and explicit authorization to publish. Source-data CI PASS is not equivalent to a complete Bible translation.
