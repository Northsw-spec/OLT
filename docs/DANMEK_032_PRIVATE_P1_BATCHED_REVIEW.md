# DANMEK-032 — Privately batched review of the 311 historical English ambiguity verses

**Date:** 2026-11-01. **Scope:** PRIVATE English-only reviewer work queue. No new automatic grammatical transformations.

## Evidence from owner-run DANMEK-031

The local private report, as **shown by the owner in terminal output**, scanned **929** chapter files and **23,144** English verses. There are **311 historical ambiguous English verses**, all of which have one or more candidate pairs (**639 total pairs**). There are **0** historical verses with no role candidates, **3,503** additional candidate pairs, and **4,142** candidate pairs overall, across **3,714** review verses. Of all 4,142, **694** were flagged as transitive-object risks and **3,448** are other unresolved English roles. The latter categories are **pair** counts; the priority classes (**311 P1, 0 P2, 574 P3, 2,829 P4**) count **verses**. **0** corrections have been approved.

Those are operator-supplied **technical diagnostics**, not a review of the actual private English by ChatGPT, and not evidence that any particular verse is wrong. The 311 cases remain an active review queue and must not be archived and ignored.

## Why a separate P1 working set?

The owner can review all 311 actual historical verses without sorting through another 3,403 review verses. DANMEK-032 creates **individually readable private static HTML batches** plus one complete P1 reviewer starter document based on the independently rechecked current DANMEK-031 priority report.

By default, there are **25 P1 verses per HTML batch**, so the observed 311-verse archive should produce **13** files of verse batches (12 × 25 plus 11 in the final batch). Each includes the complete locally derived English reading of each historical verse and its possible noun/verb roles; it does not assert grammatical correctness or automatically move words.

The separate `UNAPPROVED-review-starter.json` contains all 639 original P1 candidates with **exact, pinned** DANMEK-030 attestation fields, each set to `english_subject_role_reviewed: false` and an empty `review_note`. The file is **NOT** an active `approved.json`; this program never creates or modifies the latter. Users must distinguish a genuinely postposed subject from a possible object in English context before separately recording an explicit approval. Copying the unreviewed starter alone cannot authorize any correction.

## Source and privacy checks

- The tool recomputes the current private DANMEK-031 aggregate baseline from the locally stored CHES-derived English and requires the corresponding **private** priority report under `~/.olt-private/ches-subject-triage/`. Old valid reports remain untouched; if multiple reports exist, select the uniquely matching source snapshot and counts. Never silently select an out-of-date report.
- Every priority JSON must have a matching **content hash filename**, private 0600 permissions, and no symlinks. Every selected P1 candidate is independently regenerated from the exact recorded English verse and compared to its source-pinned unapproved record.
- Default CLI has no new files or CHES text in stdout. The opt-in writes an immutable private directory `~/.olt-private/ches-subject-batches/p1-<hash>/` containing `index.html`, static `batch-XXX.html` and one unapproved JSON starter. Directory mode 0700, file mode 0600, escaped HTML and restrictive CSP, no scripts/forms/network requests.
- CHES source, older HTML readers and the `ches-subject-review/approved.json` manifest are left untouched. Edited or conflicting generated files are not overwritten.
- **No CHES Hebrew/Aramaic correspondence revalidation, no public CI source content, no owner approvals inferred, no publication rights.** GitHub Actions uses invented names/English only.

## Parrot invocation after merge

```bash
cd "$HOME/OLT-CHES-tools"
git switch main
git pull --ff-only origin main

PYTHON="$HOME/.local/share/olt-ches-venv/bin/python"
ARCHIVE="$HOME/.olt-private/ches"

"$PYTHON" -m scripts.danmek_032_private_p1_batch_review \
  --private-root "$ARCHIVE" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only

"$PYTHON" -m scripts.danmek_032_private_p1_batch_review \
  --private-root "$ARCHIVE" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --write-private-p1-batches
```

The output's `new_private_batch_snapshot_id` is a **non-sensitive identifier**, not a public file. Open the local HTML through its corresponding private directory and use the P1 starter to prepare reviewed DANMEK-030 approvals **only after** individual English role verification. Do not post the private pages to the chat or the GitHub repository.

If the private original source or current priority report is changed, regenerate DANMEK-031's report first; DANMEK-032 fails closed rather than assuming the old report is still valid.

## Next editorial phase

After the private P1 cases are actually reviewed, accepted subject-first adjustments can be processed by DANMEK-030's opt-in, separately versioned private v3 reader. Any safe reusable general patterns should be supported by multiple real cases and synthetic negative regression tests before adding an automatic rule. Until then the 311 and 4,142 remain **unreviewed candidates**, not proven grammar mistakes.

**Publication BLOCKED.**
