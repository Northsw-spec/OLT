# DANMEK-033 — Private conditional English corrections for P1 subject/object candidates

**Date:** 2026-11-01. **Scope:** private, English-only *hypotheses*, not proven or approved grammatical corrections.

**Program:** `scripts.danmek_033_private_p1_hypothesis_previews`

## Verified input and purpose

The owner has run DANMEK-032 on the actual privately stored CHES-derived English source, reporting **929** chapters, **23,144** verses, exactly **311** historical English ambiguity verses, **639** unresolved possible noun-subject/verb pairs in P1 and **13** completed local 25-verse batches. The tool reported **15** generated/verified private files, zero approved subject-order changes and no modifications to original CHES, existing readers or the approval manifest.

Those observations are **operator-reported local command outputs**, not the result of ChatGPT opening the real CHES files. The real 639 pairs are not available to public GitHub Actions and are **not** established grammar errors. A noun immediately after a transitive verb may be an **object**, not the subject.

## What DANMEK-033 does

For each of the 639 current English P1 candidate pairs, prepare two **conditional interpretations** in a private offline page:

- **Interpretation A:** *If* the adjacent noun is really the sentence's postposed subject, display one isolated proposed typography change, moving that specific noun before its pronoun–verb expression using the existing DANMEK-027 owner-directed visual style.
- **Interpretation B:** *If* the adjacent noun is an object, or the role remains unresolved, preserve the current guarded DANMEK-028-derived English verse unchanged.

Each candidate is independently illustrated against the complete original displayed English verse; a verse with two candidate pairs gets **two isolated counterfactual previews**, not a forced simultaneous edit. The candidate ordinal, exact chapter SHA-256, verse SHA-256, verb and noun text and existing English role classification are revalidated. Neither interpretation is declared grammatically correct. The program never calls the DANMEK-030 private approval handler, never creates an `approved.json` and **never changes existing readers or original CHES JSON**.

### Privacy and source controls

- First repeat the DANMEK-032 **read-only private source validation**, including the private content-hashed DANMEK-031 priority JSON and historical P1 counts. The follow-on preview is independently calculated from the same local English, without a Hebrew, OSHB or WLC translation comparison.
- Default CLI `--audit-only`: no new files, only aggregated non-sensitive counts, no original English verse text or verse labels in stdout.
- Opt-in `--write-private-previews`: write a separately versioned, immutable snapshot below `~/.olt-private/ches-subject-previews/preview-<hash>/`. With batch size 25, the owner's 311 P1 verses should yield **13 static HTML pages**, one index and one `UNAPPROVED-hypothetical-previews.json` — **15 files** in total.
- Parent and snapshot directories use 0700, files 0600, exact content-match only; existing modified files or symlinks are rejected, no replacement. English and machine-readable previews are **private** and must not be committed to public GitHub or pasted into CI logs.
- Static HTML escapes original English and candidate glosses, blocks scripts/network/forms and marks every illustration **UNAPPROVED**. The JSON schema is intentionally distinct from DANMEK-030's `approved.json` schema: it cannot become an approval through renaming or copying.
- The CLI opt-in `--require-311` rejects an inconsistent historical baseline.

## Local execution after main Actions success

```bash
cd "$HOME/OLT-CHES-tools"
git switch main
git pull --ff-only origin main

PYTHON="$HOME/.local/share/olt-ches-venv/bin/python"
ROOT="$HOME/.olt-private/ches"

"$PYTHON" -m scripts.danmek_033_private_p1_hypothesis_previews \
  --private-root "$ROOT" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --audit-only

"$PYTHON" -m scripts.danmek_033_private_p1_hypothesis_previews \
  --private-root "$ROOT" \
  --confirm-machine-readable-use-permission \
  --require-311 \
  --write-private-previews
```

This produces private **comparison material**, not actual corrections. If any local source/snapshot/report has changed, the review must be revalidated before new output. Never promote conditional previews automatically into a DANMEK-030 approved manifest.

## Following review phase

Use the original English clause context to distinguish subjects from objects, **case by case**. Only a genuinely supported subject-first move may receive an explicit reviewer attestation and pinning via the already implemented DANMEK-030 workflow, generating its own **separate** private reading. The review can also reveal repeated safe patterns deserving future synthetic negative/positive tests. Do not infer syntactic subjecthood from capitalization, proximity, the old 311 flag, or the preview's existence.

English stays intentionally literal with source word choices from CHES; **no new CHES vs Hebrew verification**. No approval of 311 cases or a 66-book English Bible is asserted. **Publication BLOCKED.**
