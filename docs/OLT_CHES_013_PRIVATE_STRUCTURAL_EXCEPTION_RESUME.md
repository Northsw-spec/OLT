# CHES-013 — Safe continuation after known private PDF verse-layout exceptions

**Scope:** The simplified OLT English source pipeline; private authorized
OT source acquisition on the operator's own computer. This is an optional
extension to the existing resumable **929-source-chapter** importer, not a
general-purpose PDF repairer and not a complete English translation engine.

## The engineering problem

The original CHES private batch importer correctly **fails closed** when a
source chapter's printed verse anchors are unreadable, duplicated, missing,
not in the permitted exact order, or have no green source spans. That prevented
silent verse renumbering, but it also stopped the rest of the private download,
even when hundreds of subsequent chapters could still be processed safely.

The observed example was the original Nehemiah 7 source numbering anomaly:
the owner's local import had saved 419 chapters before the parser stopped.
A source-verified, strictly scoped fix was implemented for that original
numbering pattern in CHES-NEH7. Other genuinely different source layouts may
exist; no future layout or missing verse number is to be guessed.

## New optional behavior (default remains fail-closed)

The importer exposes an explicit option:

```bash
cd ~/OLT-CHES-tools
git pull --ff-only

~/.local/share/olt-ches-venv/bin/python \
  -m scripts.ches_private_batch \
  --import-all \
  --confirm-machine-readable-use-permission \
  --private-root "$HOME/.olt-private/ches" \
  --delay-seconds 1.5 \
  --continue-on-structural-error
```

With the option enabled, **only an explicitly allowlisted original PDF
verse-anchor or missing-green-verse structure error** may be deferred.
The importer skips writing the unsafe chapter, atomically records the exact
original downloaded PDF's SHA-256 and size, original source filename identity,
source index SHA and a fixed diagnostic code, and continues to the next source
chapter with a safe request delay. No original PDF bytes or licensed CHES
English source text are written into the diagnostic ledger or logs.

The private diagnostic ledger is stored separately from corpus JSONs at
`$HOME/.olt-private/ches-013-exceptions/<prefix>.<chapter>.json`, so
`scripts.ches_local_archive_audit` can still scan the chapter-only directory
without mistaking failures for valid chapters. Existing completed chapter
JSON files are skipped by the established resumption mechanism. Rerunning
the importer retries *missing* chapters, even if prior exceptions were recorded.
Once a chapter is actually extracted for the **same original PDF hash**, the
private diagnostic record is marked `RESOLVED_BY_REIMPORT`.

When an allowlisted structural exception remains unresolved, the command
finishes the remaining safe download attempts but exits with **status 2**,
reports **INCOMPLETE_UNRESOLVED_STRUCTURAL_EXCEPTIONS**, and never claims
full 929-chapter completion or translation approval. A full 929-file archive
must still independently pass the offline count/structure audit after all
exceptions have been resolved.

## Errors that MUST still immediately stop the batch

- Network and DNS failures, HTTPS certificate-chain errors, redirects to
  unapproved origins, content oversized/empty, and unexpected original
  source index inventories.
- Invalid PDF signature, malformed PDF, unknown parser exceptions, or
  errors not in the exact error-message allowlist.
- An existing private chapter that fails the pre-existing resume check.
- Changes to the original source PDF hash or source index hash of an already
  recorded unresolved exception; an unsafe or symlinked private ledger file.
- Invalid source chapter identities, public path requests, or too-fast
  request settings.

This is not a silent `try/except: pass` or a license to infer lost verse text.
A small number of absent chapters is **a quality-blocking gap**; each gap
must be researched against the actual original source and resolved before a
complete-source claim is possible.

## Practical boundaries

This milestone **does not** modify the contents of any previously imported
chapter, **does not** reconstruct a missing verse, **does not** translate
new text into English, **does not** apply the owner's Hebrew tense/lexical
rules automatically, and **does not** certify word alignment, source rights,
the English 66-book Bible, or publication.

The default invocation **without** `--continue-on-structural-error` retains
the original stop-on-first-problem behavior. GitHub Actions validates the
new path exclusively with invented synthetic input and negative test cases;
the owner's private 929-chapter corpus stays outside the public repository,
logs and CI artifacts.

**Follow-on CHES-013 tasks:** use metadata-only exception counts to prioritize
specific original PDF layout repairs, and connect the verified private OT
source archive to the existing English draft and OSHB original-language
checking components. Retain the active small English-first engine rather
than returning to the historical full custom lexicon architecture.
