# DANMEK-031 — Private 311-first English clause-role prioritization

**Implementation date:** 2026-11-01  
**New offline utility:** `scripts/danmek_031_private_english_priority_triage.py`

## Actual private DANMEK-030 baseline (operator-reported)

The owner executed DANMEK-030 on the locally stored private CHES archive, and pasted both the audit-only and write-private-review CLI results. **The assistant did not access this archive itself.** The source text remains private; the following **aggregate, owner-supplied** observations are safe to record:

| Field | Operator-observed value |
|---|---:|
| CHES-derived chapter files scanned | 929 |
| Verses scanned | 23,144 |
| Historical ambiguous English verses | 311 |
| Potential English subject-role review candidates | 4,142 |
| Explicitly approved new English subject moves | 0 |
| Private unapproved review files generated | 2 |
| Original private CHES source changed | false |
| Previous locked readers changed | false |
| Publication | BLOCKED |

Reader baseline identifier: `snapshot-649183af75b671393494`.
Private triage must **recompute and verify** these facts locally; the 311 and 4,142 are **not** grammar-error counts, and we do not claim 929/23,144 is a verified full OT critical text. The old 311 verse flags and new 4,142 *noun-phrase pair* flags represent **different dimensions**. Their real intersection was **not provided** in the initial terminal output.

## Why this step is needed

DANMEK-030 already created a flat queue of 4,142 possible English role decisions. Reviewing all candidates before the historically troublesome 311 verses would be poor prioritization. Yet assuming all 311 correspond to exactly 311 of the 4,142 pairs would be an unsupported inference: some old ambiguous verses may have **no** current candidate, and some may have **more than one**.

DANMEK-031 computes this overlap from the actual local source, **without needing the user to export copyrighted English to GitHub**. Every source verse is checked. All previously ambiguous verses and all current DANMEK-030 unresolved cases are retained.

## Review groups (not grammatical verdicts)

The private report sorts verses into:

1. `P1_HISTORICAL_AMBIGUITY_WITH_ENGLISH_CANDIDATES`: one of the 311 *and* at least one current unresolved noun-phrase candidate.
2. `P2_HISTORICAL_AMBIGUITY_WITHOUT_MATCHED_CANDIDATE`: one of the 311, but no current matched noun phrase. Still requires English review.
3. `P3_OTHER_TRANSITIVE_OBJECT_RISK_CANDIDATES`: other verses with possible direct-object/subject confusion.
4. `P4_OTHER_UNRESOLVED_ENGLISH_CANDIDATES`: other verses with an unresolved role not caught by the transitive hints.

This is a **triage** classifier only: P1 does not prove the verse contains a subject error, and P2 does not certify that the old ambiguity was false. The report measures both candidate **pair counts** and historical **verse counts**, keeping their denominators separate.

## Offline use

After merging and updating the repository locally, obtain counts without creating new files:

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" \
  -m scripts.danmek_031_private_english_priority_triage \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only
```

To generate the ordered, offline private JSON+HTML pair, replace `--audit-only` with `--write-private-priority-report`. The output is a **separate** immutable, content-hashed pair under `~/.olt-private/ches-subject-triage/`, readable only by the user (0700 directory and 0600 files), with escaped English and restrictive CSP. It does not create an `approved.json` or grant any approval to DANMEK-030; it does not alter original CHES or earlier reader snapshots. Only **aggregate numbers** may appear in terminal output, GitHub and Actions logs.

## Follow-on editorial work

Use the private prioritized cases to review actual English subject/object roles. When a noun is genuinely identified as the postposed subject, produce a **specific** DANMEK-030 approval pinned to the exact source chapter, English verse and candidate ordinal, and generate an opt-in independent private v3 view. Do **not** approve every P1 case by category or bypass the attestation requirement.

English remains deliberately literal and early-modern; no general idiomatic rewrite, no revalidation of CHES against Hebrew, no automated full-Bible grammatical certification and **no public release rights**. GitHub Actions validates only synthetic technical test cases, not the private real-corpus classifications.
