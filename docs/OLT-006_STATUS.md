# OLT-006 — Verified exception triage and Genesis 1 research cards

**Date:** 2026-10-29. **Canonical repo:** https://github.com/Northsw-spec/OLT

**GitHub Actions [OLT-006](https://github.com/Northsw-spec/OLT/actions/runs/40925657427) — PASS**, limited to source identity/data coverage and intentional negative tests. No English translation, lexicon sense or Hebrew morphology has received an independent scholarly signoff from this job.

## Fully generated source-grounded research inputs

| Finding | Actual |
|---|---:|
| MT/OSHB source word tokens in full OT | 306,785 |
| Distinct source lemma keys | 9,519 |
| Keys mapped through original AugIndex → LexicalIndex → BDB/Strong | 9,252 |
| Exact AugIndex lookups still unresolved | 267 |
| Unresolved keys carrying a preserved `+` marker | 256 |
| Other unresolved AugIndex keys | 11 |
| Genesis 1 exact lemma IDs with lexical study cards | 97 |
| Genesis 1 lexical cards without owner-locked English family | **94** |
| Genesis 1 owner-locked English families with source lemma keys | **3** |
| Genesis 1 source word tokens | 434 |
| Source-labelled Genesis 1 wayyiqtol forms | 50 |

## Detailed generated artifacts
- [Unresolved source-ID research cases](../data/quality/unresolved_lexeme_triage.json) — every source key includes its actual occurrence count, up to six real Hebrew word/verse/token samples, and possibly an unapproved numerical-base lookup. A source `+` marker is **never stripped or merged**.
- [Genesis 1 dictionary research cards](../data/quality/genesis_01_dictionary_study_cards.json) — exact 97 source lemmas with occurrence references, the verified XML dictionary identifiers, imported source lexicographic fields and individual review fields for morphology, English readability, wordplay and Christology. No new English choices are called approved.
- [Source crosswalk report](../data/quality/verified_id_crosswalk_report.json) — authoritative counts for the exact lexical XML identifier validation.
- [Main translation conventions](MASTERPROMPT.md) — authoritative owner instructions, unchanged in this checkpoint.

## Critical distinctions
1. **Exact dictionary IDs are not dictionary sense approvals.** The BDB dataset in this project currently imports selected top-level fields; complex nested `<sense>` structures are not yet fully preserved in the research cards. Restoring nested sense evidence should precede a scholarly final lexical decision.
2. **The `+` marker is not authoritatively decoded.** The 256 `+` lemma keys remain separate research cases, even when an otherwise matching bare number exists.
3. **The prefix `waw` is not a numeric root.** Owner-locked conjunction `waw → and` must be analyzed from the original prefix and its morphology, not fabricated as a 98th Genesis lemma.
4. Genesis 1 still requires real English word alignment, source-checking and visible blue under-word links on final pages. None of the 434 source words has been individually signed off as an OLT published translation.

## Next concrete gates
- Fully preserve original BDB nested sense, root and citation hierarchy, without flattening it into invented equivalence.
- Produce a bounded research issue for each non-plus source exception and a separate documented policy for `+` after original-source evidence.
- Source-review Genesis 1's 94 not-yet-locked English lemma families and verify the three owner-lock occurrences against grammar and syntax.
- Generate a fresh fully aligned English/Hebrew Genesis chapter, scholarly footnotes and visually inspected ODT/PDF; publish only after independent review.

**Release status:** BLOCKED. **Source/dictionary research coverage:** PASS for the described automatic checks.
