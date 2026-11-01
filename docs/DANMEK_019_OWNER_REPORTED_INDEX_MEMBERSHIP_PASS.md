# DANMEK-019 — Owner-run private OT index membership: verified (2026-11-01)

**Status: OWNER-REPORTED LOCAL TECHNICAL PASS for DANMEK-017.**
This replaces the prior "not yet run on real private data" state.
It does NOT certify all original Hebrew words or the final OLT translation.

## Actual local sequence

The owner first ran DANMEK-016 on Parrot after updating the local checkout,
reporting 929 imported chapter JSON files, 39 source filename prefixes,
23,144 source verse rows and no internal chapter-number gaps.
These counters are independently recorded as *owner-reported numbers* in
[DANMEK-018](DANMEK_018_OWNER_REPORTED_LOCAL_GT_COVERAGE.md).

A separate local search for a saved index HTML with the original import
SHA-256 reported **0 matches**; DANMEK-017 was correctly not run then.

The owner subsequently executed the provided index-recovery script against
the canonical public index URL
`https://www.scripture4all.org/OnlineInterlinear/Hebrew_Index.htm`.
It downloaded the index in the user's Parrot environment, refused URL
redirects, parsed 929 PDF chapter links and 39 filename prefixes, and
computed SHA-256 over the retrieved index bytes. **The SHA-256 matched
the value already recorded in the existing private `gen.1.json`
source record.** The script saved that exact retrieved HTML privately
and ran DANMEK-017 with `--require-index-complete`.

### Owner-reported result

| Check | Parrot result |
| --- | --- |
| Links in freshly retrieved source index | **929** |
| Filename prefixes in source index | **39** |
| SHA-256 equals original registered import-index hash | **True** |
| Imported private source chapters checked | **929** |
| Index chapter IDs missing locally | **0** |
| All locally imported source chapter IDs belong to the supplied index | **True** |
| All local source-index SHA records match the supplied HTML bytes | **True** |
| DANMEK-017 `--require-index-complete` | **PASS** |
| Original private CHES chapter files modified | **No** |
| Publication gate | **BLOCKED** |

The user reported these results by pasting terminal output. No exact
256-bit index digest value or file contents were shared in the chat;
neither the repository nor this document invents or reconstructs it.

This is stronger than 929/39 count-only verification: the **actual
identities of all imported chapter files** were confirmed against the
retrieved source index, with matching recorded index SHA values.

## Limits that remain binding

- This demonstrates consistency with source-index bytes retrieved from
  the canonical public URL and matching a **previously recorded SHA-256**.
  It is not independent proof of every upstream original chapter PDF's
  contents, nor an evaluation of every source word.
- It does **not** independently certify CHES PDF English gloss spans
  against Hebrew/Aramaic original tokens, morphology, translation sense
  or punctuation. The printed-source Nehemiah 7 numbering exception remains.
- It does **not** verify 929 chapters of English translation
  philologically, certify a completed 66-book OLT Bible, or grant
  permission to publish third-party data.
- Local user data (HTML index bytes, original CHES JSON, private reader
  snapshots and full private paths) remains outside public Git.
- DANMEK-013/014 presentation was independently accepted by the owner
  and remains **locked**; no change to the current reader was requested
  or implemented by this metadata-only verification.

### Next development direction

With the **whole-source index membership gate now observed as passing**,
the next material quality work is a **separate, non-mutating English
exception-triage workflow** for 311 locally observed ambiguous English
reorder cases. Prioritize exception classification, original-language
crosswalk evidence where present, and explicit **UNVERIFIED** results
where missing; no blanket automatic reordering. The verified private
reader remains unchanged until a future derived version is separately
tested and visually approved.

**Release rule:** independent English translation complete: **NOT DONE**.
Whole 66-book owner approval: **NOT DONE**. Publication: **BLOCKED**.
