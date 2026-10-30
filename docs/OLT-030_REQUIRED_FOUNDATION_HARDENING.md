# OLT-030 — Mandatory foundation status check hardening

Date: October 30, 2026. Scope: GitHub Actions CI integrity, NOT translation or philological approval.

## Existing GitHub branch protection: observed facts

The repository is public and the main branch is protected. The GitHub branches API at this checkpoint returns a required status check named **foundation** with app ID **15368**, enforcement level **everyone**.

This is live evidence of a configured required check, **not** independent proof of every other branch protection option (such as required reviews, admin bypass rules, deletions or force-push restrictions). The full protection API still returns HTTP 403 to the connector.

## Modification

The previously required job ID is retained exactly as foundation, to preserve the branch protection rule. The workflow continues to trigger on **every pull_request without paths filters** and on pushes to main.

It now explicitly sets:
- permissions: contents: read, rather than inheriting default GitHub token permissions.
- checkout persist-credentials: false, since no writes are needed.
- actions/checkout@v6 and actions/setup-python@v6. These supported releases target Node 24 and retain Python 3.12 for the test suite.
- A defined 15-minute job timeout.

The same three checks remain mandatory: baseline policy and lexical seeds, all Python unittest regressions, and a release test that is **required to fail** because Genesis is unapproved. A false successful release attempt fails the job.

Source: GitHub official actions/checkout and actions/setup-python README (https://github.com/actions/checkout ; https://github.com/actions/setup-python), and GitHub Node 20 deprecation (https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/).

## Negative regression contract

A new OLT-030 unittest verifies correct workflow structure and actively mutates a clean fixture to reject:
- missing pull_request trigger or altered required job name;
- PR paths filters that permit an absent required check;
- write token permissions or persisted credentials;
- ignore-errors constructs and conditional/skipped checks;
- removal of the release blocker.

This test is part of the same always-running foundation suite and fails on later unsafe workflow edits.

## Verification and limits

Merge ONLY when the **foundation check on this PR** actually executes and passes with the newly selected Node 24 actions, including the new regression cases. Source Hebrew, English owner decisions, research notes and publication status remain unchanged.

GitHub Actions PASS proves behavior of those automated checks; it does not grant independent Hebrew lexical approval or Bible publication.
